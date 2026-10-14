# BÁO CÁO THỰC HÀNH LAB 04

**Nội dung:** WebVulnScanner và JWTSecure  
**Ngày thực hiện:** 14/10/2026  
**Môi trường:** Windows, Python 3.14.7  
**Tài liệu thực hành:** `lab-04.pdf`, phần 4.2 và 4.4

## 1. Mục tiêu bài thực hành

Trong bài Lab 04, em thực hiện kiểm thử hai chương trình: WebVulnScanner dùng để kiểm tra một số dấu hiệu lỗ hổng web và JWTSecure dùng để kiểm tra, quản lý JWT. Nội dung thực hành gồm cài đặt thư viện, chạy các test có sẵn, kiểm tra chương trình chính và thử các chức năng thông qua giao diện web hoặc request HTTP.

Qua bài thực hành, em tìm hiểu cách chương trình nhận diện các dấu hiệu XSS, SQL Injection, CSRF và SSRF. Với phần JWT, em kiểm tra việc sinh access token, refresh token và cách API Gateway xử lý request khi token hợp lệ hoặc không hợp lệ.

## 2. Chuẩn bị môi trường

Hai dự án được đặt trong thư mục `E:\lab4` và sử dụng chung môi trường ảo `.venv`. Các thư viện chính trong lần thực hành này gồm:

| Thành phần | Phiên bản |
| --- | --- |
| Python | 3.14.7 |
| Flask | 3.1.3 |
| requests | 2.34.2 |
| PyJWT | 2.15.1 |
| pytest | 9.1.1 |

Đầu tiên, em tạo môi trường ảo bằng lệnh:

```powershell
Set-Location E:\lab4
python -m venv .venv
```

Web UI và API Gateway đều sử dụng cổng `5000`, nên hai chương trình được chạy lần lượt. Trang web dùng để thử scanner chạy riêng tại `http://127.0.0.1:8000/`.

## 3. Phần 4.2 - WebVulnScanner

### 3.1. Cấu trúc dự án

Dự án được chia thành các thư mục theo chức năng để thuận tiện cho việc kiểm thử và theo dõi kết quả:

```text
web-vuln-scanner/
├── scanners/
├── report/
├── tests/
├── ui/
│   ├── templates/
│   │   ├── index.html
│   │   └── result.html
│   └── app.py
├── __init__.py
├── main.py
└── requirements.txt
```

Thư mục `scanners` chứa bốn công cụ kiểm tra XSS, SQL Injection, CSRF và SSRF. Thư mục `report` tổng hợp kết quả, còn `ui` chứa giao diện Flask. Các test của chương trình nằm trong thư mục `tests`.

![Hình 1. Cấu trúc thư mục WebVulnScanner](evidence/screenshots/lab04-01.png)

### 3.2. Cài đặt thư viện

Em cài các thư viện trong `requirements.txt` bằng Python của môi trường ảo:

```powershell
Set-Location E:\lab4\web-vuln-scanner
..\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Quá trình cài đặt hoàn tất với mã thoát `0`. Các thư viện cần thiết cho chương trình, trong đó có Flask và requests, đã được cài thành công.

![Hình 2. Kết quả cài đặt thư viện WebVulnScanner](evidence/screenshots/lab04-02.png)

### 3.3. Chạy unittest

Sau khi cài thư viện, em chạy bộ kiểm thử:

```powershell
..\.venv\Scripts\python.exe -m unittest discover tests -v
```

Kết quả nhận được:

```text
Ran 10 tests in 0.003s
OK
```

Cả 10 test đều đạt. Các test kiểm tra việc nhận diện dấu hiệu XSS, SQL Injection, SSRF, trường token CSRF và chức năng tổng hợp báo cáo. Kết quả cho thấy các trường hợp đã viết trong bộ unittest hoạt động đúng như mong đợi.

![Hình 3. Kết quả chạy unittest](evidence/screenshots/lab04-03.png)

### 3.4. Chạy chương trình chính

Em tiếp tục chạy chương trình chính bằng lệnh:

```powershell
..\.venv\Scripts\python.exe main.py
```

Chương trình xuất báo cáo gồm ba phát hiện nghi vấn:

| Loại | Tham số | Mức rủi ro |
| --- | --- | --- |
| XSS | `q` | HIGH |
| SQL Injection | `id` | CRITICAL |
| SSRF | `url` | HIGH |

Đối với CSRF, HTML mẫu có trường `csrf_token`, nên chương trình ghi nhận tìm thấy trường token. Việc này chỉ kiểm tra sự xuất hiện của trường trong HTML, chưa kiểm tra cách máy chủ xác thực token.

Trong code hiện tại, `main.py` dùng phản hồi HTTP giả lập qua `unittest.mock`. Vì vậy, bước này minh họa cách xử lý dữ liệu và tạo báo cáo. Phần kiểm thử qua HTTP được thực hiện tiếp ở Web UI.

![Hình 4. Kết quả chạy main.py của WebVulnScanner](evidence/screenshots/lab04-04.png)

### 3.5. Khởi chạy Flask Web UI

Em khởi chạy giao diện web bằng lệnh:

```powershell
..\.venv\Scripts\python.exe ui\app.py
```

Flask chạy tại địa chỉ `http://127.0.0.1:5000/`, với chế độ debug tắt. Sau khi mở địa chỉ này trên trình duyệt, giao diện Web Vulnerability Scanner hiển thị ô nhập URL và bốn lựa chọn kiểm thử.

![Hình 5. Khởi chạy Flask Web UI](evidence/screenshots/lab04-05.png)

![Hình 6. Giao diện Web Vulnerability Scanner](evidence/screenshots/lab04-06.png)

### 3.6. Thực hiện quét và xem báo cáo

Để thử chức năng quét, em sử dụng một trang web mẫu chạy trên máy cục bộ. Trang này phản chiếu dữ liệu của tham số `q` vào HTML và có một form không chứa trường token CSRF. Trang mẫu được khởi chạy trong một terminal khác:

```powershell
Set-Location E:\lab4
.\.venv\Scripts\python.exe tools\serve_lab.py
```

Trên giao diện scanner, em chọn cả bốn công cụ, nhập URL sau và bấm **Bắt đầu kiểm thử**:

```text
http://127.0.0.1:8000/?id=%27+OR+%271%27%3D%271&url=http%3A%2F%2F127.0.0.1%2Fadmin
```

Sau khi quét, giao diện hiển thị năm phát hiện:

| Loại | Kết quả | Mức rủi ro hiển thị |
| --- | --- | --- |
| XSS | Hai payload được phản chiếu trong phản hồi HTML tại tham số `q` | HIGH |
| SQL Injection | Tham số `id` chứa chuỗi `' OR '1'='1` | CRITICAL |
| CSRF | Không tìm thấy trường token CSRF trong HTML | MEDIUM |
| SSRF | Tham số `url` chứa địa chỉ `http://127.0.0.1/admin` | HIGH |

Báo cáo hiển thị loại phát hiện, vị trí, mô tả, mức rủi ro và gợi ý khắc phục. Kết quả phù hợp với dữ liệu đã đưa vào trang thử nghiệm.

Trong bước này, XSS và CSRF được kiểm tra từ phản hồi HTTP thật của trang mẫu. SQL Injection và SSRF được nhận diện bằng cách đối chiếu chuỗi trong URL; chương trình chưa thử truy vấn cơ sở dữ liệu hay gửi request đến địa chỉ `/admin`. Do đó, các kết quả này được xem là dấu hiệu cần kiểm tra thêm trước khi kết luận có lỗ hổng khai thác được.

![Hình 7. Kết quả quét và báo cáo trên Web UI](evidence/screenshots/lab04-07.png)

## 4. Phần 4.4 - JWTSecure

### 4.1. Cấu trúc dự án

```text
jwt-security-tools/
├── api_gateway/
├── jwt_cracker/
├── jwt_validator/
├── oauth_client/
├── token_manager/
├── tests/
├── main.py
├── pytest.ini
└── requirements.txt
```

Các chức năng chính gồm kiểm tra JWT, dò khóa mẫu bằng wordlist, tạo request OAuth, quản lý token và bảo vệ API thông qua API Gateway. Bộ kiểm thử được đặt trong thư mục `tests`.

![Hình 8. Cấu trúc thư mục JWTSecure](evidence/screenshots/lab04-08.png)

### 4.2. Cài đặt thư viện

Em chuyển sang thư mục `jwt-security-tools` và cài thư viện:

```powershell
Set-Location E:\lab4\jwt-security-tools
..\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Các thư viện PyJWT, requests, Flask và pytest được cài đặt đầy đủ. Lệnh kết thúc với mã thoát `0`.

![Hình 9. Kết quả cài đặt thư viện JWTSecure](evidence/screenshots/lab04-09.png)

### 4.3. Chạy pytest

Em chạy bộ kiểm thử bằng lệnh:

```powershell
..\.venv\Scripts\python.exe -m pytest tests/ -v
```

Kết quả:

```text
12 passed, 4 warnings in 0.47s
```

Cả 12 test đều đạt. Bộ test kiểm tra API Gateway, dò khóa mẫu, OAuthClient, tạo và làm mới token, thu hồi refresh token, cùng các trường hợp JWT sai chữ ký, hết hạn hoặc thiếu trường `exp`.

Trong quá trình chạy có bốn cảnh báo `InsecureKeyLengthWarning`. Các cảnh báo xuất hiện ở test dò khóa vì bài test dùng khóa mẫu ngắn để thử wordlist. Đây là cảnh báo về độ dài khóa, không phải test thất bại.

Phần trao đổi authorization code của OAuthClient sử dụng phản hồi giả lập. Bước này kiểm tra cách chương trình gửi và xử lý request theo dữ liệu mẫu, chưa thực hiện đăng nhập với một dịch vụ OAuth bên ngoài.

![Hình 10. Kết quả chạy pytest](evidence/screenshots/lab04-10.png)

### 4.4. Khởi chạy API Gateway và sinh token

Trước khi chạy Gateway, em dừng Web UI của scanner để giải phóng cổng `5000`. Sau đó chạy:

```powershell
..\.venv\Scripts\python.exe main.py
```

Chương trình sinh access token và refresh token cho user `nguyen`, sau đó khởi chạy API Gateway tại `http://127.0.0.1:5000/`.

| Thuộc tính | Access token | Refresh token |
| --- | --- | --- |
| Thuật toán | HS256 | HS256 |
| User (`sub`) | `nguyen` | `nguyen` |
| Loại (`type`) | `access` | `refresh` |
| Thời hạn | 15 phút | 24 giờ |

Access token được dùng để truy cập endpoint `/protected`. Refresh token được dùng cho chức năng làm mới access token. Trong ảnh minh chứng, chuỗi token được che bớt; thông tin bên trong token vẫn được lưu để đối chiếu.

![Hình 11. Khởi chạy API Gateway và sinh token mẫu](evidence/screenshots/lab04-11.png)

### 4.5. Gửi request với JWT hợp lệ

Em sử dụng access token vừa được `main.py` sinh ra để gửi request đến `/protected`. Cú pháp lệnh như sau, trong đó `<access_token>` được thay bằng token của lần chạy:

```powershell
curl.exe -sS -i -H "Authorization: Bearer <access_token>" http://127.0.0.1:5000/protected
```

API trả về:

```http
HTTP/1.1 200 OK
Content-Type: application/json

{"message":"Access granted","user":"nguyen"}
```

Mã `200 OK` và thông báo `Access granted` cho thấy Gateway chấp nhận access token hợp lệ. Giá trị `user` trong phản hồi cũng khớp với user được dùng khi sinh token.

![Hình 12. Request với JWT hợp lệ](evidence/screenshots/lab04-12.png)

### 4.6. Gửi request với JWT không hợp lệ

Tiếp theo, em thử hai trường hợp: sửa một ký tự trong phần chữ ký của access token và sử dụng chuỗi `invalid` làm token. Lệnh thử token sai định dạng:

```powershell
curl.exe -sS -i -H "Authorization: Bearer invalid" http://127.0.0.1:5000/protected
```

Cả hai trường hợp đều nhận được phản hồi:

```http
HTTP/1.1 401 UNAUTHORIZED
Content-Type: application/json

{"message":"Access denied"}
```

Kết quả cho thấy Gateway từ chối token có chữ ký sai hoặc không đúng định dạng. Ngoài ra, khi dùng refresh token để gọi `/protected` hoặc gửi request không có header Authorization, API cũng trả về `401`.

![Hình 13. Request với JWT không hợp lệ](evidence/screenshots/lab04-13.png)

## 5. Tổng hợp kết quả thực hành

| Nội dung kiểm tra | Kết quả |
| --- | --- |
| Cài thư viện cho hai dự án | Thành công |
| Unittest của WebVulnScanner | 10/10 test đạt |
| Chạy `main.py` của scanner | Xuất báo cáo mẫu thành công |
| Chạy Flask Web UI | Giao diện hoạt động, gửi form quét thành công |
| Quét trang web mẫu | Hiển thị 2 dấu hiệu XSS, 1 SQL Injection, 1 CSRF và 1 SSRF |
| Pytest của JWTSecure | 12/12 test đạt, có 4 cảnh báo độ dài khóa |
| Sinh access token và refresh token | Thành công |
| Request với access token hợp lệ | HTTP 200 - Access granted |
| Request với token sai chữ ký hoặc sai định dạng | HTTP 401 - Access denied |
| Request với refresh token hoặc thiếu Authorization | HTTP 401 - Access denied |

## 6. Nhận xét và kết luận

Qua quá trình thực hành, em thấy việc chia chương trình thành các module giúp kiểm tra từng chức năng dễ hơn. Bộ unittest và pytest giúp đối chiếu kết quả xử lý với các trường hợp đã chuẩn bị. Khi chạy thêm Web UI và gửi request đến Gateway, em có thể quan sát cách các chức năng hoạt động qua HTTP.

Ở phần WebVulnScanner, chương trình đã hiển thị được các dấu hiệu nghi vấn và tổng hợp thành báo cáo. Tuy nhiên, một số phép kiểm tra còn đơn giản, đặc biệt là việc nhận diện SQL Injection và SSRF bằng chuỗi trong URL. Kết quả quét cần được xác minh thêm nếu áp dụng trên một hệ thống thực tế.

Ở phần JWTSecure, Gateway xử lý đúng các trường hợp đã thử: cho phép truy cập với access token hợp lệ và từ chối token sai. Bài thực hành cũng cho thấy cần phân biệt mục đích sử dụng của access token và refresh token. Khóa JWT trong dự án là khóa demo; chức năng thu hồi refresh token hiện lưu trong bộ nhớ của tiến trình.

Các nội dung kiểm thử trong báo cáo đã hoàn thành, kèm 13 ảnh minh chứng và log kết quả. Phạm vi báo cáo gồm phần 4.2 và 4.4; bước commit và push repository chưa được thực hiện.

## 7. Tệp minh chứng

Ảnh được lưu trong `evidence/screenshots/`, từ `lab04-01.png` đến `lab04-13.png`. Hình 6 và 7 chụp trực tiếp từ giao diện Flask; các hình còn lại chụp trang hiển thị cấu trúc thư mục hoặc log của lần chạy thực tế.

Các log chính để đối chiếu:

- [Kết quả unittest](evidence/logs/03-unittest.txt)
- [Kết quả main.py của scanner](evidence/logs/04-main.txt)
- [Log khởi chạy Flask](evidence/logs/05-flask.txt)
- [Nội dung báo cáo quét](evidence/logs/07-web-report.txt)
- [Kết quả pytest](evidence/logs/10-pytest.txt)
- [Log Gateway và token mẫu](evidence/logs/11-gateway.txt)
- [Request với JWT hợp lệ](evidence/logs/12-valid-jwt.txt)
- [Request với JWT sai chữ ký](evidence/logs/13-invalid-jwt.txt)
- [Request với JWT sai định dạng](evidence/logs/13b-malformed-jwt.txt)
- [Danh sách thư viện đã cài](evidence/logs/environment.txt)
