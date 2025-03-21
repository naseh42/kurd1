from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from backend.routers import users, domains, settings
from backend.database import Base, engine

# ایجاد شیء FastAPI
app = FastAPI(
    title="Management Panel API",
    description="Comprehensive API for managing users, domains, settings, and server operations.",
    version="1.0.0"
)

# ایجاد جداول پایگاه داده (در صورت نیاز)
Base.metadata.create_all(bind=engine)

# اضافه کردن فایل‌های استاتیک
app.mount("/static", StaticFiles(directory="backend/static"), name="static")

# افزودن Middleware برای امنیت و دسترسی‌ها
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # بهتر است دامنه‌ها در محیط تولید محدود شوند
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"],  # در محیط تولید این مقدار محدود شود
)

# افزودن روترها
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(domains.router, prefix="/domains", tags=["Domains"])
app.include_router(settings.router, prefix="/settings", tags=["Settings"])

# مسیر اصلی
@app.get("/", tags=["Root"])
def root():
    return {
        "message": "Welcome to the Management Panel API. Use /docs for detailed documentation.",
        "status": "Running"
    }
