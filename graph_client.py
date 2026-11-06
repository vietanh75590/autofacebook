import time
import requests

class GraphError(RuntimeError):
    pass

class GraphClient:
    def __init__(self, config, session=None, sleep=time.sleep):
        self.config = config
        self.session = session or requests.Session()
        self.sleep = sleep

    def get(self, path, token, params=None):
        # Chỉ GET; không thực hiện đăng bài hay retry thao tác ghi.
        url = f"https://graph.facebook.com/{self.config.api_version}/{path}"
        for attempt in range(self.config.max_retries + 1):
            try:
                response = self.session.get(
                    url, params=params, headers={"Authorization": f"Bearer {token}"},
                    timeout=self.config.timeout_seconds, allow_redirects=False,
                )
            except requests.RequestException:
                raise GraphError("Không kết nối được Meta. Kiểm tra mạng, proxy và TLS.") from None
            retryable = response.status_code == 429 or response.status_code >= 500
            if retryable and attempt < self.config.max_retries:
                header = response.headers.get("Retry-After", "")
                wait = min(int(header), 60) if header.isdigit() else min(2 ** attempt, 30)
                self.sleep(wait)
                continue
            try:
                body = response.json()
            except ValueError:
                raise GraphError("Meta trả về dữ liệu không phải JSON.") from None
            if not isinstance(body, dict):
                raise GraphError("Phản hồi Meta không hợp lệ.")
            if not 200 <= response.status_code < 300 or "error" in body:
                # Không in raw response: có thể chứa token hoặc dữ liệu cá nhân.
                code = body.get("error", {}).get("code") if isinstance(body.get("error"), dict) else None
                safe_code = code if type(code) is int else "unknown"
                raise GraphError(f"Meta HTTP {response.status_code}, code {safe_code}. Kiểm tra quyền, hạn token và App Review.")
            return body
