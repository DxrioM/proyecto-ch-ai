"""Contrato de datos del Pipeline de Extraccion de Entidades Tecnicas."""

from enum import Enum
from typing import List

from pydantic import BaseModel, Field


class NivelCriticidad(str, Enum):
    """Nivel de criticidad tecnica detectado en el texto."""

    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"


class TechExtraction(BaseModel):
    """Salida estructurada y validada que debe devolver la cadena LCEL."""

    tecnologias: List[str] = Field(
        min_length=1,
        description="Tecnologias, frameworks o herramientas mencionadas en el texto",
    )
    nivel_de_criticidad: NivelCriticidad = Field(
        description="Severidad tecnica del texto: baja, media o alta"
    )
    resumen_tecnico: str = Field(description="Resumen breve del contenido tecnico del texto")
