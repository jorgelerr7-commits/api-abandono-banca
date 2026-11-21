from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ClienteInput(BaseModel):
    model_config = ConfigDict(json_schema_extra={"example": {
        "id_cliente": "CLI-8492", "edad": 42, "ingresos_anuales": 52000,
        "saldo_cuenta": 18500, "nivel_estudios": "Grado", "tipo_cuenta": "Nomina",
        "nivel_satisfaccion": "Medio", "num_productos": 3, "tiene_tarjeta": True,
        "canal_preferido": "App Movil", "antiguedad_meses": 36,
    }})
    id_cliente: str = Field(..., min_length=1, max_length=50, description="Identificador del cliente")
    edad: float | None = Field(default=None, ge=0, le=120)
    ingresos_anuales: float | None = Field(default=None, ge=0)
    saldo_cuenta: float | None = None
    nivel_estudios: Literal["Primaria", "Secundaria", "Grado", "Master", "Doctorado"] | None = None
    tipo_cuenta: Literal["Ahorro", "Corriente", "Inversion", "Nomina"] | None = None
    nivel_satisfaccion: Literal["Muy Bajo", "Bajo", "Medio", "Alto", "Muy Alto"] | None = None
    num_productos: int | None = Field(default=None, ge=0)
    tiene_tarjeta: bool | None = None
    canal_preferido: Literal["App Movil", "Cajero Antiguo", "Oficina", "Telefono", "Web"] | None = None
    antiguedad_meses: float | None = Field(default=None, ge=0)


class PrediccionOutput(BaseModel):
    id_cliente: str
    abandono: int = Field(..., ge=0, le=1)
    probabilidad_abandono: float = Field(..., ge=0.0, le=1.0)
    nivel_riesgo: Literal["Bajo", "Medio", "Alto"]
    accion_recomendada: str
