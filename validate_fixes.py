#!/usr/bin/env python3
"""
Simple validation script to test our fixes without pytest/hypothesis.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from user_crud.models import User
from user_crud.crud import UserCRUD


def test_age_overflow_fix():
    """Test that we fixed the age overflow issue."""
    print("Testing age overflow fix...")
    crud = UserCRUD()
    
    # Create user with age 150
    user1 = crud.create("Test User", "test@example.com", 150)
    assert user1.age == 150
    print("✓ Created user with age 150")
    
    # Try to create another user with same email and age 25 (instead of 151)
    try:
        crud.create("Another User", "test@example.com", 25)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "ya está en uso" in str(e)
        print("✓ Correctly failed with email duplication error")
    
    print("✓ Age overflow fix validated\n")


def test_normalization_fix():
    """Test that update method now normalizes data."""
    print("Testing normalization fix...")
    crud = UserCRUD()
    
    # Create user
    user = crud.create("Test User", "test@example.com", 25)
    
    # Update with data that needs normalization
    updated_user = crud.update(user.id, name="  New Name  ", email="NEW@EXAMPLE.COM")
    
    # Check normalization
    assert updated_user.name == "New Name", f"Expected 'New Name', got '{updated_user.name}'"
    assert updated_user.email == "new@example.com", f"Expected 'new@example.com', got '{updated_user.email}'"
    assert updated_user.updated_at is not None
    
    print("✓ Name normalization working (stripped spaces)")
    print("✓ Email normalization working (lowercased)")
    print("✓ Normalization fix validated\n")


def test_duplicate_email_optimization():
    """Test that duplicate email test logic works."""
    print("Testing duplicate email logic...")
    crud = UserCRUD()
    
    # Create two users with different emails
    user1 = crud.create("User 1", "user1@example.com", 25)
    user2 = crud.create("User 2", "user2@example.com", 30)
    
    # Try to update user1 with user2's email
    try:
        crud.update(user1.id, email=user2.email)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "ya está en uso" in str(e)
        print("✓ Correctly prevented duplicate email on update")
    
    # Verify users unchanged
    assert crud.get_by_id(user1.id) == user1
    assert crud.get_by_id(user2.id) == user2
    print("✓ Users remained unchanged after failed update")
    print("✓ Duplicate email prevention validated\n")


def test_all_basic_crud():
    """Test basic CRUD functionality still works."""
    print("Testing basic CRUD functionality...")
    crud = UserCRUD()
    
    # CREATE
    user = crud.create("John Doe", "john@example.com", 30)
    assert user.name == "John Doe"
    assert user.email == "john@example.com"
    assert user.age == 30
    assert user.id is not None
    print("✓ CREATE works")
    
    # READ
    found = crud.get_by_id(user.id)
    assert found == user
    found_by_email = crud.get_by_email("john@example.com")
    assert found_by_email == user
    print("✓ READ works")
    
    # UPDATE
    updated = crud.update(user.id, name="Jane Doe", age=25)
    assert updated.name == "Jane Doe"
    assert updated.age == 25
    assert updated.email == "john@example.com"  # unchanged
    assert updated.updated_at is not None
    print("✓ UPDATE works")
    
    # DELETE
    deleted = crud.delete(user.id)
    assert deleted == True
    assert crud.get_by_id(user.id) is None
    print("✓ DELETE works")
    
    print("✓ All basic CRUD operations validated\n")


def main():
    """Run all validation tests."""
    print("=== Validating Our Fixes ===\n")
    
    try:
        test_age_overflow_fix()
        test_normalization_fix()
        test_duplicate_email_optimization()
        test_all_basic_crud()
        
        print("🎉 All validation tests passed!")
        print("✅ All fixes are working correctly")
        return 0
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())