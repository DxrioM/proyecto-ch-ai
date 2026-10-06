"""Fase 7: checkpointer de LangGraph sobre Redis, usando solo comandos basicos.

langgraph-checkpoint-redis necesita RediSearch (comandos FT.*), que Upstash
no soporta. Este checkpointer persiste lo mismo (checkpoints, metadata y
writes pendientes, necesarios para interrupt()/resume) con GET/SET/RPUSH/
LRANGE, que funcionan en cualquier Redis (local, Upstash, Redis Cloud).

Modelo de datos (todo bajo el prefijo `lg:`):
  lg:ckpt:{thread}:{ns}:{checkpoint_id}   -> JSON con checkpoint, metadata y parent
  lg:idx:{thread}:{ns}                    -> lista de checkpoint_ids en orden
  lg:writes:{thread}:{ns}:{cid}:{task}    -> JSON con las writes pendientes
"""

import base64
import json
from typing import Any, AsyncIterator, Optional, Sequence, Tuple

from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.base import (
    BaseCheckpointSaver,
    ChannelVersions,
    Checkpoint,
    CheckpointMetadata,
    CheckpointTuple,
)
from redis.asyncio import Redis

CHECKPOINT_TTL_SECONDS = 7 * 24 * 60 * 60


def _enc(typed: Tuple[str, bytes]) -> list:
    tipo, data = typed
    return [tipo, base64.b64encode(data).decode("ascii")]


def _dec(encoded: list) -> Tuple[str, bytes]:
    tipo, data = encoded
    return tipo, base64.b64decode(data)


class RedisCheckpointSaver(BaseCheckpointSaver):
    def __init__(self, redis_client: Redis, **kwargs: Any):
        super().__init__(**kwargs)
        self._redis = redis_client

    @staticmethod
    def _params(config: RunnableConfig) -> Tuple[str, str, Optional[str]]:
        conf = config["configurable"]
        return conf["thread_id"], conf.get("checkpoint_ns", ""), conf.get("checkpoint_id")

    @staticmethod
    def _ckpt_key(thread: str, ns: str, cid: str) -> str:
        return f"lg:ckpt:{thread}:{ns}:{cid}"

    @staticmethod
    def _idx_key(thread: str, ns: str) -> str:
        return f"lg:idx:{thread}:{ns}"

    @staticmethod
    def _writes_key(thread: str, ns: str, cid: str, task_id: str) -> str:
        return f"lg:writes:{thread}:{ns}:{cid}:{task_id}"

    async def _pending_writes(self, thread: str, ns: str, cid: str) -> list:
        pendientes = []
        async for clave in self._redis.scan_iter(match=self._writes_key(thread, ns, cid, "*")):
            task_id = clave.rsplit(":", 1)[-1]
            raw = await self._redis.get(clave)
            for canal, valor in json.loads(raw):
                pendientes.append((task_id, canal, self.serde.loads_typed(_dec(valor))))
        return pendientes

    async def _tuple_from_key(self, thread: str, ns: str, cid: str) -> Optional[CheckpointTuple]:
        raw = await self._redis.get(self._ckpt_key(thread, ns, cid))
        if raw is None:
            return None
        datos = json.loads(raw)
        checkpoint = self.serde.loads_typed(_dec(datos["checkpoint"]))
        metadata = self.serde.loads_typed(_dec(datos["metadata"]))
        parent = None
        if datos.get("parent"):
            parent = {
                "configurable": {"thread_id": thread, "checkpoint_ns": ns, "checkpoint_id": datos["parent"]}
            }
        return CheckpointTuple(
            config={"configurable": {"thread_id": thread, "checkpoint_ns": ns, "checkpoint_id": cid}},
            checkpoint=checkpoint,
            metadata=metadata,
            parent_config=parent,
            pending_writes=await self._pending_writes(thread, ns, cid),
        )

    async def aget_tuple(self, config: RunnableConfig) -> Optional[CheckpointTuple]:
        thread, ns, cid = self._params(config)
        if cid is None:
            ids = await self._redis.lrange(self._idx_key(thread, ns), -1, -1)
            if not ids:
                return None
            cid = ids[0]
        return await self._tuple_from_key(thread, ns, cid)

    async def aput(
        self,
        config: RunnableConfig,
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
        new_versions: ChannelVersions,
    ) -> RunnableConfig:
        thread, ns, _ = self._params(config)
        cid = checkpoint["id"]
        parent = config["configurable"].get("checkpoint_id")
        datos = {
            "checkpoint": _enc(self.serde.dumps_typed(checkpoint)),
            "metadata": _enc(self.serde.dumps_typed(metadata)),
            "parent": parent,
        }
        await self._redis.set(self._ckpt_key(thread, ns, cid), json.dumps(datos), ex=CHECKPOINT_TTL_SECONDS)
        await self._redis.rpush(self._idx_key(thread, ns), cid)
        return {"configurable": {"thread_id": thread, "checkpoint_ns": ns, "checkpoint_id": cid}}

    async def aput_writes(
        self,
        config: RunnableConfig,
        writes: Sequence[Tuple[str, Any]],
        task_id: str,
        task_path: str = "",
    ) -> None:
        thread, ns, cid = self._params(config)
        serializados = [[canal, _enc(self.serde.dumps_typed(valor))] for canal, valor in writes]
        await self._redis.set(
            self._writes_key(thread, ns, cid, task_id), json.dumps(serializados), ex=CHECKPOINT_TTL_SECONDS
        )

    async def alist(
        self,
        config: Optional[RunnableConfig],
        *,
        filter: Optional[dict] = None,
        before: Optional[RunnableConfig] = None,
        limit: Optional[int] = None,
    ) -> AsyncIterator[CheckpointTuple]:
        if config is None:
            return
        thread, ns, _ = self._params(config)
        ids = await self._redis.lrange(self._idx_key(thread, ns), 0, -1)
        ids.reverse()
        contador = 0
        for cid in ids:
            tupla = await self._tuple_from_key(thread, ns, cid)
            if tupla is None:
                continue
            yield tupla
            contador += 1
            if limit is not None and contador >= limit:
                break

    # La API sincronica no se usa en este proyecto (todo es async).
    def get_tuple(self, config):
        raise NotImplementedError("Usar la version async (aget_tuple)")

    def put(self, config, checkpoint, metadata, new_versions):
        raise NotImplementedError("Usar la version async (aput)")

    def put_writes(self, config, writes, task_id, task_path=""):
        raise NotImplementedError("Usar la version async (aput_writes)")

    def list(self, config, *, filter=None, before=None, limit=None):
        raise NotImplementedError("Usar la version async (alist)")
