from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from decouple import config
import os
from datetime import datetime

DATABASE_URL = config('DATABASE_URL')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Rol(Base):
    __tablename__ = 'roles'
    id_rol = Column(Integer, primary_key=True)
    nombre_rol = Column(String(50))

class Institucion(Base):
    __tablename__ = 'instituciones'
    id_institucion = Column(Integer, primary_key=True, name='id_instituciones')
    nombre = Column(String(150))
    tipo = Column(String(100))
    claves = Column(String(100))
    activo = Column(Boolean)

class Usuario(Base):
    __tablename__ = 'usuarios'
    id_usuario = Column(Integer, primary_key=True)
    nombre = Column(String(100))
    apellido_paterno = Column(String(100))
    apellido_materno = Column(String(100), nullable=True)
    correo = Column(String, unique=True)
    contrasena = Column(String(255))
    curp = Column(String(18), unique=True)
    fecha_registro = Column(DateTime, default=datetime.utcnow)
    ultimo_acceso = Column(DateTime, nullable=True)
    activo = Column(Boolean, default=True)
    rol_id = Column(Integer, ForeignKey('roles.id_rol'))
    institucion_id = Column(Integer, ForeignKey('instituciones.id_instituciones'))

    rol = relationship("Rol")
    institucion = relationship("Institucion")


app = FastAPI(title="CINVESTAVUSICAMM Database Microservice", version="1.0.0")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Bienvenido al microservicio de base de datos de CINVESTAVUSICAMM"}

@app.get("/usuarios")
def get_usuarios():
    db = SessionLocal()
    try:
        usuarios = db.query(Usuario).all()
        return [{"id": u.id_usuario, "nombre": u.nombre, "correo": u.correo, "rol": u.rol.nombre_rol if u.rol else None} for u in usuarios]
    finally:
        db.close()

@app.get("/roles")
def get_roles():
    db = SessionLocal()
    try:
        roles = db.query(Rol).all()
        return [{"id": r.id_rol, "nombre": r.nombre_rol} for r in roles]
    finally:
        db.close()

@app.get("/instituciones")
def get_instituciones():
    db = SessionLocal()
    try:
        instituciones = db.query(Institucion).all()
        return [{"id": i.id_institucion, "nombre": i.nombre, "tipo": i.tipo} for i in instituciones]
    finally:
        db.close()

@app.get("/usuario/{usuario_id}")
def get_usuario(usuario_id: int):
    db = SessionLocal()
    try:
        usuario = db.query(Usuario).filter(Usuario.id_usuario == usuario_id).first()
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return {
            "id": usuario.id_usuario,
            "nombre": usuario.nombre,
            "apellido_paterno": usuario.apellido_paterno,
            "correo": usuario.correo,
            "rol": usuario.rol.nombre_rol if usuario.rol else None,
            "institucion": usuario.institucion.nombre if usuario.institucion else None
        }
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)