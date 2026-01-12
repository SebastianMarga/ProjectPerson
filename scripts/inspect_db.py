"""Pequeña utilidad para inspeccionar la estructura de la tabla `productos`.

Útil en desarrollo para comprobar tipos, nullability y defaults. No ejecutar en producción
sin entender el entorno ya que conecta a la base configurada por `DATABASE_URL`.
"""

from app.db import engine
from sqlalchemy import inspect
insp = inspect(engine)
cols = insp.get_columns('productos')
for c in cols:
    print(c['name'], c['type'], 'nullable=' + str(c['nullable']), 'default=' + str(c.get('default')))
