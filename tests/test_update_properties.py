import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from hypothesis import given, strategies as st, assume
from user_crud.models import User
from user_crud.crud import UserCRUD


@given(
    original_name=st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
    original_email=st.emails(),
    original_age=st.integers(min_value=0, max_value=150),
    new_name=st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
    new_email=st.emails(),
    new_age=st.integers(min_value=0, max_value=150)
)
def test_update_user_properties(original_name, original_email, original_age, 
                               new_name, new_email, new_age):
    """
    Prueba basada en propiedades para UPDATE:
    - Un usuario actualizado debe mantener su ID
    - Los campos actualizados deben cambiar
    - Los campos no actualizados deben mantenerse
    - updated_at debe establecerse
    """
    assume(original_email != new_email)  # Evitar emails iguales
    
    crud = UserCRUD()
    
    # Crear usuario original
    user = crud.create(original_name, original_email, original_age)
    original_id = user.id
    original_created_at = user.created_at
    
    # Actualizar usuario
    updated_user = crud.update(user.id, name=new_name, email=new_email, age=new_age)
    
    # Propiedades que siempre deben cumplirse
    assert updated_user is not None
    assert updated_user.id == original_id  # ID no debe cambiar
    assert updated_user.created_at == original_created_at  # created_at no debe cambiar
    assert updated_user.updated_at is not None  # updated_at debe establecerse
    assert updated_user.name == new_name.strip()
    assert updated_user.email == new_email.lower()
    assert updated_user.age == new_age
    
    # El usuario actualizado debe ser recuperable
    retrieved_user = crud.get_by_id(user.id)
    assert retrieved_user == updated_user
    assert crud.get_by_email(new_email) == updated_user
    
    # El email anterior no debe funcionar más
    assert crud.get_by_email(original_email) is None


@given(
    name=st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
    email=st.emails(),
    age=st.integers(min_value=0, max_value=150),
    field_to_update=st.sampled_from(['name', 'email', 'age'])
)
def test_update_single_field_properties(name, email, age, field_to_update):
    """
    Prueba basada en propiedades para UPDATE de un solo campo:
    - Solo el campo especificado debe cambiar
    - Los otros campos deben mantenerse iguales
    """
    crud = UserCRUD()
    
    # Crear usuario original
    user = crud.create(name, email, age)
    original_values = {
        'name': user.name,
        'email': user.email,
        'age': user.age
    }
    
    # Preparar valores nuevos
    new_values = {
        'name': "Nuevo Nombre",
        'email': "nuevo@example.com",
        'age': 99
    }
    
    # Actualizar solo un campo
    update_kwargs = {field_to_update: new_values[field_to_update]}
    updated_user = crud.update(user.id, **update_kwargs)
    
    # Propiedades que siempre deben cumplirse
    assert updated_user is not None
    assert updated_user.id == user.id
    assert updated_user.updated_at is not None
    
    # Solo el campo actualizado debe cambiar
    for field in ['name', 'email', 'age']:
        if field == field_to_update:
            if field == 'email':
                assert getattr(updated_user, field) == new_values[field].lower()
            elif field == 'name':
                assert getattr(updated_user, field) == new_values[field].strip()
            else:
                assert getattr(updated_user, field) == new_values[field]
        else:
            assert getattr(updated_user, field) == original_values[field]


@given(
    users_data=st.lists(
        st.tuples(
            st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
            st.emails(),
            st.integers(min_value=0, max_value=150)
        ),
        min_size=2,
        max_size=5,
        unique_by=lambda x: x[1]  # Emails únicos
    )
)
def test_update_duplicate_email_fails(users_data):
    """
    Prueba basada en propiedades para validar que actualizar con email duplicado falla.
    """
    assume(len(users_data) >= 2)
    
    crud = UserCRUD()
    created_users = []
    
    # Crear usuarios
    for name, email, age in users_data:
        user = crud.create(name, email, age)
        created_users.append(user)
    
    user1 = created_users[0]
    user2 = created_users[1]
    
    # Intentar actualizar user1 con el email de user2 debe fallar
    with pytest.raises(ValueError, match="ya está en uso"):
        crud.update(user1.id, email=user2.email)
    
    # Los usuarios no deben haber cambiado
    assert crud.get_by_id(user1.id) == user1
    assert crud.get_by_id(user2.id) == user2
    assert crud.get_by_email(user1.email) == user1
    assert crud.get_by_email(user2.email) == user2


def test_update_nonexistent_user_properties():
    """
    Prueba basada en propiedades para UPDATE de usuario inexistente:
    - Actualizar un usuario inexistente debe retornar None
    - No debe crear ningún usuario nuevo
    """
    crud = UserCRUD()
    
    # Intentar actualizar usuario inexistente
    result = crud.update("fake-id", name="Nuevo Nombre")
    
    # Propiedades que siempre deben cumplirse
    assert result is None
    assert crud.count() == 0
    assert crud.get_by_id("fake-id") is None


@given(
    name=st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
    email=st.emails(),
    age=st.integers(min_value=0, max_value=150)
)
def test_update_with_invalid_data_properties(name, email, age):
    """
    Prueba basada en propiedades para UPDATE con datos inválidos:
    - Actualizar con datos inválidos debe fallar
    - El usuario original no debe cambiar
    """
    crud = UserCRUD()
    
    # Crear usuario original
    user = crud.create(name, email, age)
    original_user = crud.get_by_id(user.id)
    
    # Intentar actualizar con datos inválidos debe fallar
    with pytest.raises(ValueError):
        crud.update(user.id, name="")  # Nombre vacío
    
    with pytest.raises(ValueError):
        crud.update(user.id, name="   ")  # Nombre solo espacios
    
    with pytest.raises(ValueError):
        crud.update(user.id, email="invalid-email")  # Email inválido
    
    with pytest.raises(ValueError):
        crud.update(user.id, age=-1)  # Edad inválida
    
    with pytest.raises(ValueError):
        crud.update(user.id, age=151)  # Edad inválida
    
    # El usuario original no debe haber cambiado
    current_user = crud.get_by_id(user.id)
    assert current_user == original_user
    assert current_user.updated_at is None  # No debe haberse actualizado


@given(
    name=st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
    email=st.emails(),
    age=st.integers(min_value=0, max_value=150)
)
def test_update_no_changes_properties(name, email, age):
    """
    Prueba basada en propiedades para UPDATE sin cambios:
    - Actualizar sin proporcionar campos debe retornar el usuario sin cambios
    """
    crud = UserCRUD()
    
    # Crear usuario original
    user = crud.create(name, email, age)
    
    # Actualizar sin proporcionar campos
    updated_user = crud.update(user.id)
    
    # Propiedades que siempre deben cumplirse
    assert updated_user == user  # Debe ser igual al original
    assert updated_user.updated_at is None  # No debe haberse actualizado