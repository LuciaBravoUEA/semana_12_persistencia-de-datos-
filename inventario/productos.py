from app import db, Producto

def agregar_producto(nombre, precio, cantidad):
    nuevo = Producto(nombre=nombre, precio=precio, cantidad=cantidad)
    db.session.add(nuevo)
    db.session.commit()