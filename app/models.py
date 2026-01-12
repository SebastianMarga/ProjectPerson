from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Date, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()
class Product(Base):
    __tablename__ = 'productos'
    id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False)
    descripcion = Column(String(100), nullable=True)
    cantidad = Column(Integer, default=0)
    Marca= Column(String(15), nullable=True)
    tipo = Column(String(255), nullable=False, default='')
    Fecha_Vencimiento = Column(Date, nullable=False)
    Fecha_Registro = Column(Date, default=date.today)
