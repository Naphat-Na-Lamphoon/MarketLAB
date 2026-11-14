# MarketLab setup guide

คู่มือนี้ใช้สำหรับตั้งค่าและรันโปรเจคบนเครื่อง local

## 1. Prerequisites

- Node.js 20+ (ตรวจสอบด้วย `node --version`)
- Python 3.11+ และ pip (สำหรับ API)
- Docker Desktop (สำหรับ PostgreSQL/pgvector)

บน Windows ให้ติดตั้ง Python และ Docker Desktop ก่อน หากคำสั่ง `python` หรือ `docker` ใช้งานไม่ได้ จากนั้นเปิด terminal ใหม่

## 2. Environment

ที่ root ของโปรเจค:

```powershell
Copy-Item .env.example .env
```

ค่าที่ปลอดภัยสำหรับ local development มีอยู่ใน `.env.example` แล้ว ห้ามใส่ secret จริงใน git

ถ้ายังไม่มี Docker สามารถทำ M1 และตรวจ syntax ได้ด้วย `uv`:

```powershell
Set-Location backend
$env:PYTHONPATH = "."
uv run --with -r requirements.txt python -m pytest -q
python -m compileall -q app tests migrations
```

## 3. Start infrastructure

```powershell
docker compose up -d
```

## 4. Start API

```powershell
Set-Location backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

เมื่อใช้ค่าเริ่มต้นแบบ local SQLite ให้ตรวจฐานข้อมูลได้ที่
`http://localhost:8000/health/db` โดยไม่ต้องเปิด Docker

## 5. Start web

เปิด terminal อีกหน้าต่าง:

```powershell
npm install --prefix web
npm run dev:web
```

Dashboard: http://localhost:3000

## 6. Smoke test

```powershell
Invoke-RestMethod http://localhost:8000/health
Invoke-RestMethod http://localhost:3000
```

## 7. Configuration notes

- `DEFAULT_CHANNEL=simulated` ต้องคงไว้ใน development
- `ENABLE_REAL_ADS=false` ต้องเป็น false จนกว่าจะมี approval, credentials, และการทดสอบ production ที่เหมาะสม
- Gemini/PostHog เป็น optional ใน scaffold นี้; ระบบจะใช้ข้อมูลจำลองเมื่อยังไม่มี key
- API persistence จะย้ายจาก in-memory ไป PostgreSQL ใน milestone ถัดไป โดย schema หลักอ้างอิงจาก `MARKETLAB_DEV_GUIDE.md`

## 8. Expected workflow

1. สร้าง hypothesis ที่มี Problem, Segment, Offer, Pricing และ budget cap
2. สร้าง variant และ experiment
3. approve experiment ผ่าน operator
4. launch ได้เฉพาะเมื่อมี approval และ spend ไม่เกิน cap
5. ส่ง telemetry แบบ UUID-only
6. evaluate เพื่อคำนวณ CTR/CVR, z-score และ p-value

## 9. Troubleshooting

- ถ้า PowerShell block activation: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`
- ถ้า port 3000/8000 ถูกใช้ ให้เปลี่ยน port ในคำสั่ง start
- ถ้า Docker ยังไม่พร้อม ให้เปิด Docker Desktop แล้วรัน `docker compose up -d` ใหม่
