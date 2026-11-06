import os
import sys
import keyring

SERVICE = "autofacebook-page-manager"
ACCOUNT = "meta-user-token"

def windows_store():
    if sys.platform != "win32":
        raise ValueError("Lưu token chỉ hỗ trợ Windows Credential Manager. Trên cloud dùng META_USER_TOKEN.")
    from keyring.backends.Windows import WinVaultKeyring
    return WinVaultKeyring()

def save_token(token):
    token = token.strip()
    if not token or any(c.isspace() for c in token):
        raise ValueError("Token trống hoặc có khoảng trắng.")
    windows_store().set_password(SERVICE, ACCOUNT, token)

def delete_token():
    windows_store().delete_password(SERVICE, ACCOUNT)

def load_token():
    token = os.environ.get("META_USER_TOKEN")
    if not token and sys.platform == "win32":
        token = windows_store().get_password(SERVICE, ACCOUNT)
    if not token:
        raise ValueError("Chưa có token. Chạy: python main.py auth set")
    return token
