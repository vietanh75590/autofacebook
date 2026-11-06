from graph_client import GraphError

class PageService:
    def __init__(self, client, token):
        self.client = client
        self.token = token

    def list_pages(self):
        pages = []
        cursor = None
        seen = set()
        for _ in range(1000):
            params = {"fields": "id,name,tasks", "limit": 100}
            if cursor:
                params["after"] = cursor
            body = self.client.get("me/accounts", self.token, params)
            rows = body.get("data")
            if not isinstance(rows, list) or any(not isinstance(p, dict) or "id" not in p for p in rows):
                raise GraphError("Danh sách Page không hợp lệ.")
            pages.extend({"id": p["id"], "name": p.get("name", ""), "tasks": p.get("tasks", [])} for p in rows)
            paging = body.get("paging", {})
            if not paging.get("next"):
                return pages
            # Không truy cập URL next chứa token hoặc host ngoài; dùng lại endpoint cố định.
            cursor = paging.get("cursors", {}).get("after")
            if not cursor or cursor in seen:
                raise GraphError("Phân trang không hợp lệ; chưa lấy đủ Page.")
            seen.add(cursor)
        raise GraphError("Vượt giới hạn phân trang; chưa lấy đủ Page.")
