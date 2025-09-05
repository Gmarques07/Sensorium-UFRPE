from app.db.session import SessionLocal
from sqlalchemy import text


def test_db():
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
    finally:
        db.close()

if __name__ == "__main__":
    test_db()
