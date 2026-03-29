#!/usr/bin/env python3
"""Agent Heartbeat Client - HMAC authenticated status push.

Usage:
  1. Create agent-config.json in your OpenClaw workspace directory
  2. Run this script to start heartbeat

Config file location:
  - Default: ~/.openclaw/workspace/agent-config.json
  - Or set OPENCLAW_WORKSPACE env var

Config file format:
  {
    "agentId": "ling",
    "name": "小绫",
    "secretKey": "your-secret-key-32chars-min",
    "officeUrl": "https://office.yourcompany.com",
    "heartbeatInterval": 15
  }
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

try:
    import urllib.request
    import urllib.error
    HAS_URLLIB = True
except ImportError:
    HAS_URLLIB = False

# 默认配置文件路径
DEFAULT_WORKSPACE = os.path.join(os.path.expanduser("~"), ".openclaw", "workspace")
CONFIG_FILE_ENV = "STAR_OFFICE_AGENT_CONFIG"


def get_config_path() -> str:
    """获取配置文件路径"""
    # 优先使用环境变量
    env_path = os.environ.get(CONFIG_FILE_ENV, "").strip()
    if env_path:
        return env_path

    # 其次使用 OPENCLAW_WORKSPACE
    workspace = os.environ.get("OPENCLAW_WORKSPACE", DEFAULT_WORKSPACE)
    return os.path.join(workspace, "agent-config.json")


def load_config() -> dict:
    """加载配置文件"""
    config_path = get_config_path()
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[ERROR] 加载配置文件失败: {config_path}: {e}")
    return {}


def generate_signature(secret_key: str, timestamp: str, body: str) -> str:
    """生成 HMAC-SHA256 签名"""
    message = f"{timestamp}\n{body}"
    signature = hmac.new(
        secret_key.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return f"hmac-sha256={signature}"


def read_local_state() -> dict:
    """读取本地状态

    优先级：
    1. 环境变量 STAR_OFFICE_STATE_FILE 指向的 state.json
    2. workspace 目录下的 state.json
    3. 默认返回 idle 状态
    """
    # 检查环境变量
    state_file = os.environ.get("STAR_OFFICE_STATE_FILE", "").strip()
    if not state_file:
        workspace = os.environ.get("OPENCLAW_WORKSPACE", DEFAULT_WORKSPACE)
        state_file = os.path.join(workspace, "state.json")

    if os.path.exists(state_file):
        try:
            with open(state_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    return {
        "state": "idle",
        "detail": "",
        "progress": 0
    }


def do_heartbeat(config: dict, state: dict) -> bool:
    """发送心跳请求"""
    agent_id = config.get("agentId", "")
    secret_key = config.get("secretKey", "")
    office_url = config.get("officeUrl", "http://127.0.0.1:19000").rstrip("/")

    if not agent_id or not secret_key:
        print("[ERROR] 配置文件缺少 agentId 或 secretKey")
        return False

    # 准备请求
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    body = json.dumps({
        "state": state.get("state", "idle"),
        "detail": state.get("detail", ""),
        "progress": state.get("progress", 0)
    }, ensure_ascii=False)

    signature = generate_signature(secret_key, timestamp, body)

    headers = {
        "Content-Type": "application/json",
        "X-Agent-Id": agent_id,
        "X-Timestamp": timestamp,
        "X-Signature": signature
    }

    url = f"{office_url}/agent-heartbeat"

    try:
        req = urllib.request.Request(
            url=url,
            data=body.encode("utf-8"),
            headers=headers,
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw = resp.read().decode("utf-8")
            data = json.loads(raw)
            if data.get("ok"):
                print(f"[heartbeat] OK - agent={agent_id} area={data.get('area', '?')}")
                return True
            else:
                print(f"[heartbeat] FAIL - {data.get('msg', 'unknown error')}")
                return False
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8") if hasattr(e, "read") else str(e)
        try:
            err_data = json.loads(raw)
            print(f"[heartbeat] FAIL ({e.code}) - {err_data.get('msg', raw[:100])}")
        except Exception:
            print(f"[heartbeat] FAIL ({e.code}) - {raw[:100]}")
        return False
    except Exception as e:
        print(f"[heartbeat] ERROR - {e}")
        return False


def main():
    print("=" * 50)
    print("Star Office UI - Agent Heartbeat Client")
    print("=" * 50)

    config = load_config()
    if not config:
        config_path = get_config_path()
        print(f"[ERROR] 配置文件不存在或为空: {config_path}")
        print("\n请创建配置文件，格式如下:")
        print(json.dumps({
            "agentId": "your-agent-id",
            "name": "你的名字",
            "secretKey": "your-secret-key-32chars-min",
            "officeUrl": "https://office.yourcompany.com",
            "heartbeatInterval": 15
        }, indent=2, ensure_ascii=False))
        sys.exit(1)

    agent_id = config.get("agentId", "unknown")
    name = config.get("name", "unknown")
    interval = config.get("heartbeatInterval", 15)

    print(f"Agent: {name} ({agent_id})")
    print(f"Office: {config.get('officeUrl', 'http://127.0.0.1:19000')}")
    print(f"Interval: {interval}s")
    print(f"Config: {get_config_path()}")
    print("=" * 50)

    while True:
        state = read_local_state()
        do_heartbeat(config, state)
        time.sleep(interval)


if __name__ == "__main__":
    main()
