# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Claw Office UI is a pixel-art style AI office dashboard that visualizes AI agent work status in real-time. It shows "who is doing what, what was done yesterday, and whether they're online now." Supports multi-agent collaboration, CN/EN/JP trilingual interface, AI-generated room backgrounds, and desktop pet mode.

## Commands

### Backend (Python Flask)

```bash
# Install dependencies (Python 3.10+ required)
python3 -m pip install -r backend/requirements.txt

# Initialize state file (first time only)
cp state.sample.json state.json

# Start the backend server (default port: 19000)
cd backend && python3 app.py

# Or use the run script with venv and .env auto-loading
cd backend && ./run.sh

# Set state via CLI script (from project root)
python3 set_state.py writing "正在整理文档"
python3 set_state.py idle "待命中"

# Run smoke test
python3 scripts/smoke_test.py --base-url http://127.0.0.1:19000
```

### Environment Variables

- `STAR_BACKEND_PORT`: Backend port (default: 19000)
- `FLASK_SECRET_KEY` / `CLAW_OFFICE_SECRET`: Flask session secret (production: must be >=24 chars)
- `ASSET_DRAWER_PASS`: Sidebar password (production: must be >=8 chars, not default "1234")
- `GEMINI_API_KEY`: API key for AI background generation
- `GEMINI_MODEL`: Model for image generation (`nanobanana-pro` or `nanobanana-2`)

### Desktop Pet (Tauri - Recommended)

```bash
cd desktop-pet
npm install
npm run dev     # Development
npm run build   # Production build
```

### Electron Shell (Alternative)

```bash
cd electron-shell
npm install
npm run dev
```

## Architecture

### Backend Structure (`backend/`)

- `app.py`: Main Flask application with all API endpoints, state management, and image generation
- `security_utils.py`: Production mode detection, password strength validation
- `memo_utils.py`: Yesterday memo extraction and content sanitization
- `store_utils.py`: JSON file persistence utilities for agents, assets, and config

### Frontend Structure (`frontend/`)

- `index.html`: Main office UI page
- `join.html`: Agent join page for multi-agent collaboration
- `invite.html`: Human-facing invite instruction page
- `game.js`: Phaser 3 game logic (character movement, state visualization)
- `layout.js`: Layout configuration (game dimensions, positions, asset defaults)
- `vendor/phaser-3.80.1.min.js`: Phaser 3 game engine

### Key Data Files (Project Root)

- `state.json`: Main agent state (state, detail, progress, updated_at)
- `agents-state.json`: Multi-agent state list
- `join-keys.json`: Join keys for guest agents (with maxConcurrent, expiresAt)
- `asset-positions.json`: Custom asset positions set via sidebar
- `asset-defaults.json`: Default asset positions
- `runtime-config.json`: Runtime configuration (Gemini API key, model)

### Agent States and Area Mapping

Six valid states map to three office areas:
- `idle` → breakroom (sofa/rest area)
- `writing`, `researching`, `executing`, `syncing` → writing (desk/work area)
- `error` → error (bug area)

State synonyms are normalized (e.g., `working`/`busy`→`writing`, `run`→`executing`).

### Multi-Agent Flow

1. Guest agent calls `/join-agent` with `joinKey`, `name`, `state`
2. Server validates key, checks concurrent limit (default: 3 per key), auto-approves
3. Guest periodically calls `/agent-push` with `agentId`, `joinKey`, `state`, `detail`
4. If no push for 5 minutes, agent status becomes `offline`
5. Guest calls `/leave-agent` to leave and free the join key

### Image Generation (Background)

- Uses Gemini API for AI-generated RPG-style room backgrounds
- Requires `gemini-image-generate` skill installed at `../skills/gemini-image-generate/`
- Generation is async: `/assets/generate-rpg-background` returns task_id, frontend polls `/assets/generate-rpg-background/poll`
- Room reference image at `assets/room-reference.webp` ensures layout consistency

### Security Notes

- Production mode: detected via `CLAW_OFFICE_ENV=production` or `RENDER`/`Railway` env vars or non-localhost host
- Production requires strong `FLASK_SECRET_KEY`/`CLAW_OFFICE_SECRET` and `ASSET_DRAWER_PASS`
- Session cookies: HttpOnly, SameSite=Lax, Secure in production
- Sidebar password protects asset management and layout editing

## License

- Code: MIT
- Art assets: Non-commercial use only (must replace for commercial use)
