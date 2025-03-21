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
    # دریافت نام دامنه از کاربر
    echo "لطفاً دامنه مورد نظر یا دامنه‌های جدید را وارد کنید، جدا شده با کاما:"
    read -r DOMAINS

    # پردازش هر دامنه وارد شده
    IFS=',' read -r -a DOMAIN_ARRAY <<< "$DOMAINS"
    for DOMAIN_NAME in "${DOMAIN_ARRAY[@]}"
    do
        DOMAIN_NAME=$(echo "$DOMAIN_NAME" | xargs) # حذف فاصله‌های اضافی
        echo "دریافت گواهی‌های TLS برای دامنه $DOMAIN_NAME..."
        certbot certonly --standalone --agree-tos --email your-email@example.com -d "$DOMAIN_NAME" || { echo "خطا در دریافت گواهی‌های TLS برای $DOMAIN_NAME"; exit 1; }

        # تنظیم مسیر فایل‌های گواهی در کانفیگ Xray
        CERT_PATH="/etc/letsencrypt/live/$DOMAIN_NAME/fullchain.pem"
        KEY_PATH="/etc/letsencrypt/live/$DOMAIN_NAME/privkey.pem"

        echo "به‌روزرسانی کانفیگ Xray برای دامنه $DOMAIN_NAME..."
        CONFIG_FILE="/usr/local/etc/xray/config.json"
        jq ".inbounds[0].streamSettings.tlsSettings.certificates += [{\"certificateFile\": \"$CERT_PATH\", \"keyFile\": \"$KEY_PATH\"}]" "$CONFIG_FILE" > tmp.$$.json && mv tmp.$$.json "$CONFIG_FILE"
    done
else
    echo "گواهی Self-Signed برای سرور ایجاد می‌شود..."

    # ایجاد گواهی Self-Signed
    mkdir -p /etc/selfsigned
    openssl req -newkey rsa:2048 -nodes -keyout /etc/selfsigned/selfsigned.key -x509 -days 365 -out /etc/selfsigned/selfsigned.crt -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"

    # تنظیم مسیر فایل‌های گواهی Self-Signed در کانفیگ Xray
    CERT_PATH="/etc/selfsigned/selfsigned.crt"
    KEY_PATH="/etc/selfsigned/selfsigned.key"

    echo "به‌روزرسانی کانفیگ Xray برای گواهی Self-Signed..."
    CONFIG_FILE="/usr/local/etc/xray/config.json"
    jq ".inbounds[0].streamSettings.tlsSettings.certificates += [{\"certificateFile\": \"$CERT_PATH\", \"keyFile\": \"$KEY_PATH\"}]" "$CONFIG_FILE" > tmp.$$.json && mv tmp.$$.json "$CONFIG_FILE"
fi

# ایجاد فایل xray.service
echo "ایجاد فایل سرویس Xray..."
cat <<EOL > /etc/systemd/system/xray.service
[Unit]
Description=Xray Service
After=network.target

[Service]
Type=simple
User=root
ExecStart=/usr/local/bin/xray -config /usr/local/etc/xray/config.json
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOL

# بارگذاری و راه‌اندازی سرویس
systemctl daemon-reload
systemctl enable xray.service
systemctl start xray.service || { echo "خطا در راه‌اندازی Xray"; exit 1; }

# ریستارت سرویس‌های دیگر
echo "راه‌اندازی سرویس‌های WireGuard و Xray..."
systemctl restart wg-quick@wg0 || { echo "خطا در ریستارت سرویس WireGuard"; exit 1; }

echo "نصب و پیکربندی با موفقیت انجام شد!"
