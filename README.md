# BÁO CÁO BÀI THỰC HÀNH 05: PHÂN TÍCH VÀ KIỂM THỬ BẢO MẬT

**Họ và tên:** Nguyễn Ngọc Khôi Nguyên
**Mã sinh viên:** 2387700046
**Lớp:** 23DATA1
**Môn học:** Lập trình An ninh Thông tin

---

## PHẦN 1: STATIC ANALYSIS SECURITY TESTING (SAST)

### 1. Kết quả Unit Test
Công cụ SAST đã vượt qua toàn bộ 6 bài kiểm thử tự động (báo `OK`).

![SAST Unit Test](image/1.png)

### 2. Chạy phân tích trên mã nguồn không an toàn
Thực hiện phân tích file `vulnerable_01.py`, phát hiện 8 lỗi bảo mật. Báo cáo được lưu tự động ra file `report.sarif`.

![SAST Run Vulnerable](image/2.png)

### 3. Xem báo cáo kết quả (SARIF Viewer)
Sử dụng extension SARIF Viewer trên VS Code để hiển thị chi tiết danh sách các lỗ hổng bảo mật.

![SAST SARIF Viewer](image/3.png)

---

## PHẦN 2: DYNAMIC ANALYSIS SECURITY TESTING (DAST)

### 1. Kết quả Unit Test
Nền tảng DAST vượt qua toàn bộ 5 bài kiểm thử tự động (báo `OK`).

![DAST Unit Test](image/4.png)

### 2. Chạy giám sát Runtime (main.py)
Chạy kịch bản `main.py` để giám sát tài nguyên, kiểm tra rò rỉ bộ nhớ và lưu lượng mạng.

![DAST Main Run](image/5.png)

### 3. Giám sát qua Flask API (Monitor, Memory, Security, Network)
Khởi chạy server Flask và kiểm thử thành công các API `GET` thông qua trình duyệt.

**API /api/monitor:**
![DAST API Monitor](image/6.png)

**API /api/memory:**
![DAST API Memory](image/7.png)

**API /api/security:**
![DAST API Security](image/8.png)

**API /api/network:**
![DAST API Network](image/9.png)

### 4. Kiểm thử API Sandbox (Sử dụng cURL)
Gửi lệnh POST đến `/api/sandbox` để thực thi lệnh `echo Hello Sandbox` trong môi trường cách ly.

![DAST API Sandbox](image/10.png)

*(Các ảnh từ 11.png đến 15.png có thể là log server hoặc các ảnh bạn chụp thêm, bạn có thể chèn thêm vào bên dưới nếu muốn)*

![Log Server](image/11.png)

---
## KẾT LUẬN
Bài thực hành đã giúp phân biệt rõ ràng giữa SAST (phân tích mã nguồn tĩnh qua AST) và DAST (phân tích hành vi động qua Runtime). Đã xây dựng thành công 2 công cụ nhỏ để tự động hóa việc phát hiện lỗ hổng bảo mật.