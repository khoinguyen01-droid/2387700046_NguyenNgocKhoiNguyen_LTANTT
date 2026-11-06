from securelogger.logger import SecureLogger
import os

log_filename = "app_test.log"

print("=== 1. KHỞI TẠO VÀ GHI LOG CÓ CHỨA THÔNG TIN PII ===")
logger = SecureLogger(log_filename)
logger.info("User login successfully with phone 0912345678 and email khoi.nguyen@gmail.com")
logger.warning("Warning: Failed login attempt from IP 192.168.1.50")
logger.error("Error: Database timeout encountered.")

print("Đã ghi log thành công!")

print("\n=== 2. KIỂM TRA TÍNH TOÀN VẸN BAN ĐẦU ===")
# Lấy chính xác đường dẫn file log mà đối tượng logger đang thực sự ghi
actual_log_file = logger.log_file if hasattr(logger, 'log_file') else log_filename
print("Trạng thái toàn vẹn log trước khi bị sửa:", logger.verify_log_integrity(actual_log_file))

print("\n=== 3. GIẢ LẬP KẺ GIAN CHỈNH SỬA LOG TRÁI PHÉP (TAMPERING) ===")
if os.path.exists(actual_log_file):
    # Đọc nội dung file log thực tế
    with open(actual_log_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Giả lập sửa đổi một ký tự trong nội dung log
    tampered_content = content.replace("0912345678", "0919999999")
    with open(actual_log_file, "w", encoding="utf-8") as f:
        f.write(tampered_content)

    print(f"Đã cố tình thay đổi dữ liệu bên trong file '{actual_log_file}'...")
    
    # Kiểm tra lại tính toàn vẹn sau khi bị chỉnh sửa (Lúc này phải trả về False kèm danh sách lỗi)
    print("Trạng thái toàn vẹn log sau khi bị sửa:", logger.verify_log_integrity(actual_log_file))
else:
    print(f"Không tìm thấy file log tại: {actual_log_file}")