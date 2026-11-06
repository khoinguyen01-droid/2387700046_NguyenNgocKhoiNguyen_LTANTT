"""
Core Security Module: SecureValidator
Cung cấp các hàm kiểm tra và làm sạch dữ liệu đầu vào (Input Validation & Sanitization)
nhằm ngăn chặn các lỗ hổng bảo mật phổ biến: Injection, SSRF, Path Traversal, XSS.
"""

import ipaddress
import os
import re
import socket
import urllib.parse
from typing import Iterable, Optional, Set

try:
    import bleach
    BLEACH_AVAILABLE = True
except ImportError:
    BLEACH_AVAILABLE = False
    import html


class SecureValidator:
    """
    Lớp cung cấp các phương thức xác thực và làm sạch dữ liệu đầu vào.
    """

    # RFC 5322 regex đơn giản hoá nhưng chặt chẽ, kiểm tra cú pháp email hợp lệ
    _EMAIL_REGEX = re.compile(
        r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)+$"
    )

    # Whitelist ký tự an toàn cho tên file (chỉ chữ cái, số, gạch dưới, gạch ngang, dấu chấm)
    _SAFE_FILENAME_REGEX = re.compile(r"^[a-zA-Z0-9_\-\.]+$")

    # Các tên thiết bị đặc biệt trên Windows cần cấm
    _WINDOWS_RESERVED_NAMES = {
        "CON", "PRN", "AUX", "NUL",
        *(f"COM{i}" for i in range(1, 10)),
        *(f"LPT{i}" for i in range(1, 10)),
    }

    # Whitelist thẻ HTML và thuộc tính an toàn mặc định cho chống XSS
    DEFAULT_ALLOWED_TAGS = [
        "a", "b", "i", "u", "em", "strong", "p", "br",
        "ul", "ol", "li", "code", "pre", "blockquote", "span"
    ]
    DEFAULT_ALLOWED_ATTRIBUTES = {
        "a": ["href", "title", "target", "rel"],
        "span": ["class"],
    }
    DEFAULT_ALLOWED_PROTOCOLS = ["http", "https", "mailto"]

    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Kiểm tra định dạng email hợp lệ và phòng chống Email Header Injection.

        Nguyên tắc bảo mật:
        1. Kiểm tra kiểu dữ liệu và độ dài (tối đa 254 ký tự theo RFC 5321).
        2. Chống Email Injection: Nghiêm cấm ký tự xuống dòng (CRLF: \r, \n) và null byte (\0)
           để ngăn chặn kẻ tấn công chèn thêm header (CC, BCC, Subject...).
        3. Kiểm tra định dạng theo chuẩn RFC 5322 bằng Regex.

        :param email: Chuỗi email cần kiểm tra.
        :return: True nếu email hợp lệ và an toàn, False nếu không hợp lệ.
        """
        if not isinstance(email, str):
            return False

        email = email.strip()
        if not email or len(email) > 254:
            return False

        # Chống Header Injection: cấm tuyệt đối \r, \n, \0 và các ký tự điều khiển ASCII
        if any(ord(char) < 32 or ord(char) == 127 for char in email):
            return False

        # Kiểm tra độ dài phần local-part (trước dấu @) tối đa 64 ký tự
        if "@" not in email:
            return False
        parts = email.split("@")
        if len(parts) != 2:
            return False

        local_part, domain_part = parts
        if not local_part or len(local_part) > 64 or not domain_part:
            return False

        # Không cho phép 2 dấu chấm liên tiếp
        if ".." in email:
            return False

        return bool(SecureValidator._EMAIL_REGEX.match(email))

    @staticmethod
    def validate_url(url: str, allowed_schemes: Optional[Iterable[str]] = None) -> bool:
        """
        Kiểm tra tính hợp lệ của URL và phòng chống SSRF (Server-Side Request Forgery).

        Nguyên tắc bảo mật:
        1. Chỉ cho phép các giao thức an toàn trong whitelist (mặc định: http, https).
           Cấm các scheme nguy hiểm: file://, gopher://, dict://, ftp://, ldap://, data://...
        2. Phân tích hostname và giải quyết phân giải DNS.
        3. Chặn các dải IP nội bộ, loopback, link-local (cloud metadata 169.254.169.254),
           multicast và reserved IP để chống SSRF.

        :param url: URL cần kiểm tra.
        :param allowed_schemes: Danh sách các scheme cho phép (mặc định: http, https).
        :return: True nếu URL an toàn để truy cập, False nếu nguy hiểm hoặc không hợp lệ.
        """
        if not isinstance(url, str):
            return False

        url = url.strip()
        if not url:
            return False

        if allowed_schemes is None:
            allowed_schemes = {"http", "https"}
        else:
            allowed_schemes = {s.lower() for s in allowed_schemes}

        try:
            parsed = urllib.parse.urlparse(url)
        except Exception:
            return False

        # 1. Kiểm tra scheme
        if not parsed.scheme or parsed.scheme.lower() not in allowed_schemes:
            return False

        hostname = parsed.hostname
        if not hostname:
            return False

        # Chống injection qua thông tin username/password trong authority
        if parsed.username or parsed.password:
            return False

        # 2. Phân giải DNS và kiểm tra địa chỉ IP
        try:
            # Lấy tất cả địa chỉ IP (cả IPv4 lẫn IPv6) ứng với hostname
            addr_info = socket.getaddrinfo(hostname, None)
        except (socket.gaierror, socket.herror, OSError):
            # Không thể phân giải DNS hoặc hostname không tồn tại
            return False

        resolved_ips: Set[str] = {info[4][0] for info in addr_info}

        for ip_str in resolved_ips:
            try:
                ip = ipaddress.ip_address(ip_str)
            except ValueError:
                return False

            # Kiểm tra địa chỉ có nằm trong dải nguy hiểm không:
            # - is_private: 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16, fc00::/7
            # - is_loopback: 127.0.0.0/8, ::1
            # - is_link_local: 169.254.0.0/16 (AWS/GCP metadata service), fe80::/10
            # - is_multicast: 224.0.0.0/4, ff00::/8
            # - is_reserved: IETF reserved
            # - is_unspecified: 0.0.0.0, ::
            if (
                ip.is_private
                or ip.is_loopback
                or ip.is_link_local
                or ip.is_multicast
                or ip.is_reserved
                or ip.is_unspecified
            ):
                return False

        return True

    @staticmethod
    def validate_filename(
        filename: str,
        allowed_extensions: Optional[Iterable[str]] = None
    ) -> bool:
        """
        Kiểm tra tên file để ngăn chặn tấn công Path Traversal / Directory Traversal.

        Nguyên tắc bảo mật:
        1. Cấm chuỗi di chuyển thư mục ('..', '/', '\\').
        2. Cấm Null Byte Injection (\x00, %00).
        3. Cấm đường dẫn tuyệt đối hoặc tên thiết bị đặc biệt trên Windows (CON, PRN...).
        4. Áp dụng Whitelist ký tự cho tên file.
        5. Kiểm tra phần mở rộng (extension) nếu được cấu hình.

        :param filename: Tên file cần kiểm tra.
        :param allowed_extensions: Danh sách đuôi mở rộng cho phép (vd: ['.jpg', '.png', '.pdf']).
        :return: True nếu tên file an toàn, False nếu chứa nguy cơ Path Traversal.
        """
        if not isinstance(filename, str):
            return False

        filename = filename.strip()
        if not filename:
            return False

        # 1. Chống Null Byte Injection
        if "\x00" in filename or "%00" in filename:
            return False

        # 2. Chống Path Traversal: không cho phép '/', '\\', hoặc chuỗi '..'
        if "/" in filename or "\\" in filename or ".." in filename:
            return False

        # Đảm bảo filename thuần túy là basename
        if os.path.basename(filename) != filename:
            return False

        # 3. Chống các tên file ẩn bắt đầu bằng dấu chấm hoặc kết thúc bằng dấu chấm/khoảng trắng
        if filename.startswith(".") or filename.endswith("."):
            return False

        # 4. Kiểm tra thiết bị bảo lưu trên Windows
        base_name_without_ext = os.path.splitext(filename)[0].upper()
        if base_name_without_ext in SecureValidator._WINDOWS_RESERVED_NAMES:
            return False

        # 5. Kiểm tra ký tự an toàn theo Whitelist
        if not SecureValidator._SAFE_FILENAME_REGEX.match(filename):
            return False

        # 6. Kiểm tra đuôi file (nếu có yêu cầu)
        if allowed_extensions is not None:
            normalized_exts = {
                ext.lower() if ext.startswith(".") else f".{ext.lower()}"
                for ext in allowed_extensions
            }
            _, ext = os.path.splitext(filename)
            if ext.lower() not in normalized_exts:
                return False

        return True

    @staticmethod
    def sanitize_sql_input(input_str: str) -> str:
        """
        Làm sạch dữ liệu đầu vào để giảm thiểu nguy cơ SQL Injection.

        LƯU Ý QUAN TRỌNG VỀ BẢO MẬT:
        Giải pháp chuẩn mực và an toàn tuyệt đối nhất chống SQL Injection luôn là
        sử dụng PARAMETERIZED QUERIES (Prepared Statements / ORM).
        Hàm này đóng vai trò phòng vệ theo chiều sâu (Defense-in-Depth) trong trường hợp
        cần tiền xử lý chuỗi trước khi ghi nhận hoặc hiển thị.

        Cơ chế làm sạch:
        - Loại bỏ ký tự Null Byte (\x00, \x1a).
        - Thoát (escape) dấu nháy đơn (') thành ('').
        - Loại bỏ các ký tự kết thúc câu lệnh hoặc chú thích SQL (;, --, /*, */).
        - Thoát dấu gạch chéo ngược (\\).

        :param input_str: Chuỗi đầu vào từ người dùng.
        :return: Chuỗi đã được làm sạch an toàn.
        """
        if not isinstance(input_str, str):
            raise TypeError("Input phải là chuỗi ký tự (str).")

        # 1. Loại bỏ Null Bytes
        sanitized = input_str.replace("\x00", "").replace("\x1a", "")

        # 2. Loại bỏ các cú pháp chú thích SQL nguy hiểm
        sanitized = re.sub(r"--+", "", sanitized)  # Chú thích đơn dòng --
        sanitized = re.sub(r"/\*.*?\*/", "", sanitized, flags=re.DOTALL)  # Chú thích khối /* */

        # 3. Loại bỏ dấu chấm phẩy ; để ngăn chặn xếp chồng câu lệnh (Stacked Queries)
        sanitized = sanitized.replace(";", "")

        # 4. Escape dấu nháy đơn và backslash
        sanitized = sanitized.replace("\\", "\\\\")
        sanitized = sanitized.replace("'", "''")

        return sanitized.strip()

    @staticmethod
    def sanitize_html_input(
        html_str: str,
        allowed_tags: Optional[Iterable[str]] = None,
        allowed_attributes: Optional[dict] = None
    ) -> str:
        """
        Làm sạch dữ liệu HTML để phòng chống tấn công XSS (Cross-Site Scripting).

        Sử dụng thư viện bảo mật chuyên dụng Bleach (dựa trên chuẩn HTML5lib) để phân tích
        và làm sạch mã HTML, loại bỏ tất cả các thẻ nguy hiểm (<script>, <iframe>, <object>,
        <embed>, <svg>...) và các trình xử lý sự kiện nguy hiểm (onload, onerror, onclick...).

        Nếu môi trường chưa cài đặt bleach, hàm sẽ fallback sang html.escape() để đảm bảo
        an toàn tối đa.

        :param html_str: Đoạn mã HTML cần làm sạch.
        :param allowed_tags: Danh sách các thẻ HTML được phép.
        :param allowed_attributes: Dict các thuộc tính được phép cho từng thẻ.
        :return: Đoạn mã HTML an toàn đã được làm sạch.
        """
        if not isinstance(html_str, str):
            raise TypeError("Input phải là chuỗi ký tự (str).")

        # Loại bỏ hoàn toàn các khối thẻ nguy hiểm kèm nội dung bên trong như <script> và <style>
        sanitized = re.sub(
            r"<(script|style|iframe|object|embed)[^>]*>.*?</\1>",
            "",
            html_str,
            flags=re.IGNORECASE | re.DOTALL,
        )

        tags = list(allowed_tags) if allowed_tags is not None else SecureValidator.DEFAULT_ALLOWED_TAGS
        attrs = allowed_attributes if allowed_attributes is not None else SecureValidator.DEFAULT_ALLOWED_ATTRIBUTES

        if BLEACH_AVAILABLE:
            cleaned = bleach.clean(
                sanitized,
                tags=tags,
                attributes=attrs,
                protocols=SecureValidator.DEFAULT_ALLOWED_PROTOCOLS,
                strip=True,  # Loại bỏ thẻ không được phép thay vì escape
                strip_comments=True,
            )
            return cleaned
        else:
            # Fallback an toàn nếu không có bleach
            return html.escape(sanitized)


# Alias các hàm ở mức module để người dùng có thể import trực tiếp
validate_email = SecureValidator.validate_email
validate_url = SecureValidator.validate_url
validate_filename = SecureValidator.validate_filename
sanitize_sql_input = SecureValidator.sanitize_sql_input
sanitize_html_input = SecureValidator.sanitize_html_input
