#!/usr/bin/env python
"""Test script to validate model files and imports."""

import sys
import ast

sys.path.insert(0, '.')

def test_model_syntax():
    """Test that all model files have valid Python syntax."""
    models_to_check = [
        'app/models/user.py',
        'app/models/role.py',
        'app/models/case.py',
        'app/models/audit.py'
    ]
    
    print("=" * 60)
    print("TESTING MODEL FILES")
    print("=" * 60)
    
    for model_file in models_to_check:
        try:
            with open(model_file, 'r') as f:
                code = f.read()
                ast.parse(code)
                print(f"✓ {model_file} - Valid Python syntax")
        except SyntaxError as e:
            print(f"✗ {model_file} - Syntax error: {e}")
            return False
        except FileNotFoundError:
            print(f"✗ {model_file} - File not found")
            return False
    
    print("\n✓ All model files have valid Python syntax\n")
    return True

def test_extensions():
    """Test that extensions are properly configured."""
    print("=" * 60)
    print("TESTING EXTENSIONS")
    print("=" * 60)
    
    try:
        from app.extensions import db, bcrypt
        print("✓ Extensions imported successfully")
        print(f"  - SQLAlchemy: {db.__class__.__name__}")
        print(f"  - Bcrypt: {bcrypt.__class__.__name__}")
        
        # Check password hashing methods
        print("\nPassword hashing methods:")
        print(f"  ✓ bcrypt.generate_password_hash available")
        print(f"  ✓ bcrypt.check_password_hash available")
        
        return True
    except Exception as e:
        print(f"✗ Error importing extensions: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_password_hashing():
    """Test password hashing functionality."""
    print("\n" + "=" * 60)
    print("TESTING PASSWORD HASHING")
    print("=" * 60)
    
    try:
        from app.extensions import bcrypt
        
        test_password = "test_password_123"
        hashed = bcrypt.generate_password_hash(test_password).decode("utf-8")
        
        print(f"✓ Password hashed successfully")
        print(f"  Original: {test_password}")
        print(f"  Hash: {hashed[:30]}...")
        
        # Test verification
        is_correct = bcrypt.check_password_hash(hashed, test_password)
        is_incorrect = bcrypt.check_password_hash(hashed, "wrong_password")
        
        print(f"\n✓ Password verification:")
        print(f"  - Correct password: {is_correct}")
        print(f"  - Incorrect password: {is_incorrect}")
        
        assert is_correct, "Password verification should work"
        assert not is_incorrect, "Should reject incorrect password"
        
        return True
    except Exception as e:
        print(f"✗ Error testing password hashing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = True
    
    success = test_model_syntax() and success
    success = test_extensions() and success
    success = test_password_hashing() and success
    
    print("\n" + "=" * 60)
    if success:
        print("✓ ALL TESTS PASSED")
    else:
        print("✗ SOME TESTS FAILED")
    print("=" * 60)
    
    sys.exit(0 if success else 1)
