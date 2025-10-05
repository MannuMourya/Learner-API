from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
import secrets

from .base import Base

class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(320), unique=True, index=True, nullable=False)
    hashed_password = Column(String(1024), nullable=False)
    role = Column(String(50), default="user", nullable=False)
    api_key = Column(String(128), unique=True, index=True, nullable=True)

    items = relationship("Item", back_populates="owner")

    def ensure_api_key(self):
        if not self.api_key:
            self.api_key = secrets.token_hex(20)
