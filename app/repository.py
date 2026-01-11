from datetime import date
from sqlalchemy.exc import IntegrityError
import traceback
# Import Product and SessionLocal, support running module directly whether executed as package or script
try:
    from app.models import Product
    from app.db import SessionLocal
except ModuleNotFoundError:
    try:
        from models import Product
        from db import SessionLocal
    except Exception:
        traceback.print_exc()
        raise

# Insertar productos
def insert_product(session, name, descripcion=None, cantidad=0, Marca=None, Fecha_Vencimiento=None):
    if isinstance(Fecha_Vencimiento, str):
        Fecha_Vencimiento = date.fromisoformat(Fecha_Vencimiento)
    prod = Product(
        name=name,
        descripcion=descripcion,
        cantidad=cantidad,
        Marca=Marca,
        Fecha_Vencimiento=Fecha_Vencimiento
    )
    try:
        session.add(prod)
        session.commit()
        session.refresh(prod)
        return prod
    except IntegrityError:
        session.rollback()
        raise
    except Exception:
        session.rollback()
        raise

def insert_product_safe(**kwargs):
    session = SessionLocal()
    try:
        return insert_product(session, **kwargs)
    finally:
        session.close()

# Listar productos
def list_products(session=None):
    """Return all products ordered by id. If session is None a temporary session is used."""
    own = False
    if session is None:
        session = SessionLocal()
        own = True
    try:
        return session.query(Product).order_by(Product.id).all()
    finally:
        if own:
            session.close()

# Editar producto
def update_product(session, product_id, **fields):
    prod = session.get(Product, product_id)
    if not prod:
        return None
    if 'Fecha_Vencimiento' in fields and isinstance(fields['Fecha_Vencimiento'], str):
        fields['Fecha_Vencimiento'] = date.fromisoformat(fields['Fecha_Vencimiento'])
    for k, v in fields.items():
        if hasattr(prod, k):
            setattr(prod, k, v)
    try:
        session.commit()
        session.refresh(prod)
        return prod
    except Exception:
        session.rollback()
        raise

def update_product_safe(product_id, **fields):
    session = SessionLocal()
    try:
        return update_product(session, product_id, **fields)
    finally:
        session.close()

# Eliminar producto
def delete_product(product_id, session=None):
    """Delete product by id. If session is None, opens and closes a session automatically.
    Returns True if deleted, False if not found."""
    own_session = False
    if session is None:
        session = SessionLocal()
        own_session = True
    try:
        prod = session.get(Product, product_id)
        if not prod:
            return False
        session.delete(prod)
        session.commit()
        return True
    except Exception:
        session.rollback()
        raise
    finally:
        if own_session:
            session.close()


def list_products(session=None):
    """Return list of Product objects. Opens/closes session automatically if none provided."""
    own_session = False
    if session is None:
        session = SessionLocal()
        own_session = True
    try:
        return session.query(Product).order_by(Product.id).all()
    finally:
        if own_session:
            session.close()


if __name__ == "__main__":

    print("Repository utilities: insert_product, update_product, delete_product")
    session = SessionLocal()
    try:
        count = session.query(Product).count()
        print(f"Products in DB: {count}")
    except Exception:
        traceback.print_exc()
    finally:
        session.close()