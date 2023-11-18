from pydantic import BaseModel

# Base user class
class User(BaseModel):
    username: str
    nombre: str
    cedula: str
    ubicacion: str
