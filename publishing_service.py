def preview_post(page_id, message, pages):
    if not page_id.isdecimal():
        raise ValueError("Page ID phải gồm các chữ số.")
    if not message.strip():
        raise ValueError("Nội dung không được trống.")
    page = next((p for p in pages if str(p["id"]) == page_id), None)
    if page is None:
        raise ValueError("Page không nằm trong danh sách được cấp quyền.")
    return {
        "mode": "dry-run", "network_write": False,
        "page": {"id": page_id, "name": page["name"]},
        "message": message,
        "note": "Chỉ xem trước, chưa kiểm tra quyền đăng và không gửi bài lên Facebook.",
    }
