#!/usr/bin/env python3
"""
Ejemplo de uso del CRUD de usuarios con property-based testing.
Este script demuestra cómo usar las operaciones CRUD básicas.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from user_crud.crud import UserCRUD
from user_crud.models import User

def main():
    """Función principal que demuestra el uso del CRUD."""
    print("=== CRUD de Usuarios - Ejemplo de Uso ===\n")
    
    # Crear instancia del CRUD
    crud = UserCRUD()
    print("✓ CRUD inicializado")
    
    # CREATE - Crear usuarios
    print("\n--- CREATE ---")
    try:
        user1 = crud.create("Juan Pérez", "juan@example.com", 30)
        print(f"✓ Usuario creado: {user1.name} ({user1.email})")
        
        user2 = crud.create("María García", "maria@example.com", 25)
        print(f"✓ Usuario creado: {user2.name} ({user2.email})")
        
        user3 = crud.create("Carlos López", "carlos@example.com", 35)
        print(f"✓ Usuario creado: {user3.name} ({user3.email})")
        
    except ValueError as e:
        print(f"✗ Error al crear usuario: {e}")
    
    # READ - Leer usuarios
    print("\n--- READ ---")
    
    # Leer por ID
    retrieved_user = crud.get_by_id(user1.id)
    if retrieved_user:
        print(f"✓ Usuario encontrado por ID: {retrieved_user.name}")
    
    # Leer por email
    retrieved_user = crud.get_by_email("maria@example.com")
    if retrieved_user:
        print(f"✓ Usuario encontrado por email: {retrieved_user.name}")
    
    # Leer todos los usuarios
    all_users = crud.get_all()
    print(f"✓ Total de usuarios: {len(all_users)}")
    for user in all_users:
        print(f"  - {user.name} ({user.email}, {user.age} años)")
    
    # UPDATE - Actualizar usuario
    print("\n--- UPDATE ---")
    try:
        updated_user = crud.update(user1.id, age=31, name="Juan Carlos Pérez")
        if updated_user:
            print(f"✓ Usuario actualizado: {updated_user.name}, {updated_user.age} años")
            print(f"  Actualizado el: {updated_user.updated_at}")
    except ValueError as e:
        print(f"✗ Error al actualizar usuario: {e}")
    
    # DELETE - Eliminar usuario
    print("\n--- DELETE ---")
    success = crud.delete(user2.id)
    if success:
        print(f"✓ Usuario eliminado: {user2.name}")
        print(f"✓ Usuarios restantes: {crud.count()}")
    
    # Verificar que el usuario fue eliminado
    deleted_user = crud.get_by_email("maria@example.com")
    if deleted_user is None:
        print("✓ Confirmado: el usuario eliminado no existe")
    
    # Mostrar estado final
    print("\n--- ESTADO FINAL ---")
    final_users = crud.get_all()
    print(f"Usuarios en el sistema: {len(final_users)}")
    for user in final_users:
        print(f"  - {user.name} ({user.email})")
    
    # Demostrar validaciones
    print("\n--- VALIDACIONES ---")
    try:
        # Intentar crear usuario con email duplicado
        crud.create("Otro Usuario", "juan@example.com", 40)
    except ValueError as e:
        print(f"✓ Validación funcionando - Email duplicado: {e}")
    
    try:
        # Intentar crear usuario con datos inválidos
        crud.create("", "invalid-email", -5)
    except ValueError as e:
        print(f"✓ Validación funcionando - Datos inválidos: {e}")
    
    print("\n=== Fin del ejemplo ===")

if __name__ == "__main__":
    main()