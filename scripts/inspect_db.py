from app.db import engine
from sqlalchemy import inspect
insp = inspect(engine)
cols = insp.get_columns('productos')
for c in cols:
    print(c['name'], c['type'], 'nullable=' + str(c['nullable']), 'default=' + str(c.get('default')))
