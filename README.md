# LineMind MVP

AI 기반 생산 관리 시스템 - 생산 예측, 믹스 최적화, 인력 스케줄링 풀사이클 데모

## 📋 프로젝트 개요

LineMind는 제조 현장을 위한 AI 기반 생산 관리 시스템입니다. 이 MVP는 다음 3가지 핵심 기능을 제공합니다:

1. **생산량 예측** - 과거 생산 이력을 기반으로 미래 30일간의 수요 예측
2. **생산 믹스 최적화** - MILP를 사용하여 라인별 최적 모델 배정
3. **인력 스케줄링** - CP-SAT를 사용하여 제약 조건을 고려한 작업자 배정

### 핵심 가치

- 📈 **수요 예측**: 이동평균 알고리즘으로 생산 계획의 정확성 향상
- ⚙️ **비용 절감**: 체인지오버 비용과 라인 용량을 고려한 최적화
- 👥 **인건비 최적화**: 근무 시간 제한과 법규를 준수하는 스케줄링

## 🛠 기술 스택

### Backend
- **Framework**: FastAPI 0.104+
- **Language**: Python 3.9+
- **Data Processing**: pandas, numpy
- **Optimization**: OR-Tools (SCIP for MILP, CP-SAT for scheduling)
- **Server**: uvicorn

### Frontend
- **Framework**: Next.js 14+ (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Charts**: Recharts
- **HTTP Client**: fetch API

### Data Layer
- CSV 기반 시드 데이터 (데이터베이스 불필요)
- 4종 CSV 파일: production_history, lines, workers, cost_params

## 🚀 빠른 시작

### 사전 요구사항

- Python 3.9 이상
- Node.js 18 이상
- Git

### 설치 및 실행

#### 1. 저장소 클론

```bash
git clone https://github.com/sapgun/LineMind.git
cd LineMind
```

#### 2. 백엔드 설정 및 실행

```bash
cd backend

# 가상환경 생성 및 활성화
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# 의존성 설치
pip install -r requirements.txt

# 서버 실행
python app.py
```

백엔드 서버가 http://localhost:8000 에서 실행됩니다.

#### 3. 프론트엔드 설정 및 실행

새 터미널을 열고:

```bash
cd frontend

# 의존성 설치
npm install

# 개발 서버 실행
npm run dev
```

프론트엔드가 http://localhost:3000 에서 실행됩니다.

#### 4. 브라우저에서 접속

http://localhost:3000 을 열어 LineMind를 사용하세요!

## 📁 프로젝트 구조

```
linemind-mvp/
├── backend/                 # FastAPI 백엔드
│   ├── app.py              # API 엔드포인트
│   ├── data_loader.py      # CSV 데이터 로딩
│   ├── forecast.py         # 생산량 예측 엔진
│   ├── optimizer.py        # 생산 믹스 최적화 (MILP)
│   ├── scheduler.py        # 인력 스케줄링 (CP-SAT)
│   ├── requirements.txt    # Python 의존성
│   └── data/seed/          # 시드 데이터 CSV
│       ├── production_history.csv
│       ├── lines.csv
│       ├── workers.csv
│       └── cost_params.csv
├── frontend/               # Next.js 프론트엔드
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx           # 홈 대시보드
│   │   │   └── layout.tsx         # 루트 레이아웃
│   │   └── components/
│   │       ├── ForecastPage.tsx   # 예측 UI
│   │       ├── OptimizePage.tsx   # 최적화 UI
│   │       └── SchedulePage.tsx   # 스케줄링 UI
│   ├── package.json
│   └── tailwind.config.js
├── docs/                   # 문서 및 스크린샷
└── README.md
```

## 🎯 주요 기능

### 1. 생산량 예측

- 과거 생산 이력 기반 이동평균 예측
- 모델별 30일 예측 생성
- 신뢰구간 (±20%) 제공
- 라인 차트 시각화

### 2. 생산 믹스 최적화

- OR-Tools MILP (SCIP 솔버) 사용
- 제약 조건:
  - 라인당 주간 단일 모델 생산
  - 라인 용량 제한
  - 수요 충족
  - 라인별 지원 가능 모델 제한
- 목적: 총 비용 최소화
- KPI: 총 수요, 계획 생산, 충족률, 예상 비용

### 3. 인력 스케줄링

- OR-Tools CP-SAT 솔버 사용
- 제약 조건:
  - 하루 최대 1교대
  - 주간 최대 근무시간
  - 필요 인원 충족
- 목적: 총 인건비 최소화
- KPI: 총 인건비, OT 시간, 야간 편중 지수, 충족률

## 🔧 환경 변수

백엔드에서 알고리즘을 선택할 수 있습니다:

```bash
# MILP 최적화 사용 (기본값: true)
USE_MILP=true

# CP-SAT 스케줄링 사용 (기본값: true)
USE_CPSAT=true
```

false로 설정하면 더미(Stub) 알고리즘을 사용합니다.

## 📊 API 엔드포인트

### GET /health
서버 상태 확인

### GET /api/data/status
데이터 로딩 상태 확인

### POST /api/forecast/run
생산량 예측 실행

### POST /api/mix/optimize
생산 믹스 최적화 실행

### POST /api/schedule/run
인력 스케줄링 실행 (body: mix_plan)

## 🧪 테스트

### 백엔드 테스트

```bash
cd backend

# 데이터 로더 테스트
python data_loader.py

# 예측 테스트
python forecast.py

# 최적화 테스트
python optimizer.py

# 스케줄링 테스트
python scheduler.py
```

### 전체 플로우 테스트

1. 백엔드와 프론트엔드 모두 실행
2. 브라우저에서 http://localhost:3000 접속
3. 홈 → 생산량 예측 → 예측 실행
4. 홈 → 생산 믹스 → 최적화 실행
5. 홈 → 인력 스케줄링 → 스케줄링 실행

## 📝 개발 단계

이 프로젝트는 다음 단계로 개발되었습니다:

- ✅ STEP 0: 프로젝트 초기화 및 기본 연결
- ✅ STEP 1: 시드 데이터 및 DataLoader
- ✅ STEP 2: 생산량 예측 (이동평균)
- ✅ STEP 3: 더미 생산 믹스 최적화
- ✅ STEP 4: MILP 생산 믹스 최적화
- ✅ STEP 5: 더미 인력 스케줄링
- ✅ STEP 6: CP-SAT 인력 스케줄링

## 🤝 기여

이 프로젝트는 MVP 단계입니다. 개선 사항이나 버그를 발견하시면 이슈를 등록해주세요.

## 📄 라이선스

MIT License

## 👨‍💻 개발자

sapgun

---

**LineMind** - AI로 더 스마트한 생산 관리
