#!/usr/bin/env python3
"""Storage helper utilities for Claw Office backend.

JSON load/save for agents state, asset positions/defaults, runtime config, and join keys.
"""

from __future__ import annotations

import json
import os


def _load_json(path: str):
    """Load JSON from a file; caller handles missing file or parse errors."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_json(path: str, data):
    """Write data as JSON with UTF-8 and indent=2."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_agents_state(path: str, default_agents: list) -> list:
    """Load agents list from path; return default_agents if file missing or invalid."""
    if os.path.exists(path):
        try:
            data = _load_json(path)
            if isinstance(data, list):
                return data
        except Exception:
            pass
    return list(default_agents)


def save_agents_state(path: str, agents: list):
    """Persist agents list to path."""
    _save_json(path, agents)


def load_asset_positions(path: str) -> dict:
    """Load asset positions map from path; return {} if missing or invalid."""
    if os.path.exists(path):
        try:
            data = _load_json(path)
            if isinstance(data, dict):
                return data
        except Exception:
            pass
    return {}


def save_asset_positions(path: str, data: dict):
    """Persist asset positions to path."""
    _save_json(path, data)


def load_asset_defaults(path: str) -> dict:
    """Load asset defaults map from path; return {} if missing or invalid."""
    if os.path.exists(path):
        try:
            data = _load_json(path)
            if isinstance(data, dict):
                return data
        except Exception:
            pass
    return {}


def save_asset_defaults(path: str, data: dict):
    """Persist asset defaults to path."""
    _save_json(path, data)


def _normalize_user_model(model_name: str) -> str:
    """Map provider model names to canonical user-facing options (nanobanana-pro / nanobanana-2)."""
    m = (model_name or "").strip().lower()
    if m in {"nanobanana-pro", "nanobanana-2"}:
        return m
    if m in {"nano-banana-pro-preview", "gemini-3-pro-image-preview"}:
        return "nanobanana-pro"
    if m in {"gemini-2.5-flash-image", "gemini-2.0-flash-exp-image-generation"}:
        return "nanobanana-2"
    return "nanobanana-pro"


def load_runtime_config(path: str) -> dict:
    """Load runtime config (gemini_api_key, gemini_model) from env and optional JSON file."""
    base = {
        "gemini_api_key": os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or "",
        "gemini_model": _normalize_user_model(os.getenv("GEMINI_MODEL") or "nanobanana-pro"),
    }
    if os.path.exists(path):
        try:
            data = _load_json(path)
            if isinstance(data, dict):
                base.update({k: data.get(k, base.get(k)) for k in ["gemini_api_key", "gemini_model"]})
                base["gemini_model"] = _normalize_user_model(base.get("gemini_model") or "nanobanana-pro")
        except Exception:
            pass
    return base


def save_runtime_config(path: str, data: dict):
    """Merge data into current runtime config and save to path; chmod 0o600 on path."""
    cfg = load_runtime_config(path)
    cfg.update(data or {})
    _save_json(path, cfg)
    try:
        os.chmod(path, 0o600)
    except Exception:
        pass


def load_join_keys(path: str) -> dict:
    """Load join keys structure from path; return {'keys': []} if missing or invalid."""
    if os.path.exists(path):
        try:
            data = _load_json(path)
            if isinstance(data, dict) and isinstance(data.get("keys"), list):
                return data
        except Exception:
            pass
    return {"keys": []}


def save_join_keys(path: str, data: dict):
    """Persist join keys to path."""
    _save_json(path, data)


# ============================================================================
# Agents Config (预注册 agent 配置，用于 HMAC 认证)
# ============================================================================

DEFAULT_AGENTS_CONFIG = {
    "agents": [],
    "defaults": {},
    "settings": {
        "offlineTimeout": 300,
        "signatureExpireSeconds": 60,
    }
}


def load_agents_config(path: str) -> dict:
    """Load agents config from path; return default structure if missing or invalid.

    Agents config contains:
    - agents: list of pre-registered agents with id, name, secretKey (optional), avatar
    - defaults: shared config (secretKey, avatar) inherited by all agents
    - settings: timeout and security settings
    """
    if os.path.exists(path):
        try:
            data = _load_json(path)
            if isinstance(data, dict):
                # 确保必要的字段存在
                if "agents" not in data:
                    data["agents"] = []
                if "defaults" not in data:
                    data["defaults"] = {}
                if "settings" not in data:
                    data["settings"] = DEFAULT_AGENTS_CONFIG["settings"]
                return data
        except Exception:
            pass
    return dict(DEFAULT_AGENTS_CONFIG)


def save_agents_config(path: str, data: dict):
    """Persist agents config to path; chmod 0o600 for security."""
    _save_json(path, data)
    try:
        os.chmod(path, 0o600)
    except Exception:
        pass


def find_agent_by_id(config: dict, agent_id: str) -> dict | None:
    """Find agent config by agentId, merging with defaults.

    Args:
        config: agents config dict (with agents, defaults, settings)
        agent_id: agent ID to find

    Returns:
        Merged agent config dict (defaults + agent-specific) or None if not found
    """
    defaults = config.get("defaults", {})
    for agent in config.get("agents", []):
        if agent.get("agentId") == agent_id:
            # 合并: defaults 作为基础，agent 特定配置覆盖
            merged = dict(defaults)
            merged.update(agent)
            return merged
    return None
