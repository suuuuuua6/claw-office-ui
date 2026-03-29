#!/usr/bin/env python3
"""HMAC authentication utilities for agent heartbeat."""

import hmac
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Optional, Tuple

# 允许的时间戳偏差（秒）
TIMESTAMP_TOLERANCE_SECONDS = 300  # 5分钟


def generate_signature(secret_key: str, timestamp: str, body: str) -> str:
    """生成 HMAC-SHA256 签名

    Args:
        secret_key: 密钥
        timestamp: ISO 格式时间戳
        body: 请求体字符串

    Returns:
        签名字符串，格式为 "hmac-sha256=<hex>"
    """
    message = f"{timestamp}\n{body}"
    signature = hmac.new(
        secret_key.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return f"hmac-sha256={signature}"


def verify_signature(secret_key: str, timestamp: str, body: str, signature: str) -> bool:
    """验证 HMAC-SHA256 签名

    Args:
        secret_key: 密钥
        timestamp: ISO 格式时间戳
        body: 请求体字符串
        signature: 待验证的签名字符串

    Returns:
        签名是否有效
    """
    expected = generate_signature(secret_key, timestamp, body)
    return hmac.compare_digest(expected, signature)


def verify_timestamp(timestamp_str: str, tolerance_seconds: int = TIMESTAMP_TOLERANCE_SECONDS) -> Tuple[bool, Optional[str]]:
    """验证时间戳是否在允许范围内

    Args:
        timestamp_str: ISO 格式时间戳字符串
        tolerance_seconds: 允许的偏差秒数

    Returns:
        (是否有效, 错误信息)
    """
    try:
        # 支持 Z 和 +00:00 两种格式
        ts = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        now = datetime.now(timezone.utc)
        diff = abs((now - ts).total_seconds())
        if diff > tolerance_seconds:
            return False, f"Timestamp expired (diff={diff:.0f}s, tolerance={tolerance_seconds}s)"
        return True, None
    except Exception as e:
        return False, f"Invalid timestamp format: {e}"


def hash_secret_key(secret_key: str) -> str:
    """对密钥进行 SHA256 哈希

    Args:
        secret_key: 原始密钥

    Returns:
        哈希后的字符串，格式为 "sha256:<hex>"
    """
    return f"sha256:{hashlib.sha256(secret_key.encode('utf-8')).hexdigest()}"


def verify_secret_key_hash(secret_key: str, secret_key_hash: str) -> bool:
    """验证密钥哈希

    Args:
        secret_key: 原始密钥
        secret_key_hash: 存储的密钥哈希

    Returns:
        密钥是否匹配
    """
    if not secret_key_hash.startswith("sha256:"):
        # 兼容直接存储明文密钥的情况（不推荐）
        return hmac.compare_digest(secret_key, secret_key_hash)

    expected_hash = secret_key_hash[7:]  # 去掉 "sha256:" 前缀
    actual_hash = hashlib.sha256(secret_key.encode('utf-8')).hexdigest()
    return hmac.compare_digest(expected_hash, actual_hash)
