"""
Secure Logging Module: SecureLogger
Cung cấp hệ thống ghi log bảo mật cao tuân thủ các tiêu chuẩn an toàn thông tin:
1. Đa cấp độ log (DEBUG, INFO, WARNING, ERROR, CRITICAL).
2. Tự động phát hiện và che giấu thông tin định danh cá nhân (PII Masking).
3. Định dạng có cấu trúc JSON (JSON Lines).
4. Cơ chế chống giả mạo nhật ký (Tamper Detection qua Cryptographic Hash Chaining / HMAC-SHA256).
"""

import datetime
import hashlib
import hmac
import json
import os
import re
import threading
from typing import Any, Dict, List, Optional, Tuple, Union


class PIIMasker:
    """
    Module phụ trợ nhận diện và che giấu thông tin định danh cá nhân (PII)
    trong chuỗi văn bản và dữ liệu có cấu trúc.
    """

    # Email regex
    _EMAIL_REGEX = re.compile(
        r"\b([A-Za-z0-9._%+-])[A-Za-z0-9._%+-]*@([A-Za-z0-9.-]+\.[A-Z|a-z]{2,})\b"
    )

    # Thẻ tín dụng: 13 đến 19 chữ số (hỗ trợ dấu gạch ngang hoặc khoảng trắng)
    _CREDIT_CARD_REGEX = re.compile(
        r"\b(?:\d{4}[ -]?){3}(\d{4})\b"
    )

    # Số điện thoại (hỗ trợ định dạng Việt Nam và Quốc tế)
    _PHONE_REGEX = re.compile(
        r"\b((?:\+84|0)[0-9]{2})[0-9]{4}([0-9]{3})\b"
    )

    # Căn cước công dân (12 chữ số) hoặc CMND (9 chữ số)
    _CCCD_REGEX = re.compile(
        r"\b([0-9]{3})[0-9]{3,6}([0-9]{3})\b"
    )

    # Các từ khóa nhạy cảm trong dictionary keys cần che 100%
    _SENSITIVE_KEYS = {
        "password", "passwd", "pwd", "secret", "token", "access_token",
        "api_key", "auth", "authorization", "private_key", "cvv", "credit_card", "card"
    }

    @classmethod
    def mask_text(cls, text: str) -> str:
        """
        Quét và che giấu PII trong một chuỗi văn bản tự do.
        """
        if not isinstance(text, str):
            return text

        # 1. Che giấu Email: user@domain.com -> u***@domain.com
        text = cls._EMAIL_REGEX.sub(r"\1***@\2", text)

        # 2. Che giấu thẻ tín dụng: 1234-5678-9012-3456 -> ****-****-****-3456
        text = cls._CREDIT_CARD_REGEX.sub(r"****-****-****-\1", text)

        # 3. Che giấu số điện thoại: 0912345678 -> 091****678
        text = cls._PHONE_REGEX.sub(r"\1****\2", text)

        # 4. Che giấu CCCD: 079123456789 -> 079******789
        # Chỉ che nếu từ khoá lân cận gợi ý số định danh hoặc đúng 12 chữ số
        def _mask_cccd(match):
            val = match.group(0)
            if len(val) in (9, 12):
                return val[:3] + "*" * (len(val) - 6) + val[-3:]
            return val

        text = re.sub(r"\b\d{12}\b|\b\d{9}\b", _mask_cccd, text)

        return text

    @classmethod
    def mask_data(cls, data: Any) -> Any:
        """
        Đệ quy che giấu PII trong dict, list hoặc kiểu dữ liệu nguyên thuỷ.
        """
        if isinstance(data, dict):
            masked_dict = {}
            for k, v in data.items():
                k_lower = str(k).lower()
                if any(sens in k_lower for sens in cls._SENSITIVE_KEYS):
                    masked_dict[k] = "********"
                else:
                    masked_dict[k] = cls.mask_data(v)
            return masked_dict
        elif isinstance(data, list):
            return [cls.mask_data(item) for item in data]
        elif isinstance(data, tuple):
            return tuple(cls.mask_data(item) for item in data)
        elif isinstance(data, str):
            return cls.mask_text(data)
        return data


class LogLevel:
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

    _PRIORITY = {
        DEBUG: 10,
        INFO: 20,
        WARNING: 30,
        ERROR: 40,
        CRITICAL: 50,
    }

    @classmethod
    def get_priority(cls, level: str) -> int:
        return cls._PRIORITY.get(level.upper(), 20)


class SecureLogger:
    """
    Hệ thống ghi nhật ký bảo mật với JSON Lines và chuỗi băm chống giả mạo (Hash Chaining).
    """

    GENESIS_HASH = "0" * 64

    def __init__(
        self,
        name: str = "SecureLogger",
        log_file: Optional[str] = "app_secure.log",
        min_level: str = LogLevel.INFO,
        secret_key: Optional[str] = None,
        console_output: bool = True,
    ):
        """
        Khởi tạo SecureLogger.

        :param name: Tên của logger.
        :param log_file: Đường dẫn tới file lưu trữ JSON logs. Nếu None, chỉ ghi ra console.
        :param min_level: Cấp độ log tối thiểu (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        :param secret_key: Khóa bí mật dùng cho HMAC-SHA256 (Tamper Detection).
                           Nếu None, sử dụng mã băm tiêu chuẩn SHA-256.
        :param console_output: Có hiển thị ra màn hình terminal không.
        """
        self.name = name
        self.log_file = log_file
        self.min_level = min_level.upper()
        self.secret_key = secret_key
        self.console_output = console_output

        self._lock = threading.Lock()
        self._sequence_number = 0
        self._last_hash = self.GENESIS_HASH

        # Khôi phục trạng thái chuỗi băm từ file cũ nếu file đã tồn tại
        if self.log_file and os.path.exists(self.log_file):
            self._recover_last_state()

    def _recover_last_state(self):
        """Đọc dòng cuối cùng của log file để tiếp tục chuỗi băm mà không làm gãy chuỗi."""
        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f if line.strip()]
                if lines:
                    last_record = json.loads(lines[-1])
                    self._sequence_number = last_record.get("seq", len(lines))
                    self._last_hash = last_record.get("entry_hash", self.GENESIS_HASH)
        except Exception:
            # Nếu file lỗi cú pháp, bắt đầu lại từ Genesis để đảm bảo an toàn
            self._sequence_number = 0
            self._last_hash = self.GENESIS_HASH

    def _calculate_hash(self, entry_payload: Dict[str, Any]) -> str:
        """
        Tính toán mã băm cho bản ghi nhật ký.
        Sử dụng Canonical JSON (sort_keys=True, không khoảng trắng dư) để đảm bảo
        tính xác thực nhất quán.
        """
        canonical_json = json.dumps(entry_payload, sort_keys=True, separators=(",", ":"))
        data_bytes = canonical_json.encode("utf-8")

        if self.secret_key:
            return hmac.new(
                self.secret_key.encode("utf-8"), data_bytes, hashlib.sha256
            ).hexdigest()
        else:
            return hashlib.sha256(data_bytes).hexdigest()

    def _log_record(self, level: str, message: str, extra: Optional[Dict[str, Any]] = None):
        """Xử lý định dạng, che PII, tạo hash chain và lưu trữ bản ghi."""
        if LogLevel.get_priority(level) < LogLevel.get_priority(self.min_level):
            return

        # 1. Che giấu PII trong message và extra data
        safe_message = PIIMasker.mask_text(str(message))
        safe_extra = PIIMasker.mask_data(extra) if extra else {}

        now_utc = datetime.datetime.now(datetime.timezone.utc).isoformat()

        with self._lock:
            self._sequence_number += 1
            seq = self._sequence_number
            prev_hash = self._last_hash

            # Payload trước khi băm (chứa prev_hash để liên kết chuỗi)
            record_payload = {
                "seq": seq,
                "timestamp": now_utc,
                "logger": self.name,
                "level": level,
                "message": safe_message,
                "extra": safe_extra,
                "prev_hash": prev_hash,
            }

            # 2. Tính toán mã băm cho bản ghi (Tamper Detection)
            entry_hash = self._calculate_hash(record_payload)
            record_payload["entry_hash"] = entry_hash

            # Cập nhật state hash hiện tại
            self._last_hash = entry_hash

            # 3. Ghi vào tệp log dưới dạng JSON Lines
            if self.log_file:
                log_dir = os.path.dirname(self.log_file)
                if log_dir:
                    os.makedirs(log_dir, exist_ok=True)
                with open(self.log_file, "a", encoding="utf-8") as f:
                    f.write(json.dumps(record_payload, ensure_ascii=False) + "\n")

        # 4. Hiển thị Console (nếu kích hoạt)
        if self.console_output:
            color = {
                LogLevel.DEBUG: "\033[94m",
                LogLevel.INFO: "\033[92m",
                LogLevel.WARNING: "\033[93m",
                LogLevel.ERROR: "\033[91m",
                LogLevel.CRITICAL: "\033[95m\033[1m",
            }.get(level, "\033[0m")
            reset = "\033[0m"
            print(f"{color}[{now_utc}] [{level}] [{self.name}] {safe_message}{reset}")

    # Các phương thức ghi log theo từng cấp độ
    def debug(self, message: str, **extra):
        self._log_record(LogLevel.DEBUG, message, extra)

    def info(self, message: str, **extra):
        self._log_record(LogLevel.INFO, message, extra)

    def warning(self, message: str, **extra):
        self._log_record(LogLevel.WARNING, message, extra)

    def error(self, message: str, **extra):
        self._log_record(LogLevel.ERROR, message, extra)

    def critical(self, message: str, **extra):
        self._log_record(LogLevel.CRITICAL, message, extra)

    @classmethod
    def verify_log_integrity(
        cls, log_file: str, secret_key: Optional[str] = None
    ) -> Tuple[bool, List[str]]:
        """
        Kiểm tra tính toàn vẹn của tệp nhật ký (Tamper Detection).
        Phát hiện bất kỳ hành vi sửa đổi, thêm bớt hoặc tráo đổi vị trí log.

        :param log_file: Đường dẫn tệp log cần kiểm tra.
        :param secret_key: Khóa bí mật HMAC (nếu khi ghi log có sử dụng).
        :return: (is_valid: bool, errors: List[str])
        """
        if not os.path.exists(log_file):
            return False, [f"Tệp log không tồn tại: {log_file}"]

        errors = []
        expected_prev_hash = cls.GENESIS_HASH
        expected_seq = 1

        with open(log_file, "r", encoding="utf-8") as f:
            for line_idx, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue

                try:
                    record = json.loads(line)
                except json.JSONDecodeError as e:
                    errors.append(f"Dòng {line_idx}: Cú pháp JSON bị hỏng ({str(e)}).")
                    return False, errors

                # 1. Kiểm tra số thứ tự sequence
                seq = record.get("seq")
                if seq != expected_seq:
                    errors.append(
                        f"Dòng {line_idx}: Sai số thứ tự sequence (kỳ vọng {expected_seq}, nhận được {seq})."
                    )

                # 2. Kiểm tra liên kết prev_hash với dòng trước
                prev_hash = record.get("prev_hash")
                if prev_hash != expected_prev_hash:
                    errors.append(
                        f"Dòng {line_idx}: Chuỗi liên kết bị gãy! "
                        f"prev_hash không khớp với entry_hash của dòng trước."
                    )

                # 3. Tính toán lại entry_hash để kiểm tra nội dung có bị sửa đổi không
                entry_hash = record.get("entry_hash")
                payload_to_verify = {
                    "seq": record.get("seq"),
                    "timestamp": record.get("timestamp"),
                    "logger": record.get("logger"),
                    "level": record.get("level"),
                    "message": record.get("message"),
                    "extra": record.get("extra"),
                    "prev_hash": prev_hash,
                }

                canonical_json = json.dumps(
                    payload_to_verify, sort_keys=True, separators=(",", ":")
                )
                data_bytes = canonical_json.encode("utf-8")

                if secret_key:
                    computed_hash = hmac.new(
                        secret_key.encode("utf-8"), data_bytes, hashlib.sha256
                    ).hexdigest()
                else:
                    computed_hash = hashlib.sha256(data_bytes).hexdigest()

                if computed_hash != entry_hash:
                    errors.append(
                        f"Dòng {line_idx}: DỮ LIỆU BỊ GIẢ MẠO! "
                        f"entry_hash trong file không khớp với nội dung thực tế."
                    )

                # Cập nhật kỳ vọng cho dòng tiếp theo
                expected_prev_hash = entry_hash
                expected_seq += 1

        is_valid = len(errors) == 0
        return is_valid, errors
