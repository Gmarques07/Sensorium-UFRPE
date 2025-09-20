# backend/tests/integration/conftest.py
import pytest
from sqlalchemy.orm import Session
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

# Import all necessary models
from backend.app.db.session import SessionLocal
from backend.app.models import Notificacao, PhNivel, NivelAgua, Local, Usuario, UsuarioSensor

@pytest.fixture(scope="function", autouse=True)
def auto_cleanup_db():
    """
    Fixture to automatically clean up known test data after each integration test.
    """
    yield  # Run the test

    # --- Teardown: Clean up database ---
    print("\n--- Running automatic test cleanup ---")
    db: Session = SessionLocal()
    try:
        # Find test users based on the email pattern used in tests
        test_users = db.query(Usuario).filter(Usuario.email.like('%@example.com')).all()
        if not test_users:
            print("--- No test users found to clean up ---")
            db.close()
            return

        test_user_ids = [user.id for user in test_users]
        test_user_emails = [user.email for user in test_users]

        # --- Delete related data first to avoid foreign key violations ---

        # 1. Delete UsuarioSensor entries
        db.query(UsuarioSensor).filter(UsuarioSensor.usuario_id.in_(test_user_ids)).delete(synchronize_session=False)
        
        # 2. Delete Notificacao entries
        db.query(Notificacao).filter(Notificacao.email_usuario.in_(test_user_emails)).delete(synchronize_session=False)

        # (Add cleanup for other test data like 'Local' if necessary in the future)

        # 3. Now, delete the test users themselves
        for user in test_users:
            db.delete(user)

        db.commit()
        print(f"--- Cleanup successful: Removed {len(test_users)} test user(s) and related data. ---")
    except Exception as e:
        print(f"--- Cleanup failed: {e} ---")
        db.rollback()
    finally:
        db.close()