from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from decouple import config  # برای مدیریت متغیرهای محیطی

# دریافت URL پایگاه داده از فایل .env
SQLALCHEMY_DATABASE_URL = config("DATABASE_URL", default="sqlite:///./test.db")

# ایجاد Engine برای اتصال به پایگاه داده
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {}
)

# ایجاد Session برای مدیریت تراکنش‌ها
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# پایه‌گذاری برای مدل‌های پایگاه داده
Base = declarative_base()

# Dependency برای دسترسی به Session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
