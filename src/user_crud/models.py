from dataclasses import dataclass
from typing import Optional, Dict, Any
import uuid
from datetime import datetime


@dataclass
class User:
    """Modelo de usuario con validaciones básicas."""
    id: str
    name: str
    email: str
    age: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Validaciones después de la inicialización."""
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("El nombre no puede estar vacío")
        
        if not self.email or "@" not in self.email:
            raise ValueError("Email inválido")
        
        if self.age < 0 or self.age > 150:
            raise ValueError("La edad debe estar entre 0 y 150 años")
    
    @classmethod
    def create(cls, name: str, email: str, age: int) -> "User":
        """Factory method para crear un nuevo usuario."""
        return cls(
            id=str(uuid.uuid4()),
            name=name.strip(),
            email=email.strip().lower(),
            age=age,
            created_at=datetime.now()
        )
    
    def update(self, **kwargs) -> "User":
        """Actualiza el usuario con nuevos valores."""
        allowed_fields = {"name", "email", "age"}
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if updates:
            updates["updated_at"] = datetime.now()
            # Crear una nueva instancia con los valores actualizados
            new_data = {
                "id": self.id,
                "name": updates.get("name", self.name),
                "email": updates.get("email", self.email),
                "age": updates.get("age", self.age),
                "created_at": self.created_at,
                "updated_at": updates["updated_at"]
            }
            return User(**new_data)
        
        return self
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el usuario a diccionario."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "age": self.age,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }