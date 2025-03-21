import json
import subprocess
from typing import Dict, Union

# مسیر فایل کانفیگ
XRAY_CONFIG_PATH = "/etc/xray/config.json"
WIREGUARD_CONFIG_PATH = "/etc/wireguard/config.conf"

def load_config(config_path: str) -> Dict:
    """بارگذاری فایل کانفیگ به صورت JSON"""
    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        raise Exception(f"Config file not found: {config_path}")
    except json.JSONDecodeError:
        raise Exception(f"Invalid JSON format in {config_path}")

def save_config(config_path: str, config_data: Dict) -> None:
    """ذخیره تنظیمات در فایل کانفیگ به صورت JSON"""
    try:
        with open(config_path, "w") as f:
            json.dump(config_data, f, indent=4)
    except Exception as e:
        raise Exception(f"Error saving config: {str(e)}")

def add_inbound(config_path: str, inbound_data: Dict) -> None:
    """اضافه کردن اینباند جدید به کانفیگ"""
    config = load_config(config_path)
    if "inbounds" not in config:
        config["inbounds"] = []
    config["inbounds"].append(inbound_data)
    save_config(config_path, config)

def update_port(config_path: str, inbound_tag: str, new_port: int) -> None:
    """تغییر پورت یک اینباند موجود"""
    config = load_config(config_path)
    for inbound in config.get("inbounds", []):
        if inbound.get("tag") == inbound_tag:
            inbound["port"] = new_port
            break
    save_config(config_path, config)

def restart_service(service_name: str) -> None:
    """ری‌استارت سرویس برای اعمال تنظیمات"""
    try:
        subprocess.run(["systemctl", "restart", service_name], check=True)
    except subprocess.CalledProcessError:
        raise Exception(f"Failed to restart service: {service_name}")
