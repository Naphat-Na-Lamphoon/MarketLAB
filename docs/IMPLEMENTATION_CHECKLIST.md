# MarketLab implementation checklist

เอกสารนี้เป็นลำดับการพัฒนา MarketLab จาก MVP scaffold ไปสู่ระบบที่พร้อมเชื่อม Generative AI และรัน experiment ได้อย่างปลอดภัย

## กติกาการทำงาน

- ทำทีละ milestone และให้ milestone ก่อนหน้าผ่าน validation ก่อนเริ่ม milestone ถัดไป
- ทุก AI output ต้องมีสถานะ `DRAFT` จนกว่า operator จะอนุมัติ
- ใช้ `simulated` เป็น channel เริ่มต้นเสมอ
- ห้ามส่งข้อมูลส่วนบุคคลไปยัง Gemini, telemetry หรือ evidence
- ห้ามยิง Google Ads หากไม่มี approval ที่ถูกต้องและงบไม่เกิน cap

## สถานะปัจจุบัน

- [x] สร้าง monorepo scaffold
- [x] สร้าง Next.js web shell
- [x] สร้าง FastAPI API เบื้องต้น
- [x] สร้าง environment template
- [x] สร้าง Docker Compose สำหรับ PostgreSQL/pgvector
- [x] เพิ่มคู่มือ setup
- [ ] เชื่อม database จริง
- [ ] เพิ่ม authentication/RBAC
- [ ] เพิ่ม Generative AI
- [ ] เพิ่ม experiment execution จริง

## VS Code-only phase: ทำได้ทันทีโดยไม่ต้องติดตั้ง backend infrastructure

- [x] เพิ่ม VS Code extension recommendations
- [x] เพิ่ม VS Code settings สำหรับ Python backend และ TypeScript
- [x] เพิ่ม VS Code tasks สำหรับ typecheck และ build ของ web
- [x] เพิ่ม VS Code task สำหรับเริ่ม web dev server
- [ ] ติดตั้ง extension ที่แนะนำตามความพร้อมของเครื่อง
- [x] ตรวจและปรับ API schemas ให้ครบตาม SRS เบื้องต้น
- [x] เพิ่ม domain models และ repository interfaces เบื้องต้น
- [x] เพิ่ม prompt templates และ AI output schemas โดยยังไม่เรียก provider
- [x] เพิ่ม unit tests สำหรับ rules และ stats
- [x] เพิ่ม frontend forms สำหรับ hypothesis และ asset review
- [x] เพิ่ม API client ฝั่ง web
- [ ] เพิ่ม mock data สำหรับพัฒนา UI โดยไม่ต้องมี database

**ขอบเขต:** phase นี้ทำได้ใน VS Code และใช้ Node.js ที่มีอยู่ได้ทันที ส่วน Python runtime, Docker, PostgreSQL และ Redis จะทำใน Milestone 0 เมื่อพร้อมติดตั้ง

## Milestone 0: เตรียมเครื่องมือและรันระบบ

- [ ] ติดตั้ง Python 3.11+
- [ ] ติดตั้ง Docker Desktop
- [ ] สร้าง `.env` จาก `.env.example`
- [ ] รัน PostgreSQL/pgvector และ Redis ด้วย Docker Compose
- [ ] รัน FastAPI และเปิด `/docs`
- [ ] รัน Next.js และเปิด dashboard
- [ ] ผ่าน health check ของ API และ web

**จุดตรวจ:** ระบบเริ่มได้จากเครื่องใหม่ตาม [SETUP.md](./SETUP.md) โดยไม่ต้องแก้ source code

## Milestone 1: วางฐานข้อมูลและ domain model

### สถานะ local-first (ไม่ใช้ Docker)

- [x] เพิ่ม SQLAlchemy async engine และ session management
- [x] เพิ่ม Alembic configuration และ migration แรก
- [x] สร้าง model หลักและความสัมพันธ์สำหรับ local SQLite
- [x] เพิ่ม tests สำหรับ create/read และ foreign-key relationships
- [ ] ตรวจสอบ PostgreSQL/pgvector จริง (รอ Docker หรือ PostgreSQL)
- [ ] เปลี่ยน API ทั้งหมดจาก in-memory เป็น database repository/service

นี่คือขั้นแรกที่ควรทำหลังเตรียมเครื่อง เพราะทุกส่วนถัดไปต้องพึ่งข้อมูลที่ถาวรและมีความสัมพันธ์ถูกต้อง

- [x] เพิ่ม SQLAlchemy 2.0 async engine และ session management
- [x] เพิ่ม Alembic
- [x] สร้าง model: users, hypotheses, variants, experiments
- [x] สร้าง model: approvals, adapter_requests, telemetry_events
- [x] สร้าง model: evaluations, evidence_records
- [x] เพิ่ม constraints, indexes และ enum/status ตาม SRS
- [x] สร้าง migration แรก
- [x] เพิ่ม database health check
- [ ] เปลี่ยน API จาก in-memory เป็น database repository/service
- [x] เพิ่ม tests สำหรับ create/read และ foreign-key relationships

**จุดตรวจ:** restart API แล้วข้อมูลยังอยู่ และ migration ทำงานจากฐานข้อมูลว่างได้

## Milestone 2: Authentication และ governance

- [ ] เพิ่ม JWT authentication
- [ ] เพิ่ม role: operator, admin, viewer
- [ ] ป้องกัน endpoint ที่ไม่ใช่ public telemetry
- [ ] เพิ่ม current-user dependency
- [ ] บันทึกผู้อนุมัติลง approvals แบบ append-only
- [ ] บังคับ approval และ budget cap ใน backend ทุกครั้งที่ launch
- [ ] เพิ่ม audit logging สำหรับ state transitions
- [ ] เพิ่ม tests สำหรับ unauthorized, forbidden และ invalid approval

**จุดตรวจ:** ผู้ไม่มีสิทธิ์ไม่สามารถ approve หรือ launch ได้ แม้เรียก API โดยตรง

## Milestone 3: Hypothesis และ asset workflow

- [ ] ทำ 4D validation: Problem, Segment, Offer, Pricing
- [ ] เพิ่ม hypothesis versioning
- [ ] เพิ่ม variant CRUD
- [ ] เพิ่ม status transition: DRAFT, APPROVED, REJECTED
- [ ] เพิ่มหน้า Hypothesis Builder
- [ ] เพิ่มหน้า Asset Review
- [ ] แสดง budget cap และสถานะ approval ใน UI
- [ ] ทดสอบ state transition ที่ไม่ถูกต้อง

**จุดตรวจ:** ทุก asset ที่แสดงใน landing page ต้องเป็น variant ที่ approved เท่านั้น

## Milestone 4: ใส่ Generative AI อย่างปลอดภัย

- [ ] เพิ่ม Gemini client ใน backend เท่านั้น ห้ามเรียก provider จาก browser
- [ ] เพิ่ม config สำหรับ model, timeout, retry และ rate limit
- [ ] สร้าง prompt templates แบบ versioned ใน `backend/app/prompts/`
- [ ] เพิ่ม Pydantic schema สำหรับ hypothesis extraction
- [ ] เพิ่ม Pydantic schema สำหรับ ad copy และ landing page
- [ ] เพิ่ม PII redaction ก่อนส่งข้อมูลไป Gemini
- [ ] เพิ่ม structured JSON response validation
- [ ] retry เมื่อ JSON ไม่ถูกต้องได้ไม่เกินจำนวนที่กำหนด
- [ ] handle timeout, 429 และ provider error แบบแจ้งผู้ใช้ชัดเจน
- [ ] เพิ่ม endpoint `POST /api/v1/hypotheses/extract`
- [ ] เพิ่ม endpoint `POST /api/v1/variants/{id}/generate`
- [ ] เก็บ prompt version, model, status และ error metadata
- [ ] บังคับผลลัพธ์ทุกครั้งเป็น `DRAFT`
- [ ] เพิ่มปุ่ม Generate, Regenerate, Approve และ Reject ใน UI
- [ ] เพิ่ม tests ที่ยืนยันว่า AI ไม่สามารถข้าม approval gate ได้

**จุดตรวจ:** มี Gemini key แล้วจึง generate ได้ แต่ระบบยังทำงานใน simulated mode ได้แม้ไม่มี Gemini key

## Milestone 5: Simulated experiment และ idempotency

- [ ] สร้าง `ChannelAdapter` interface
- [ ] สร้าง `SimulatedAdapter`
- [ ] รองรับ configurable CTR/CVR/latency
- [ ] รองรับ injectable timeout/failure สำหรับ tests
- [ ] สร้าง adapter request ledger
- [ ] persist idempotency key ก่อนเรียก adapter
- [ ] retry โดยใช้ key เดิม
- [ ] ป้องกัน duplicate spend
- [ ] เพิ่ม launch/pause/metrics flow
- [ ] เพิ่ม Celery worker และ Redis task queue
- [ ] เพิ่ม tests timeout แล้ว retry สำเร็จเพียงครั้งเดียว

**จุดตรวจ:** retry ใด ๆ ไม่สร้าง campaign หรือ spend ซ้ำ

## Milestone 6: Landing page และ telemetry

- [ ] เชื่อม landing page กับ approved experiment data
- [ ] assign variant ด้วย anonymous UUID ที่ไม่ใช่ PII
- [ ] เพิ่ม academic prototype disclaimer
- [ ] เพิ่ม telemetry endpoint แบบ batch
- [ ] validate event type และ event payload
- [ ] deduplicate ด้วย event_id
- [ ] ปฏิเสธ PII fields
- [ ] เชื่อม PostHog แบบ opt-out
- [ ] เพิ่ม tests duplicate event และ privacy

**จุดตรวจ:** event เดิมส่งซ้ำแล้วไม่เพิ่มยอด และไม่มีข้อมูลส่วนบุคคลถูกจัดเก็บ

## Milestone 7: Statistics และ decision rules

- [ ] คำนวณ sample size
- [ ] คำนวณ CTR/CVR
- [ ] คำนวณ z-score และ p-value
- [ ] ไม่ประกาศ significance ก่อน minimum sample
- [ ] ใช้ R1 winner
- [ ] ใช้ R2 approval/budget guard
- [ ] ใช้ R3 idempotency
- [ ] ใช้ R4 inconclusive
- [ ] แสดงผลใน Experiment Monitor
- [ ] เพิ่ม textbook และ boundary-value tests

**จุดตรวจ:** ผลลัพธ์ทุกสถานะมีเหตุผลและตัวเลขประกอบตรวจสอบได้

## Milestone 8: Evidence Graph

- [ ] เพิ่ม embedding provider abstraction
- [ ] สร้าง evidence summary โดยไม่มี raw telemetry หรือ PII
- [ ] บันทึก pgvector embedding
- [ ] เพิ่ม semantic search และ filter ตาม segment/offer/date
- [ ] เชื่อม winner result เข้ากับ evidence record
- [ ] เพิ่ม Evidence Search UI
- [ ] เพิ่ม tests ว่าผลลัพธ์ที่ใกล้เคียงสุดขึ้นก่อน

## Milestone 9: Production readiness

- [ ] เพิ่ม CI: lint, type-check, tests, coverage
- [ ] เพิ่ม structured logging และ request correlation ID
- [ ] เพิ่ม secrets management
- [ ] เพิ่ม database backup/restore procedure
- [ ] เพิ่ม rate limiting และ request size limits
- [ ] เพิ่ม error monitoring
- [ ] เพิ่ม OpenAPI export
- [ ] เพิ่ม deployment configuration
- [ ] ทดสอบ staging โดยยังปิด real ads
- [ ] เปิด Google Ads เฉพาะหลังผ่าน approval, budget และ operational review

## ลำดับการลงมือที่แนะนำตอนนี้

1. ทำ Milestone 0 ให้เครื่องรัน API, web, PostgreSQL และ Redis ได้
2. ทำ Milestone 1 ให้ข้อมูลถาวรใน PostgreSQL
3. ทำ Milestone 2 ให้มีตัวตนและสิทธิ์ผู้ใช้งาน
4. ทำ Milestone 3 ให้ workflow ของ hypothesis/asset สมบูรณ์
5. เริ่ม Milestone 4 เพื่อเชื่อม Generative AI

ไม่แนะนำให้เริ่มจากการใส่ Gemini ในหน้าเว็บทันที เพราะถ้ายังไม่มี database, auth และ approval gate จะควบคุม draft, audit และสิทธิ์การนำผลลัพธ์ AI ไปใช้จริงได้ไม่ปลอดภัย
