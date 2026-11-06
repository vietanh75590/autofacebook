# Facebook Page Manager — Python / Windows

CLI quản trị Page bằng Meta Graph API. Phiên bản tối thiểu: nhập token OAuth
đã cấp, liệt kê Page và xem trước bài viết cho một Page. Không gửi bài thật.
Không có follow, reaction hoặc bình luận hàng loạt.

## Chạy trên Windows (CMD)

1. Cài Python 3.12 từ https://www.python.org/downloads/windows/ (chọn Add Python to PATH).
2. Tải mã nguồn chứa những file này bằng Code → Download ZIP rồi Extract All.
   Nếu thay đổi chưa được đẩy lên GitHub, ZIP từ GitHub sẽ chưa chứa phiên bản này.
3. Mở CMD, chuyển tới thư mục có `main.py` (thay đường dẫn bên dưới):

```bat
cd /d "C:\Users\TEN_BAN\Downloads\autofacebook-main"
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe main.py --demo pages
.venv\Scripts\python.exe main.py --demo preview --page-id 123456789 --message-file message.example.txt
```

Demo dùng Page giả; không cần tài khoản, không gọi mạng và không đăng bài.
Sửa nội dung `message.example.txt` bằng Notepad rồi lưu UTF-8 để thử.

## Kết nối Page thật

Bản này **chưa triển khai OAuth redirect/login trong ứng dụng**. Bạn phải lấy
User Access Token qua luồng OAuth chính thức của ứng dụng Meta do mình quản lý,
hoặc Graph API Explorer của Meta để thử nghiệm với tài khoản có vai trò phù hợp.
Không nhập mật khẩu, cookie, mã 2FA vào tool. Không lấy token từ dịch vụ bên ngoài.

1. Tạo/cấu hình ứng dụng ở https://developers.facebook.com/apps/ và chọn use case
   hỗ trợ Facebook Login / quản lý Page theo dashboard hiện hành.
2. Kiểm tra tài liệu chính thức trước khi xin quyền:
   - https://developers.facebook.com/docs/pages-api/getting-started/
   - https://developers.facebook.com/docs/graph-api/reference/user/accounts/
   - https://developers.facebook.com/docs/facebook-login/
   - https://developers.facebook.com/docs/permissions/
   - https://developers.facebook.com/docs/graph-api/changelog/
3. `/me/accounts` với `id,name,tasks` dùng User Access Token; `pages_show_list`
   là quyền liên quan việc liệt kê Page. Page xuất hiện phụ thuộc quyền đã cấp,
   lựa chọn Page trong OAuth, vai trò/tác vụ và loại ứng dụng. Không bảo đảm liệt kê
   mọi Page nhìn thấy trên giao diện Facebook.
4. Chế độ development thường giới hạn người dùng có vai trò trong app.
   Sử dụng cho người dùng bên ngoài có thể cần Advanced Access, App Review và
   xác minh doanh nghiệp theo yêu cầu Meta. Kiểm tra dashboard của app.
5. Copy cấu hình rồi điền **phiên bản API đang được Meta hỗ trợ cho app của bạn**:

```bat
copy config.example.json config.json
notepad config.json
.venv\Scripts\python.exe main.py auth set
.venv\Scripts\python.exe main.py pages
.venv\Scripts\python.exe main.py preview --page-id ID_PAGE_CUA_BAN --message-file message.example.txt
```

`api_version` cố ý để trống, chỉ chấp nhận dạng `vNN.0`. Không dùng nguyên
`vNN.0` hoặc phiên bản giả từ tests. Không tự chọn phiên bản khi chưa kiểm tra Meta.
Token được nhập ẩn và lưu trong **Windows Credential Manager**, không lưu vào JSON.
`auth set` chỉ lưu token, không xác thực nó; `pages` mới kiểm tra quyền truy cập thực tế.
Lệnh `auth delete` xóa token đã lưu. Token hết hạn hoặc bị thu hồi phải cấp lại.
Không truyền token qua tham số dòng lệnh. Biến `META_USER_TOKEN` nếu đã có sẽ
được ưu tiên hơn token trong Credential Manager; tránh cấu hình nhầm tài khoản.

`preview` thật chỉ đọc danh sách Page và tạo bản xem trước tại máy; không kiểm tra
khả năng đăng bài. Chưa hỗ trợ đăng/lên lịch, lấy Page Access Token, đọc hoặc trả lời
bình luận. Những phần đó cần xác minh API và quyền riêng (ví dụ
`pages_manage_posts`, `pages_read_engagement`, `pages_manage_engagement` tùy tác vụ).
Không dùng User Access Token thay Page Access Token để tự bổ sung lệnh ghi.

## Mạng, dữ liệu và lỗi

- Chỉ gọi HTTPS `graph.facebook.com`; không theo redirect hoặc URL phân trang từ server.
- Token nằm trong Authorization header. Không ghi token, response hoặc exception thô
  vào log. Không có log file mặc định; kết quả và lỗi đã lọc được in ra terminal.
- Chỉ GET được retry khi HTTP 429/5xx, số lần cấu hình được giới hạn. Retry-After
  dạng số được chờ tối đa 60 giây; hết lượt sẽ dừng. Không tự retry lỗi quyền/token.
- Không có secret nào trong config; `config.json` được Git ignore.
- Môi trường cloud hiện chưa xác minh truy cập Meta: proxy trả HTTP 403 khi đọc
  tài liệu Meta. Vì vậy các endpoint/quyền trên là hướng dẫn cần đối chiếu, không phải
  tuyên bố đã kiểm tra tài liệu mới nhất. Chưa chạy API thật vì chưa có token.
- Nếu dùng cloud, cần cho phép `graph.facebook.com` và `developers.facebook.com`
  trong environment settings. Không cần thay đổi thiết lập mạng Windows nếu truy cập
  trực tiếp Meta bình thường.

## Kiểm thử

```bat
.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Tests dùng HTTP giả lập, kiểm tra phân trang, bảo vệ token trong lỗi, retry,
Page không được quản lý và dry-run. Không thay thế kiểm thử live với Meta hoặc
kiểm thử Windows Credential Manager trên máy Windows.

## Cấu trúc

- `main.py`: CLI, lệnh auth/pages/preview.
- `auth_module.py`: Windows Credential Manager và token môi trường.
- `config.py`: đọc/kiểm tra cấu hình.
- `graph_client.py`: HTTPS GET, timeout và retry giới hạn.
- `page_service.py`: Page được cấp quyền và phân trang.
- `publishing_service.py`: tạo bản xem trước, không ghi lên Meta.
- `tests/`: kiểm thử không cần tài khoản.

Python tối thiểu 3.12. Cài đặt dùng requests và keyring; trên cloud Linux có thể dùng
`.venv/bin/python` thay đường dẫn Windows. Không cần tạo Git worktree để chạy.
