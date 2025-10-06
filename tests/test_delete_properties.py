import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from hypothesis import given, strategies as st, assume
from user_crud.models import User
from user_crud.crud import UserCRUD


@given(
    users_data=st.lists(
        st.tuples(
            st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
            st.emails(),
            st.integers(min_value=0, max_value=150)
        ),
        min_size=1,
        max_size=10,
        unique_by=lambda x: x[1]  # Emails únicos
    )
)
def test_delete_user_properties(users_data):
    """
    Prueba basada en propiedades para DELETE:
    - Un usuario eliminado no debe ser recuperable
    - delete() debe retornar True para usuarios existentes
    - delete() debe retornar False para usuarios inexistentes
    - El contador debe decrementar correctamente
    """
    crud = UserCRUD()
    created_users = []
    
    # Crear usuarios
    for name, email, age in users_data:
        user = crud.create(name, email, age)
        created_users.append(user)
    
    original_count = crud.count()
    user_to_delete = created_users[0]
    
    # Eliminar un usuario
    result = crud.delete(user_to_delete.id)
    
    # Propiedades que siempre deben cumplirse
    assert result is True
    assert crud.count() == original_count - 1
    assert crud.exists(user_to_delete.id) is False
    assert crud.get_by_id(user_to_delete.id) is None
    assert crud.get_by_email(user_to_delete.email) is None
    
    # Los otros usuarios deben seguir existiendo
    for user in created_users[1:]:
        assert crud.exists(user.id) is True
        assert crud.get_by_id(user.id) is not None
        assert crud.get_by_email(user.email) is not None


@given(
    users_data=st.lists(
        st.tuples(
            st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
            st.emails(),
            st.integers(min_value=0, max_value=150)
        ),
        min_size=2,
        max_size=10,
        unique_by=lambda x: x[1]  # Emails únicos
    )
)
def test_delete_multiple_users_properties(users_data):
    """
    Prueba basada en propiedades para DELETE múltiple:
    - Eliminar múltiples usuarios debe funcionar correctamente
    - El contador debe decrementar apropiadamente
    - Los usuarios restantes deben seguir siendo válidos
    """
    assume(len(users_data) >= 2)
    
    crud = UserCRUD()
    created_users = []
    
    # Crear usuarios
    for name, email, age in users_data:
        user = crud.create(name, email, age)
        created_users.append(user)
    
    original_count = crud.count()
    users_to_delete = created_users[:len(created_users)//2]  # Eliminar la mitad
    users_to_keep = created_users[len(created_users)//2:]
    
    # Eliminar usuarios
    for user in users_to_delete:
        result = crud.delete(user.id)
        assert result is True
    
    # Propiedades que siempre deben cumplirse
    expected_count = original_count - len(users_to_delete)
    assert crud.count() == expected_count
    
    # Los usuarios eliminados no deben existir
    for user in users_to_delete:
        assert crud.exists(user.id) is False
        assert crud.get_by_id(user.id) is None
        assert crud.get_by_email(user.email) is None
    
    # Los usuarios no eliminados deben seguir existiendo
    for user in users_to_keep:
        assert crud.exists(user.id) is True
        assert crud.get_by_id(user.id) is not None
        assert crud.get_by_email(user.email) is not None


def test_delete_nonexistent_user_properties():
    """
    Prueba basada en propiedades para DELETE de usuario inexistente:
    - Eliminar un usuario inexistente debe retornar False
    - No debe afectar el estado del CRUD
    """
    crud = UserCRUD()
    
    # Crear algunos usuarios para verificar que no se afectan
    user1 = crud.create("Test User 1", "test1@example.com", 25)
    user2 = crud.create("Test User 2", "test2@example.com", 30)
    
    original_count = crud.count()
    
    # Intentar eliminar usuario inexistente
    result = crud.delete("fake-id-12345")
    
    # Propiedades que siempre deben cumplirse
    assert result is False
    assert crud.count() == original_count
    
    # Los usuarios existentes no deben verse afectados
    assert crud.exists(user1.id) is True
    assert crud.exists(user2.id) is True
    assert crud.get_by_id(user1.id) == user1
    assert crud.get_by_id(user2.id) == user2


@given(
    users_data=st.lists(
        st.tuples(
            st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
            st.emails(),
            st.integers(min_value=0, max_value=150)
        ),
        min_size=1,
        max_size=10,
        unique_by=lambda x: x[1]  # Emails únicos
    )
)
def test_delete_all_users_properties(users_data):
    """
    Prueba basada en propiedades para DELETE todos los usuarios:
    - Eliminar todos los usuarios debe dejar el CRUD vacío
    - Después de eliminar todos, get_all() debe retornar lista vacía
    """
    crud = UserCRUD()
    created_users = []
    
    # Crear usuarios
    for name, email, age in users_data:
        user = crud.create(name, email, age)
        created_users.append(user)
    
    # Eliminar todos los usuarios
    for user in created_users:
        result = crud.delete(user.id)
        assert result is True
    
    # Propiedades que siempre deben cumplirse después de eliminar todos
    assert crud.count() == 0
    assert crud.get_all() == []
    
    # Ningún usuario debe existir
    for user in created_users:
        assert crud.exists(user.id) is False
        assert crud.get_by_id(user.id) is None
        assert crud.get_by_email(user.email) is None


@given(
    name=st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
    email=st.emails(),
    age=st.integers(min_value=0, max_value=150)
)
def test_delete_and_recreate_properties(name, email, age):
    """
    Prueba basada en propiedades para DELETE y recrear:
    - Después de eliminar un usuario, debe ser posible crear otro con el mismo email
    - El nuevo usuario debe tener un ID diferente
    """
    crud = UserCRUD()
    
    # Crear usuario original
    original_user = crud.create(name, email, age)
    original_id = original_user.id
    
    # Eliminar usuario
    result = crud.delete(original_id)
    assert result is True
    assert crud.count() == 0
    
    # Recrear usuario con los mismos datos
    new_user = crud.create(name, email, age)
    
    # Propiedades que siempre deben cumplirse
    assert new_user.id != original_id  # ID debe ser diferente
    assert new_user.name == name.strip()
    assert new_user.email == email.lower()
    assert new_user.age == age
    assert crud.count() == 1
    assert crud.exists(new_user.id) is True
    assert crud.exists(original_id) is False


def test_clear_all_users_properties():
    """
    Prueba basada en propiedades para clear():
    - clear() debe eliminar todos los usuarios
    - Después de clear(), el CRUD debe estar en estado inicial
    """
    crud = UserCRUD()
    
    # Crear algunos usuarios
    users = [
        crud.create("User 1", "user1@example.com", 25),
        crud.create("User 2", "user2@example.com", 30),
        crud.create("User 3", "user3@example.com", 35)
    ]
    
    assert crud.count() > 0
    
    # Limpiar todos los usuarios
    crud.clear()
    
    # Propiedades que siempre deben cumplirse después de clear()
    assert crud.count() == 0
    assert crud.get_all() == []
    
    # Ningún usuario debe existir
    for user in users:
        assert crud.exists(user.id) is False
        assert crud.get_by_id(user.id) is None
        assert crud.get_by_email(user.email) is None
    
    # Debe ser posible crear nuevos usuarios después de clear()
    new_user = crud.create("New User", "new@example.com", 40)
    assert crud.count() == 1
    assert crud.exists(new_user.id) is True