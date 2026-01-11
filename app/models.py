from datetime import datetime
from sqlalchemy import Column, Integer, String, Date, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()
class Product(Base):
    __tablename__ = 'Productos'
    id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False)
    descripcion = Column(String(100), nullable=True)
    cantidad = Column(Integer, default=0)
    Marca= Column(String(15), nullable=True)
    Fecha_Vencimiento = Column(Date, nullable=False)
    Fecha_Registro = Column(DateTime, default=datetime.utcnow)
