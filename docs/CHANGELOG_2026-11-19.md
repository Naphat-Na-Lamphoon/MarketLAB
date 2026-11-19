# รายงานการเปลี่ยนแปลงล่าสุด

วันที่: 19 พฤศจิกายน 2026  
ฐานการเปรียบเทียบ: `1d38b3c` (`Refresh MarketLAB dashboard UI`)

## สรุป

รอบนี้เพิ่มความพร้อมสำหรับการสาธิต MarketLAB แบบ local โดยสามารถใช้ workflow
ทดลองจำลองได้โดยไม่ต้องเชื่อมฐานข้อมูลภายนอก พร้อมเพิ่ม seed data และเอกสาร
สำหรับการนำเสนอและการตั้งค่าสภาพแวดล้อม

## รายการเปลี่ยนแปลง

### Backend API

- เพิ่ม demo state สำหรับ `admin`, `operator` และ `viewer` ในโหมด `ENV=dev`
- เพิ่มการสร้าง/เรียกดู hypotheses และ variants
- เพิ่มการ approve/reject variants
- จำกัด channel ของ prototype ให้ใช้ `simulated` เท่านั้น
- เพิ่มการเรียกดู experiments และการ pause experiment
- เพิ่ม telemetry ที่ป้องกัน event ซ้ำด้วย `event_id`
- เพิ่ม metrics ราย variant ได้แก่ views, clicks, conversions, CTR และ CVR
- เพิ่มการประเมินผลด้วย z-test และ decision status
- เพิ่ม validation ไม่ให้ค่า telemetry `value` ติดลบ

### Seed data และการทดสอบ

- เพิ่ม `backend/app/seed.py` สำหรับสร้างข้อมูล role demo แบบใช้ซ้ำได้
- ใช้ PBKDF2 ในการ hash password ของข้อมูล seed
- เพิ่ม test สำหรับ API workflow, telemetry idempotency และ seed data

### Frontend

- ปรับข้อความปุ่มกลับหน้า Dashboard ใน Hypothesis Builder ให้รองรับภาษาไทย
- คง dashboard และ form styling สำหรับการสาธิต workflow

### Configuration และ Documentation

- เปลี่ยนพอร์ต host ของ PostgreSQL ใน Docker Compose เป็น `5433`
- อัปเดต `.env.example` ให้ตรงกับพอร์ตใหม่
- อัปเดต README, setup guide และ implementation checklist
- เพิ่มเอกสารภาพรวมโครงการสำหรับการนำเสนอที่
  [`MARKETLAB_PROJECT_DOCUMENT.md`](./MARKETLAB_PROJECT_DOCUMENT.md)
- เพิ่มไฟล์ PDF ของเอกสารภาพรวมโครงการ

## การตรวจสอบ

- Backend tests: 28 passed
- Frontend TypeScript check: passed
- Next.js production build: passed
- Patch whitespace check: passed

## ข้อจำกัดที่ยังคงอยู่

- demo state และ telemetry ของ API ยังอยู่ใน memory และหายเมื่อ restart
- authentication และ RBAC ยังไม่ถูก enforce ใน API
- PostgreSQL/pgvector และ Google Ads จริงยังไม่เปิดใช้งาน
- dashboard ยังมีข้อมูลสรุปที่จัดเตรียมเพื่อการนำเสนอ
