import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from hypothesis import given, strategies as st, assume
from user_crud.models import User
from user_crud.crud import UserCRUD


@given(
    name=st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
    email=st.emails(),
    age=st.integers(min_value=0, max_value=150)
)
def test_create_user_properties(name, email, age):
    """
    Prueba basada en propiedades para CREATE:
    - Un usuario creado siempre debe tener un ID único
    - El usuario debe tener los datos que se proporcionaron
    - El email debe estar en minúsculas
    - El nombre debe estar sin espacios al inicio/final
    """
    crud = UserCRUD()
    
    user = crud.create(name, email, age)
    
    # Propiedades que siempre deben cumplirse
    assert user.id is not None
    assert len(user.id) > 0
    assert user.name == name.strip()
    assert user.email == email.lower()
    assert user.age == age
    assert user.created_at is not None
    assert user.updated_at is None
    
    # El usuario debe existir en el CRUD
    assert crud.exists(user.id)
    assert crud.get_by_id(user.id) == user
    assert crud.get_by_email(email) == user
    assert crud.count() == 1


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
def test_create_multiple_users_properties(users_data):
    """
    Prueba basada en propiedades para CREATE múltiple:
    - Todos los usuarios creados deben tener IDs únicos
    - No debe haber emails duplicados
    - El contador debe ser correcto
    """
    crud = UserCRUD()
    created_users = []
    
    for name, email, age in users_data:
        user = crud.create(name, email, age)
        created_users.append(user)
    
    # Propiedades que siempre deben cumplirse
    user_ids = [user.id for user in created_users]
    assert len(set(user_ids)) == len(user_ids)  # IDs únicos
    
    user_emails = [user.email for user in created_users]
    assert len(set(user_emails)) == len(user_emails)  # Emails únicos
    
    assert crud.count() == len(users_data)
    
    # Todos los usuarios deben ser recuperables
    all_users = crud.get_all()
    assert len(all_users) == len(users_data)


@given(
    name=st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
    email=st.emails(),
    age=st.integers(min_value=0, max_value=150)
)
def test_create_duplicate_email_fails(name, email, age):
    """
    Prueba basada en propiedades para validar que emails duplicados fallan.
    """
    crud = UserCRUD()
    
    # Crear primer usuario
    user1 = crud.create(name, email, age)
    assert crud.count() == 1
    
    # Intentar crear segundo usuario con mismo email debe fallar
    with pytest.raises(ValueError, match="ya está en uso"):
        crud.create("Otro nombre", email, age + 1)
    
    # El contador no debe haber cambiado
    assert crud.count() == 1
    
    # Solo el primer usuario debe existir
    assert crud.get_by_email(email) == user1


def test_create_invalid_data_properties():
    """
    Prueba basada en propiedades para datos inválidos en CREATE.
    """
    crud = UserCRUD()
    
    # Nombres vacíos deben fallar
    with pytest.raises(ValueError):
        crud.create("", "test@example.com", 25)
    
    with pytest.raises(ValueError):
        crud.create("   ", "test@example.com", 25)
    
    # Emails inválidos deben fallar
    with pytest.raises(ValueError):
        crud.create("Test", "invalid-email", 25)
    
    # Edades inválidas deben fallar
    with pytest.raises(ValueError):
        crud.create("Test", "test@example.com", -1)
    
    with pytest.raises(ValueError):
        crud.create("Test", "test@example.com", 151)
    
    # No debe haberse creado ningún usuario
    assert crud.count() == 0