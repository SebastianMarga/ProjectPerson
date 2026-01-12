"""Modelos de datos (SQLAlchemy).

Contiene la clase Product que refleja la tabla `productos`.
Notas:
- `tipo` es NOT NULL y debe contener una categoría válida (capturada por la UI).
- `Fecha_Vencimiento` es obligatoria (Date), `Fecha_Registro` usa `date.today` por defecto.
- Cambios de esquema deben manejarse mediante Alembic para mantener historial de migraciones.
"""

from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Date, DateTime, Float
from sqlalchemy.orm import declarative_base

Base = declarative_base()
class Product(Base):
    __tablename__ = 'productos'
    id = Column(Integer, primary_key=True)
    # Nombre corto, requerido
    name = Column(String(30), nullable=False)
    descripcion = Column(String(100), nullable=True)
    cantidad = Column(Integer, default=0)
    Marca= Column(String(15), nullable=True)
    # `tipo` es requerido; la UI debe garantizar su presencia
    tipo = Column(String(255), nullable=False, default='')
    # Precio en unidades monetarias (float)
    precio = Column(Float, default=0.0)
    # Fecha de vencimiento (obligatoria)
    Fecha_Vencimiento = Column(Date, nullable=False)
    # Fecha de registro (solo fecha, sin hora)
    Fecha_Registro = Column(Date, default=date.today)
