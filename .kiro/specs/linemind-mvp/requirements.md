# Requirements Document

## Introduction

LineMind는 제조 현장을 위한 AI 기반 생산 관리 시스템입니다. 이 MVP는 생산량 예측, 모델 믹스 최적화, 인력 스케줄링의 전체 사이클을 데모하는 것을 목표로 합니다. 필드 지식이 없는 개발자도 단계별로 구현할 수 있도록 설계되었으며, 각 단계는 독립적으로 테스트 가능하고 점진적으로 복잡도가 증가합니다.

핵심 가치는 다음과 같습니다:
- 수요 예측을 통한 생산 계획의 정확성 향상
- 라인별 최적 모델 배정으로 체인지오버 비용 절감
- 제약 조건을 고려한 인력 스케줄링으로 인건비 최적화

## Requirements

### Requirement 1: 프로젝트 초기화 및 기본 연결

**User Story:** 개발자로서, 백엔드와 프론트엔드가 정상적으로 통신하는지 확인하고 싶습니다. 그래야 이후 기능 개발을 안전하게 진행할 수 있습니다.

#### Acceptance Criteria

1. WHEN 프로젝트 구조가 생성되면 THEN 시스템은 `linemind-mvp` 루트 디렉토리 아래 `backend`, `frontend`, `data`, `docs` 서브디렉토리를 포함해야 합니다
2. WHEN FastAPI 백엔드가 실행되면 THEN 시스템은 `GET /health` 엔드포인트에서 200 OK 응답과 함께 `{"status": "LineMind API is running"}` 메시지를 반환해야 합니다
3. WHEN Next.js 프론트엔드가 실행되면 THEN 시스템은 `http://localhost:3000`에서 "LineMind Ready"와 API 상태를 표시해야 합니다
4. WHEN 프론트엔드가 백엔드 `/health` 엔드포인트를 호출하면 THEN CORS 설정으로 인해 요청이 성공해야 합니다
5. WHEN 개발자가 Git 저장소를 초기화하면 THEN 시스템은 `.git` 디렉토리를 생성하고 커밋 준비 상태가 되어야 합니다

### Requirement 2: 시드 데이터 로딩 시스템

**User Story:** 개발자로서, 생산 이력, 라인 정보, 작업자 정보, 비용 파라미터를 CSV 파일로 관리하고 싶습니다. 그래야 데이터 변경 시 코드 수정 없이 테스트할 수 있습니다.

#### Acceptance Criteria

1. WHEN 시스템이 `production_history.csv`를 로드하면 THEN 필수 컬럼 `date`, `line_id`, `model`, `shift`, `produced_units`, `target_units`가 존재해야 합니다
2. WHEN 시스템이 `lines.csv`를 로드하면 THEN 필수 컬럼 `line_id`, `eligible_models`, `base_daily_capacity`가 존재해야 합니다
3. WHEN 시스템이 `workers.csv`를 로드하면 THEN 필수 컬럼 `worker_id`, `name`, `years`, `wage_per_hour`, `max_hours_week`가 존재해야 합니다
4. WHEN 시스템이 `cost_params.csv`를 로드하면 THEN 필수 컬럼 `from_model`, `to_model`, `changeover_hours`, `changeover_cost`가 존재해야 합니다
5. WHEN CSV 파일에 결측치(NA)가 있으면 THEN 시스템은 명확한 에러 메시지와 함께 로딩을 실패해야 합니다
6. WHEN CSV 파일이 존재하지 않으면 THEN 시스템은 `FileNotFoundError`를 발생시켜야 합니다
7. WHEN `GET /api/data/status` 엔드포인트가 호출되면 THEN 시스템은 각 데이터셋의 행 개수를 포함한 JSON 응답을 반환해야 합니다

### Requirement 3: 기본 생산량 예측

**User Story:** 생산 관리자로서, 각 모델의 미래 생산량을 예측하고 싶습니다. 그래야 사전에 생산 계획을 수립할 수 있습니다.

#### Acceptance Criteria

1. WHEN 시스템이 예측을 실행하면 THEN 이동평균 알고리즘을 사용하여 각 모델별로 30일간의 예측값을 생성해야 합니다
2. WHEN 특정 모델의 과거 데이터가 없으면 THEN 시스템은 기본값(100 units/day)으로 예측을 생성해야 합니다
3. WHEN 예측이 생성되면 THEN 각 예측 포인트는 `date`, `model`, `forecast_units`, `conf_lo`, `conf_hi`를 포함해야 합니다
4. WHEN `POST /api/forecast/run` 엔드포인트가 호출되면 THEN 시스템은 모든 모델에 대한 예측 결과를 JSON 형식으로 반환해야 합니다
5. WHEN 프론트엔드에서 "예측 실행" 버튼을 클릭하면 THEN 시스템은 모델별 예측 그래프를 라인 차트로 표시해야 합니다
6. WHEN 예측 결과가 표시되면 THEN 각 모델별로 평균 예측값, 예측 기간, 총 예측량을 요약 통계로 보여줘야 합니다

### Requirement 4: 더미 생산 믹스 최적화

**User Story:** 생산 관리자로서, 예측된 수요를 바탕으로 각 라인에 어떤 모델을 배정할지 알고 싶습니다. 그래야 생산 계획을 수립할 수 있습니다.

#### Acceptance Criteria

1. WHEN 시스템이 믹스 최적화를 실행하면 THEN 예측 결과를 자동으로 가져와서 사용해야 합니다
2. WHEN 라인 배정이 수행되면 THEN 각 모델은 해당 모델을 생산할 수 있는 라인에만 배정되어야 합니다
3. WHEN 수요가 여러 라인에 분배되면 THEN 시스템은 균등 분배 방식을 사용해야 합니다
4. WHEN 최적화 결과가 생성되면 THEN 각 계획 항목은 `period`, `line_id`, `model`, `planned_units`, `line_utilization`을 포함해야 합니다
5. WHEN `POST /api/mix/optimize` 엔드포인트가 호출되면 THEN 시스템은 믹스 계획과 KPI(`total_demand`, `total_planned`, `fulfillment_rate`)를 반환해야 합니다
6. WHEN 프론트엔드에서 최적화 결과를 표시하면 THEN 모델별 생산 비중을 파이 차트로, 라인별 계획을 바 차트로 시각화해야 합니다
7. WHEN 최적화 결과가 표시되면 THEN KPI 카드(총 수요, 계획 생산, 충족률, 예상 비용)를 보여줘야 합니다

### Requirement 5: MILP 기반 생산 믹스 최적화

**User Story:** 생산 관리자로서, 체인지오버 비용과 라인 용량을 고려한 최적의 생산 계획을 원합니다. 그래야 비용을 최소화하면서 수요를 충족할 수 있습니다.

#### Acceptance Criteria

1. WHEN 시스템이 MILP 최적화를 실행하면 THEN OR-Tools SCIP 솔버를 사용해야 합니다
2. WHEN 최적화 모델이 생성되면 THEN 각 라인-모델-주차 조합에 대한 생산량 변수 `Q[l,m,w]`와 생산 여부 변수 `Y[l,m,w]`를 정의해야 합니다
3. WHEN 제약 조건이 적용되면 THEN 각 라인은 주당 최대 하나의 모델만 생산해야 합니다
4. WHEN 제약 조건이 적용되면 THEN 생산량은 라인의 주간 용량(`base_daily_capacity * 7`)을 초과할 수 없습니다
5. WHEN 제약 조건이 적용되면 THEN 각 모델의 주간 수요는 모든 라인의 생산량 합으로 충족되어야 합니다
6. WHEN 목적 함수가 정의되면 THEN 총 비용(생산 비용 + 체인지오버 비용)을 최소화해야 합니다
7. WHEN 솔버가 최적해를 찾으면 THEN 시스템은 믹스 계획과 KPI(`total_cost`, `changeovers`, `fulfillment_rate`)를 반환해야 합니다
8. WHEN 솔버가 해를 찾지 못하면 THEN 시스템은 "No optimal solution found" 에러 메시지를 반환해야 합니다

### Requirement 6: 더미 인력 스케줄링

**User Story:** 생산 관리자로서, 생산 계획에 따라 필요한 작업자를 배정하고 싶습니다. 그래야 인력 운영 계획을 수립할 수 있습니다.

#### Acceptance Criteria

1. WHEN 스케줄링이 실행되면 THEN 최적화된 생산 계획(`mix_plan`)을 입력으로 받아야 합니다
2. WHEN 필요 인원이 산정되면 THEN 100대 생산당 1명의 비율을 사용해야 합니다
3. WHEN 작업자가 배정되면 THEN 연차가 높은 순서대로 우선 배정해야 합니다
4. WHEN 스케줄이 생성되면 THEN 각 항목은 `date`, `line_id`, `shift`, `worker_id`, `worker_name`을 포함해야 합니다
5. WHEN `POST /api/schedule/run` 엔드포인트가 호출되면 THEN 시스템은 스케줄 결과를 JSON 배열로 반환해야 합니다
6. WHEN 프론트엔드에서 스케줄을 표시하면 THEN 날짜, 라인, 교대, 작업자 정보를 테이블 형식으로 보여줘야 합니다

### Requirement 7: CP-SAT 기반 인력 스케줄링

**User Story:** 생산 관리자로서, 근무 시간 제한, 휴식 시간, 교대 규칙을 준수하는 최적의 인력 스케줄을 원합니다. 그래야 법규를 준수하면서 인건비를 최소화할 수 있습니다.

#### Acceptance Criteria

1. WHEN 시스템이 CP-SAT 스케줄링을 실행하면 THEN OR-Tools CP-SAT 솔버를 사용해야 합니다
2. WHEN 스케줄링 모델이 생성되면 THEN 각 작업자-날짜-교대 조합에 대한 불리언 변수 `x[w,d,s]`를 정의해야 합니다
3. WHEN 제약 조건이 적용되면 THEN 각 작업자는 하루에 최대 한 교대만 근무해야 합니다
4. WHEN 제약 조건이 적용되면 THEN 각 작업자의 주간 총 근무 시간은 `max_hours_week`를 초과할 수 없습니다
5. WHEN 제약 조건이 적용되면 THEN 연속 야간 근무는 3일을 초과할 수 없습니다
6. WHEN 목적 함수가 정의되면 THEN 총 인건비와 선호도 위반 페널티를 최소화해야 합니다
7. WHEN 솔버가 해를 찾으면 THEN 시스템은 스케줄과 KPI(`total_cost`, `total_ot_hours`, `fulfillment_rate`)를 반환해야 합니다
8. WHEN 프론트엔드에서 KPI를 표시하면 THEN 총 인건비, 총 OT 시간, 야간 편중 지수를 카드 형식으로 보여줘야 합니다

### Requirement 8: 워크플로우 통합 및 에러 핸들링

**User Story:** 사용자로서, 예측부터 스케줄링까지 전체 프로세스를 원클릭으로 진행하고 싶습니다. 그리고 오류 발생 시 명확한 안내를 받고 싶습니다.

#### Acceptance Criteria

1. WHEN 예측 페이지에서 "이 결과로 믹스 최적화" 버튼을 클릭하면 THEN 시스템은 자동으로 최적화 페이지로 이동하고 최적화를 실행해야 합니다
2. WHEN 최적화 페이지에서 "이 계획으로 스케줄링" 버튼을 클릭하면 THEN 시스템은 자동으로 스케줄링 페이지로 이동하고 스케줄링을 실행해야 합니다
3. WHEN CSV 파일에 필수 컬럼이 누락되면 THEN 시스템은 "필수 컬럼이 없습니다: [컬럼명]" 에러 메시지를 UI에 표시해야 합니다
4. WHEN CSV 파일에 결측치가 있으면 THEN 시스템은 "데이터에 결측치가 있습니다" 에러 메시지를 UI에 표시해야 합니다
5. WHEN 솔버가 타임아웃되거나 해를 찾지 못하면 THEN 시스템은 "제약 조건을 완화해보세요" 같은 해결책을 제안해야 합니다
6. WHEN API 호출이 실패하면 THEN 시스템은 사용자 친화적인 토스트 메시지를 표시해야 합니다
7. WHEN 백엔드에서 예외가 발생하면 THEN 시스템은 서버가 중단되지 않고 에러 응답을 반환해야 합니다

### Requirement 9: 대시보드 및 UI/UX 개선

**User Story:** 사용자로서, 프로젝트의 가치와 현재 진행 상황을 한눈에 파악하고 싶습니다. 그래야 시스템을 효과적으로 활용할 수 있습니다.

#### Acceptance Criteria

1. WHEN 홈 페이지가 로드되면 THEN 시스템은 핵심 KPI 4개(예측 정확도, 비용 절감률, OT 감소율, 충족률)를 카드 형식으로 표시해야 합니다
2. WHEN 홈 페이지가 로드되면 THEN 시스템은 현재 워크플로우 진행 상황(예측 → 믹스 → 스케줄링)을 Progress Bar로 표시해야 합니다
3. WHEN 각 기능 페이지가 표시되면 THEN "이 화면은 무엇을 해결하나요?" 같은 설명 박스를 포함해야 합니다
4. WHEN 데이터 라벨이 표시되면 THEN 특정 산업(예: 자동차 부품)에 맞는 용어를 사용해야 합니다
5. WHEN 사용자가 네비게이션하면 THEN "홈으로 돌아가기" 버튼이 항상 표시되어야 합니다
6. WHEN 차트가 표시되면 THEN 한글 레이블과 툴팁을 사용해야 합니다

### Requirement 10: 프로젝트 문서화 및 제출 준비

**User Story:** 개발자로서, 프로젝트를 다른 사람에게 전달하거나 제출할 때 필요한 모든 문서를 준비하고 싶습니다.

#### Acceptance Criteria

1. WHEN README.md가 작성되면 THEN 프로젝트 개요, 설치 방법, 실행 방법, 기술 스택을 포함해야 합니다
2. WHEN README.md가 작성되면 THEN 각 단계(STEP 0-9)의 체크리스트와 커밋 메시지를 포함해야 합니다
3. WHEN 프로젝트가 제출되면 THEN requirements.txt와 package.json이 모든 의존성을 포함해야 합니다
4. WHEN 프로젝트가 제출되면 THEN 주요 화면의 스크린샷 또는 GIF를 docs 폴더에 포함해야 합니다
5. WHEN 프로젝트가 제출되면 THEN .gitignore 파일이 venv, node_modules, __pycache__ 등을 제외해야 합니다
6. WHEN 프로젝트가 제출되면 THEN 모든 코드가 Git에 커밋되고 의미 있는 커밋 메시지를 가져야 합니다
