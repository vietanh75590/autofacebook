import argparse
import getpass
import json
from pathlib import Path
import sys
from auth_module import save_token, delete_token, load_token
from config import Config
from graph_client import GraphClient, GraphError
from page_service import PageService
from publishing_service import preview_post

DEMO_PAGES = [{"id": "123456789", "name": "Page demo (dữ liệu giả)", "tasks": ["CREATE_CONTENT"]}]

def main(argv=None):
    parser = argparse.ArgumentParser(description="Quản lý Page: liệt kê và xem trước, không đăng thật.")
    parser.add_argument("--config", default="config.json")
    parser.add_argument("--demo", action="store_true", help="Không cần token, không kết nối Facebook")
    subs = parser.add_subparsers(dest="command", required=True)
    auth = subs.add_parser("auth", help="Lưu/xóa token OAuth trên Windows")
    auth.add_argument("action", choices=["set", "delete"])
    subs.add_parser("pages", help="Liệt kê Page được cấp quyền")
    preview = subs.add_parser("preview", help="Xem trước bài viết cho một Page")
    preview.add_argument("--page-id", required=True)
    preview.add_argument("--message-file", required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "auth":
            if args.demo:
                raise ValueError("Không dùng --demo với auth.")
            if args.action == "set":
                save_token(getpass.getpass("Token OAuth từ Meta (ẩn khi nhập): "))
                print("Đã lưu vào Windows Credential Manager; chưa xác thực token với Meta.")
            else:
                delete_token()
                print("Đã xóa token đã lưu.")
            return 0
        message = None
        if args.command == "preview":
            message = Path(args.message_file).read_text(encoding="utf-8-sig")
            if not message.strip():
                raise ValueError("Nội dung không được trống.")
        pages = DEMO_PAGES if args.demo else PageService(GraphClient(Config.load(args.config)), load_token()).list_pages()
        result = pages if args.command == "pages" else preview_post(args.page_id, message, pages)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, GraphError):
        # In thông báo ứng dụng đã kiểm soát; không dump exception thư viện/keyring.
        exc = sys.exception()
        if isinstance(exc, (ValueError, GraphError)) and not isinstance(exc, json.JSONDecodeError):
            print(f"Lỗi: {exc}", file=sys.stderr)
        else:
            print("Lỗi đọc file/cấu hình. Kiểm tra đường dẫn và JSON UTF-8.", file=sys.stderr)
        return 1
    except Exception:
        print("Lỗi hệ thống hoặc kho credential. Không in chi tiết để bảo vệ token.", file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
