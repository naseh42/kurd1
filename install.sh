#!/bin/bash

# بررسی دسترسی‌های root
if [ "$EUID" -ne 0 ]; then
    echo "لطفاً این اسکریپت را با دسترسی‌های root اجرا کنید."
    exit 1
fi

echo "شروع نصب و پیکربندی پروژه..."

# نصب ابزارهای ضروری
echo "نصب ابزارهای مورد نیاز..."
apt update && apt install -y python3 python3-pip sqlite3 unzip jq curl wget wireguard-tools uuid-runtime openssl certbot || { echo "خطا در نصب ابزارهای ضروری"; exit 1; }

# نصب virtualenv برای مدیریت محیط مجازی
echo "نصب virtualenv..."
pip3 install virtualenv || { echo "خطا در نصب virtualenv"; exit 1; }

# دانلود و نصب Xray
echo "دانلود و نصب Xray..."
curl -Lo xray.zip https://github.com/XTLS/Xray-core/releases/latest/download/Xray-linux-64.zip || { echo "خطا در دانلود Xray"; exit 1; }
unzip -o xray.zip -d xray || { echo "خطا در استخراج فایل Xray"; exit 1; }
mv xray/xray /usr/local/bin/xray || { echo "خطا در انتقال فایل Xray"; exit 1; }
chmod +x /usr/local/bin/xray || { echo "خطا در تنظیم دسترسی‌های Xray"; exit 1; }
rm -rf xray xray.zip

# تنظیم دایرکتوری پروژه
PROJECT_DIR="/opt/backend"
mkdir -p $PROJECT_DIR
echo "انتقال فایل‌های پروژه..."
if ! cp -r ./backend/* $PROJECT_DIR/; then
    echo "خطا در انتقال فایل‌های پروژه"
    exit 1
fi

# تولید UUID یکتا برای کانفیگ Xray و WireGuard
echo "تولید UUID و کلیدهای WireGuard..."
UUID=$(uuidgen)
WG_PRIVATE_KEY=$(wg genkey)
WG_PUBLIC_KEY=$(echo "$WG_PRIVATE_KEY" | wg pubkey)
WG_CLIENT_PRIVATE_KEY=$(wg genkey)
WG_CLIENT_PUBLIC_KEY=$(echo "$WG_CLIENT_PRIVATE_KEY" | wg pubkey)

# ایجاد فایل requirements.txt
echo "ایجاد فایل requirements.txt..."
cat <<EOL > $PROJECT_DIR/requirements.txt
fastapi
sqlalchemy
pydantic
uvicorn
EOL

# تنظیم PYTHONPATH
echo "تنظیم PYTHONPATH..."
export PYTHONPATH=/opt
if ! grep -q "PYTHONPATH=/opt" ~/.bashrc; then
    echo "export PYTHONPATH=/opt" >> ~/.bashrc
fi

# ایجاد محیط مجازی پایتون
echo "ایجاد محیط مجازی..."
cd $PROJECT_DIR || { echo "خطا: مسیر پروژه یافت نشد"; exit 1; }
virtualenv venv || { echo "خطا در ایجاد محیط مجازی"; exit 1; }
source venv/bin/activate || { echo "خطا در فعال‌سازی محیط مجازی"; exit 1; }

# نصب وابستگی‌ها
echo "نصب وابستگی‌های پروژه..."
pip install --upgrade pip || { echo "خطا در به‌روزرسانی pip"; exit 1; }
pip install -r requirements.txt || { echo "خطا در نصب وابستگی‌ها"; exit 1; }

# تنظیم دسترسی‌ها
chmod -R 755 $PROJECT_DIR || { echo "خطا در تنظیم دسترسی‌ها"; exit 1; }

# مدیریت دامنه‌ها
echo "آیا می‌خواهید دامنه‌ای اضافه کنید یا دامنه‌های جدیدی ثبت کنید؟ (y/n)"
read -r ADD_DOMAIN

if [[ "$ADD_DOMAIN" == "y" ]]; then
    # دریافت دامنه‌ها از کاربر
    echo "لطفاً دامنه جدید را وارد کنید:"
    read -r DOMAIN_NAME

    echo "دریافت گواهی‌های TLS برای دامنه $DOMAIN_NAME..."
    certbot certonly --standalone --agree-tos --email your-email@example.com -d "$DOMAIN_NAME" || { echo "خطا در دریافت گواهی‌های TLS برای $DOMAIN_NAME"; exit 1; }

    # به‌روزرسانی کانفیگ Xray
    CERT_PATH="/etc/letsencrypt/live/$DOMAIN_NAME/fullchain.pem"
    KEY_PATH="/etc/letsencrypt/live/$DOMAIN_NAME/privkey.pem"
    echo "به‌روزرسانی کانفیگ Xray با دامنه جدید $DOMAIN_NAME..."
    CONFIG_FILE="/usr/local/etc/xray/config.json"
    jq ".inbounds[0].streamSettings.tlsSettings.certificates += [{\"certificateFile\": \"$CERT_PATH\", \"keyFile\": \"$KEY_PATH\"}]" "$CONFIG_FILE" > tmp.$$.json && mv tmp.$$.json "$CONFIG_FILE"
fi

# تنظیم مسیر WebSocket در Xray
echo "تنظیم مسیر WebSocket در کانفیگ Xray..."
CONFIG_FILE="/usr/local/etc/xray/config.json"
jq '.inbounds[0].streamSettings += {"wsSettings": {"path": "/websocket"}}' "$CONFIG_FILE" > tmp.$$.json && mv tmp.$$.json "$CONFIG_FILE"

# راه‌اندازی سرویس‌ها
echo "راه‌اندازی مجدد سرویس Xray..."
systemctl daemon-reload
systemctl restart xray.service || { echo "خطا در راه‌اندازی Xray"; exit 1; }

echo "راه‌اندازی سرویس WireGuard..."
systemctl enable wg-quick@wg0
systemctl start wg-quick@wg0 || { echo "خطا در راه‌اندازی WireGuard"; exit 1; }

echo "نصب و پیکربندی با موفقیت انجام شد!"
