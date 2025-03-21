from pydantic import BaseModel, Field
from typing import Optional

# Schema برای کاربران
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Username must be between 3 and 50 characters.")
    uuid: str = Field(..., regex="^[a-f0-9-]{36}$", description="UUID must be in a valid format.")
    traffic_limit: int = Field(..., ge=0, description="Traffic limit in MB.")
    usage_duration: int = Field(..., ge=0, description="Usage duration in minutes.")
    simultaneous_connections: int = Field(..., ge=1, le=10, description="Simultaneous connections allowed.")

class UserCreate(UserBase):
    pass  # برای ساخت کاربر جدید، اطلاعات از UserBase کافی است.

class UserResponse(UserBase):
    id: int
    created_at: Optional[str]
    updated_at: Optional[str]

    class Config:
        orm_mode = True


# Schema برای دامنه‌ها
class DomainBase(BaseModel):
    name: str = Field(..., max_length=255, description="Domain name.")
    description: Optional[str] = Field(None, max_length=255, description="Domain description.")

class DomainCreate(DomainBase):
    pass

class DomainResponse(DomainBase):
    id: int
    owner_id: Optional[int]
    created_at: Optional[str]
    updated_at: Optional[str]

    class Config:
        orm_mode = True


# Schema برای تنظیمات
class SettingsBase(BaseModel):
    language: str = Field(..., max_length=10, description="Language setting.")
    theme: str = Field(..., max_length=20, description="Theme setting (e.g., light or dark).")
    enable_notifications: bool = Field(..., description="Enable or disable notifications.")

class SettingsResponse(SettingsBase):
    id: int
    created_at: Optional[str]
    updated_at: Optional[str]

    class Config:
        orm_mode = True
