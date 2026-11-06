"""
Unit tests for SecureLogger, PIIMasker, and Tamper Detection
"""

import json
import os
import pytest
from securelogger.logger import SecureLogger, LogLevel, PIIMasker


@pytest.fixture
def temp_log_file(tmp_path):
    return str(tmp_path / "test_secure.log")


class TestPIIMasker:
    def test_email_masking(self):
        text = "Contact user at admin@example.com for assistance"
        masked = PIIMasker.mask_text(text)
        assert "admin@example.com" not in masked
        assert "a***@example.com" in masked

    def test_phone_masking(self):
        text = "Customer phone number is 0912345678 or +84987654321"
        masked = PIIMasker.mask_text(text)
        assert "0912345678" not in masked
        assert "091****678" in masked

    def test_credit_card_masking(self):
        text = "Payment card: 4111-2222-3333-4444 approved"
        masked = PIIMasker.mask_text(text)
        assert "4111-2222-3333-4444" not in masked
        assert "****-****-****-4444" in masked

    def test_cccd_masking(self):
        text = "Citizen ID is 079123456789 verified"
        masked = PIIMasker.mask_text(text)
        assert "079123456789" not in masked
        assert "079******789" in masked

    def test_structured_extra_masking(self):
        data = {
            "username": "john_doe",
            "password": "SuperSecretP@ssword",
            "token": "ghp_1234567890abcdef",
            "details": {
                "email": "john@test.com",
                "nested_secret": "my_api_key_secret",
            },
        }
        masked = PIIMasker.mask_data(data)
        assert masked["username"] == "john_doe"
        assert masked["password"] == "********"
        assert masked["token"] == "********"
        assert masked["details"]["nested_secret"] == "********"
        assert masked["details"]["email"] == "j***@test.com"


class TestSecureLogger:
    def test_log_levels_and_threshold(self, temp_log_file):
        logger = SecureLogger(
            name="TestLogger",
            log_file=temp_log_file,
            min_level=LogLevel.INFO,
            console_output=False,
        )

        logger.debug("This is a debug message - should be filtered")
        logger.info("This is an info message")
        logger.warning("This is a warning message")
        logger.error("This is an error message")
        logger.critical("This is a critical message")

        with open(temp_log_file, "r", encoding="utf-8") as f:
            lines = [json.loads(line) for line in f if line.strip()]

        assert len(lines) == 4
        levels = [l["level"] for l in lines]
        assert LogLevel.DEBUG not in levels
        assert levels == [LogLevel.INFO, LogLevel.WARNING, LogLevel.ERROR, LogLevel.CRITICAL]

    def test_json_structure_and_pii_in_logger(self, temp_log_file):
        logger = SecureLogger(
            name="BankService",
            log_file=temp_log_file,
            console_output=False,
        )

        logger.info(
            "User payment processed for user@bank.com",
            card="5555 4444 3333 2222",
            phone="0901234567",
        )

        with open(temp_log_file, "r", encoding="utf-8") as f:
            record = json.loads(f.readline())

        assert record["seq"] == 1
        assert "timestamp" in record
        assert record["level"] == LogLevel.INFO
        assert "u***@bank.com" in record["message"]
        assert record["extra"]["card"] == "********"  # card is sensitive key
        assert "090****567" in record["extra"]["phone"]
        assert record["prev_hash"] == SecureLogger.GENESIS_HASH
        assert len(record["entry_hash"]) == 64


class TestTamperDetection:
    def test_valid_chain_integrity(self, temp_log_file):
        logger = SecureLogger(
            name="AuditLogger",
            log_file=temp_log_file,
            console_output=False,
        )

        for i in range(5):
            logger.info(f"Transaction step {i}")

        is_valid, errors = SecureLogger.verify_log_integrity(temp_log_file)
        assert is_valid is True
        assert len(errors) == 0

    def test_tamper_detection_message_modified(self, temp_log_file):
        logger = SecureLogger(
            name="AuditLogger",
            log_file=temp_log_file,
            console_output=False,
        )

        logger.info("Transfer 100 USD to Bob")
        logger.info("Transfer 200 USD to Charlie")

        # Kẻ tấn công sửa nội dung file log: đổi 100 USD thành 9999 USD
        with open(temp_log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        record = json.loads(lines[0])
        record["message"] = "Transfer 9999 USD to Bob"  # Sửa đổi trái phép
        lines[0] = json.dumps(record) + "\n"

        with open(temp_log_file, "w", encoding="utf-8") as f:
            f.writelines(lines)

        is_valid, errors = SecureLogger.verify_log_integrity(temp_log_file)
        assert is_valid is False
        assert any("DỮ LIỆU BỊ GIẢ MẠO" in err for err in errors)

    def test_tamper_detection_line_deleted(self, temp_log_file):
        logger = SecureLogger(
            name="AuditLogger",
            log_file=temp_log_file,
            console_output=False,
        )

        logger.info("Event 1")
        logger.info("Event 2 - Sensitive action")
        logger.info("Event 3")

        # Kẻ tấn công xoá dòng 2 để phi tang dấu vết
        with open(temp_log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        del lines[1]

        with open(temp_log_file, "w", encoding="utf-8") as f:
            f.writelines(lines)

        is_valid, errors = SecureLogger.verify_log_integrity(temp_log_file)
        assert is_valid is False
        assert any("Chuỗi liên kết bị gãy" in err or "Sai số thứ tự sequence" in err for err in errors)

    def test_hmac_secret_key_verification(self, temp_log_file):
        secret = "super_secure_hmac_key_2026"
        logger = SecureLogger(
            name="HmacLogger",
            log_file=temp_log_file,
            secret_key=secret,
            console_output=False,
        )

        logger.info("Authenticated event")

        # Xác thực với đúng key -> Thành công
        is_valid, errors = SecureLogger.verify_log_integrity(temp_log_file, secret_key=secret)
        assert is_valid is True

        # Xác thực với sai key -> Phát hiện giả mạo
        is_valid_wrong, errors_wrong = SecureLogger.verify_log_integrity(temp_log_file, secret_key="wrong_key")  # nosec
        assert is_valid_wrong is False
