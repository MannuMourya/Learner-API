from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.session import engine, SessionLocal
from app.models.base import Base
from app.models.user import User
from app.core.security import get_password_hash
from loguru import logger

def init() -> None:
    logger.info("Creating database tables if not exist...")
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        # Seed admin
        admin_email = "admin@example.com"
        if not db.scalar(select(User).where(User.email == admin_email)):
            admin = User(
                email=admin_email,
                hashed_password=get_password_hash("adminpass"),
                role="admin",
            )
            admin.ensure_api_key()
            db.add(admin)

        # Seed regular user
        user_email = "user@example.com"
        if not db.scalar(select(User).where(User.email == user_email)):
            u = User(
                email=user_email,
                hashed_password=get_password_hash("userpass"),
                role="user",
            )
            u.ensure_api_key()
            db.add(u)

        db.commit()
    logger.info("DB init complete.")

if __name__ == "__main__":
    init()
