from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from backend.database import Base

# مدل کاربران
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    uuid = Column(String(36), unique=True, nullable=False, index=True)
    traffic_limit = Column(Integer, nullable=False, default=0)  # به مگابایت
    usage_duration = Column(Integer, nullable=False, default=0)  # به دقیقه
    simultaneous_connections = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # رابطه با دامنه‌ها
    domains = relationship("Domain", back_populates="owner")

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "uuid": self.uuid,
            "traffic_limit": self.traffic_limit,
            "usage_duration": self.usage_duration,
            "simultaneous_connections": self.simultaneous_connections,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

# مدل دامنه‌ها
class Domain(Base):
    __tablename__ = "domains"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(String(255), nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # رابطه با کاربران
    owner = relationship("User", back_populates="domains")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "owner_id": self.owner_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

# مدل تنظیمات
class Setting(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    language = Column(String(10), nullable=False, default="en")
    theme = Column(String(20), nullable=False, default="light")
    enable_notifications = Column(Integer, nullable=False, default=1)  # 1: فعال، 0: غیرفعال
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "language": self.language,
            "theme": self.theme,
            "enable_notifications": bool(self.enable_notifications),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
