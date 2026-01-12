"""Repository: funciones de acceso a datos (CRUD) sobre `Product`.

Esta capa encapsula sesiones y transacciones. Use las funciones `*_safe` cuando quiera que
el wrapper maneje la apertura/cierre de sesiones automáticamente.
"""

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
def insert_product(session, name, tipo, descripcion=None, cantidad=0, Marca=None, Fecha_Vencimiento=None, precio=0.0):
    """Insert a product. `tipo` is required. `precio` is a numeric value (default 0.0)."""
    # Validación sencilla del campo 'tipo'
    if tipo is None or str(tipo).strip() == "":
        raise ValueError("El campo 'tipo' es obligatorio")
    # Aceptamos fechas en formato ISO (str) o `datetime.date` y las normalizamos
    if isinstance(Fecha_Vencimiento, str):
        Fecha_Vencimiento = date.fromisoformat(Fecha_Vencimiento)
    # normalizar precio
    try:
        precio = float(precio)
    except Exception:
        precio = 0.0
    # Nota: la llamada a session.commit() sigue el patrón explícito; en caso de error se realiza rollback
    prod = Product(
        name=name,
        tipo=tipo,
        descripcion=descripcion,
        cantidad=cantidad,
        Marca=Marca,
        precio=precio,
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
    """Update a product by id.

    `fields` can include any attribute present on the model. Only attributes that
    exist on the mapped `Product` are set; this prevents accidental creation of new attributes.
    """
    prod = session.get(Product, product_id)
    if not prod:
        return None
    if 'Fecha_Vencimiento' in fields and isinstance(fields['Fecha_Vencimiento'], str):
        fields['Fecha_Vencimiento'] = date.fromisoformat(fields['Fecha_Vencimiento'])
    if 'precio' in fields:
        try:
            fields['precio'] = float(fields['precio'])
        except Exception:
            fields['precio'] = prod.precio or 0.0
    for k, v in fields.items():
        # Solo asignar si existe el atributo en el modelo
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