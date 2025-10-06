from typing import Dict, List, Optional
from .models import User


class UserCRUD:
    """Clase para operaciones CRUD de usuarios usando almacenamiento en memoria."""
    
    def __init__(self):
        self._users: Dict[str, User] = {}
    
    def create(self, name: str, email: str, age: int) -> User:
        """Crea un nuevo usuario."""
        user = User.create(name, email, age)
        
        # Verificar que el email no esté en uso
        for existing_user in self._users.values():
            if existing_user.email == user.email:
                raise ValueError(f"El email {user.email} ya está en uso")
        
        self._users[user.id] = user
        return user
    
    def get_by_id(self, user_id: str) -> Optional[User]:
        """Obtiene un usuario por su ID."""
        return self._users.get(user_id)
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Obtiene un usuario por su email."""
        email = email.strip().lower()
        for user in self._users.values():
            if user.email == email:
                return user
        return None
    
    def get_all(self) -> List[User]:
        """Obtiene todos los usuarios."""
        return list(self._users.values())
    
    def update(self, user_id: str, **kwargs) -> Optional[User]:
        """Actualiza un usuario existente."""
        user = self._users.get(user_id)
        if not user:
            return None
        
        # Si se está actualizando el email, verificar que no esté en uso
        if "email" in kwargs:
            new_email = kwargs["email"].strip().lower()
            for uid, existing_user in self._users.items():
                if uid != user_id and existing_user.email == new_email:
                    raise ValueError(f"El email {new_email} ya está en uso")
        
        updated_user = user.update(**kwargs)
        self._users[user_id] = updated_user
        return updated_user
    
    def delete(self, user_id: str) -> bool:
        """Elimina un usuario por su ID."""
        if user_id in self._users:
            del self._users[user_id]
            return True
        return False
    
    def count(self) -> int:
        """Retorna el número total de usuarios."""
        return len(self._users)
    
    def clear(self) -> None:
        """Elimina todos los usuarios."""
        self._users.clear()
    
    def exists(self, user_id: str) -> bool:
        """Verifica si un usuario existe."""
        return user_id in self._users