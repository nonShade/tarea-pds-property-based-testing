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
def test_read_by_id_properties(users_data):
    """
    Prueba basada en propiedades para READ por ID:
    - Un usuario creado siempre debe ser recuperable por su ID
    - get_by_id con ID inexistente debe retornar None
    - get_by_id siempre debe retornar el usuario correcto
    """
    crud = UserCRUD()
    created_users = []
    
    # Crear usuarios
    for name, email, age in users_data:
        user = crud.create(name, email, age)
        created_users.append(user)
    
    # Propiedades que siempre deben cumplirse
    for user in created_users:
        retrieved_user = crud.get_by_id(user.id)
        assert retrieved_user is not None
        assert retrieved_user == user
        assert retrieved_user.id == user.id
        assert retrieved_user.email == user.email
        assert retrieved_user.name == user.name
        assert retrieved_user.age == user.age
    
    # ID inexistente debe retornar None
    fake_id = "fake-id-12345"
    assert crud.get_by_id(fake_id) is None


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
def test_read_by_email_properties(users_data):
    """
    Prueba basada en propiedades para READ por email:
    - Un usuario creado siempre debe ser recuperable por su email
    - get_by_email con email inexistente debe retornar None
    - get_by_email debe ser case-insensitive
    """
    crud = UserCRUD()
    created_users = []
    
    # Crear usuarios
    for name, email, age in users_data:
        user = crud.create(name, email, age)
        created_users.append(user)
    
    # Propiedades que siempre deben cumplirse
    for user in created_users:
        # Buscar por email original
        retrieved_user = crud.get_by_email(user.email)
        assert retrieved_user is not None
        assert retrieved_user == user
        
        # Buscar por email en mayúsculas (case-insensitive)
        retrieved_user_upper = crud.get_by_email(user.email.upper())
        assert retrieved_user_upper is not None
        assert retrieved_user_upper == user
        
        # Buscar por email con espacios
        retrieved_user_spaces = crud.get_by_email(f"  {user.email}  ")
        assert retrieved_user_spaces is not None
        assert retrieved_user_spaces == user
    
    # Email inexistente debe retornar None
    fake_email = "nonexistent@fake.com"
    assert crud.get_by_email(fake_email) is None


@given(
    users_data=st.lists(
        st.tuples(
            st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
            st.emails(),
            st.integers(min_value=0, max_value=150)
        ),
        min_size=0,
        max_size=15,
        unique_by=lambda x: x[1]  # Emails únicos
    )
)
def test_get_all_properties(users_data):
    """
    Prueba basada en propiedades para READ todos los usuarios:
    - get_all() debe retornar exactamente los usuarios creados
    - La cantidad debe coincidir con count()
    - No debe haber duplicados
    """
    crud = UserCRUD()
    created_users = []
    
    # Crear usuarios
    for name, email, age in users_data:
        user = crud.create(name, email, age)
        created_users.append(user)
    
    # Propiedades que siempre deben cumplirse
    all_users = crud.get_all()
    
    assert len(all_users) == len(created_users)
    assert len(all_users) == crud.count()
    
    # Todos los usuarios creados deben estar en la lista
    for user in created_users:
        assert user in all_users
    
    # No debe haber duplicados
    user_ids = [user.id for user in all_users]
    assert len(set(user_ids)) == len(user_ids)
    
    user_emails = [user.email for user in all_users]
    assert len(set(user_emails)) == len(user_emails)


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
def test_exists_properties(users_data):
    """
    Prueba basada en propiedades para verificar existencia:
    - exists() debe retornar True para usuarios creados
    - exists() debe retornar False para IDs inexistentes
    """
    crud = UserCRUD()
    created_users = []
    
    # Crear usuarios
    for name, email, age in users_data:
        user = crud.create(name, email, age)
        created_users.append(user)
    
    # Propiedades que siempre deben cumplirse
    for user in created_users:
        assert crud.exists(user.id) is True
    
    # IDs inexistentes deben retornar False
    fake_ids = ["fake-1", "fake-2", "nonexistent"]
    for fake_id in fake_ids:
        assert crud.exists(fake_id) is False


def test_read_empty_crud_properties():
    """
    Prueba basada en propiedades para CRUD vacío:
    - Un CRUD recién creado debe estar vacío
    - Todas las operaciones de lectura deben manejar correctamente el estado vacío
    """
    crud = UserCRUD()
    
    # Propiedades que siempre deben cumplirse en un CRUD vacío
    assert crud.count() == 0
    assert crud.get_all() == []
    assert crud.get_by_id("any-id") is None
    assert crud.get_by_email("any@email.com") is None
    assert crud.exists("any-id") is False