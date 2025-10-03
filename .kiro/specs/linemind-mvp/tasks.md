# Implementation Plan

- [x] 1. 프로젝트 구조 및 Git 초기화




  - 루트 디렉토리 `linemind-mvp` 생성 및 하위 폴더 `backend`, `frontend`, `data`, `docs` 생성
  - Git 저장소 초기화 및 `.gitignore` 파일 생성 (venv, node_modules, __pycache__, .next 제외)
  - _Requirements: 1.1, 1.5_





- [ ] 2. FastAPI 백엔드 기본 설정
  - [ ] 2.1 Python 가상환경 생성 및 의존성 설치
    - `backend` 폴더에서 가상환경 생성
    - fastapi, uvicorn, pandas, numpy 설치


    - `requirements.txt` 생성
    - _Requirements: 1.2_
  
  - [ ] 2.2 FastAPI 앱 및 health 엔드포인트 구현
    - `backend/app.py` 생성

    - FastAPI 앱 인스턴스 생성 (title="LineMind API", version="1.0.0")


    - CORS 미들웨어 추가 (allow_origins=["http://localhost:3000"])
    - `GET /health` 엔드포인트 구현 ({"status": "LineMind API is running"} 반환)
    - uvicorn으로 서버 실행 테스트 (port 8000)


    - _Requirements: 1.2, 1.4_

- [ ] 3. Next.js 프론트엔드 기본 설정
  - [ ] 3.1 Next.js 프로젝트 생성
    - `frontend` 폴더에서 create-next-app 실행 (TypeScript, Tailwind CSS, ESLint 옵션 활성화)

    - 프로젝트 구조 확인


    - _Requirements: 1.3_
  
  - [ ] 3.2 홈 페이지에서 백엔드 연결 테스트
    - `frontend/src/app/page.tsx` 수정


    - useState로 apiStatus 상태 관리
    - useEffect에서 `/health` 엔드포인트 호출
    - "LineMind Ready" 텍스트 및 API 상태 표시


    - 브라우저에서 연결 확인 (localhost:3000)
    - _Requirements: 1.3, 1.4_



- [x] 4. 시드 데이터 CSV 파일 생성

  - [x] 4.1 production_history.csv 생성


    - `backend/data/seed/` 폴더 생성
    - 최소 8행의 생산 이력 데이터 작성 (date, line_id, model, shift, produced_units, target_units)
    - 3개 모델 (ModelA, ModelB, ModelC), 2개 라인 (L1, L2) 포함


    - _Requirements: 2.1_
  
  - [ ] 4.2 lines.csv 생성
    - 3개 라인 정보 작성 (line_id, eligible_models, base_daily_capacity)
    - eligible_models는 쉼표로 구분된 문자열


    - _Requirements: 2.2_
  
  - [ ] 4.3 workers.csv 생성
    - 5명 이상의 작업자 정보 작성 (worker_id, name, years, wage_per_hour, max_hours_week, prefer_night)


    - _Requirements: 2.3_
  
  - [ ] 4.4 cost_params.csv 생성
    - 모든 모델 간 체인지오버 비용 정의 (from_model, to_model, changeover_hours, changeover_cost)
    - 최소 6개 조합 (A→B, B→A, B→C, C→B, A→C, C→A)
    - _Requirements: 2.4_




- [ ] 5. DataLoader 클래스 구현
  - [ ] 5.1 DataLoader 클래스 기본 구조 작성
    - `backend/data_loader.py` 생성


    - DataLoader 클래스 정의 (__init__ 메서드에서 data_dir 설정)
    - _Requirements: 2.1-2.4_
  
  - [ ] 5.2 load_csv 메서드 구현
    - 파일 존재 여부 확인 (FileNotFoundError 발생)
    - pandas로 CSV 로드
    - 필수 컬럼 검증 (ValueError 발생)


    - 결측치 검증 (ValueError 발생)
    - _Requirements: 2.5, 2.6_
  
  - [x] 5.3 load_all_data 메서드 및 테스트 함수 구현



    - 4개 CSV 파일 로드 (production, lines, workers, costs)
    - 각 파일의 필수 컬럼 리스트 정의
    - test_data_loading() 함수 작성 (성공 시 행 개수 출력)
    - 스크립트 실행하여 "✅ 모든 CSV 로드 성공" 확인


    - _Requirements: 2.1-2.7_

- [x] 6. 데이터 상태 API 엔드포인트 추가

  - `backend/app.py`에 DataLoader 인스턴스 생성


  - `GET /api/data/status` 엔드포인트 구현
  - try-except로 에러 핸들링 (status: error 반환)
  - 성공 시 각 데이터셋의 행 개수 반환
  - 브라우저 또는 curl로 엔드포인트 테스트
  - _Requirements: 2.7_



- [ ] 7. SimpleForecaster 클래스 구현
  - [ ] 7.1 SimpleForecaster 클래스 기본 구조 작성
    - `backend/forecast.py` 생성


    - SimpleForecaster 클래스 정의 (__init__에서 DataLoader 인스턴스 생성)
    - _Requirements: 3.1_
  
  - [x] 7.2 moving_average_forecast 메서드 구현


    - 특정 모델의 과거 데이터 필터링
    - 데이터 없으면 기본값 100 units/day로 예측 생성
    - 날짜별 총 생산량 계산 및 최근 7일 이동평균 계산
    - 정규분포 노이즈 추가 (std = 평균 * 0.1)
    - 신뢰구간 계산 (예측값 * 0.8, 예측값 * 1.2)
    - DataFrame 반환 (date, model, forecast_units, conf_lo, conf_hi)
    - _Requirements: 3.1, 3.2, 3.3_

  


  - [ ] 7.3 run_forecast_all_models 메서드 및 테스트 함수 구현
    - 모든 모델에 대해 예측 실행
    - 결과를 딕셔너리로 반환 (status, forecasts, message)


    - test_forecast() 함수 작성 (모델별 예측 일수 출력)
    - 스크립트 실행하여 예측 결과 확인
    - _Requirements: 3.4_

- [ ] 8. 예측 API 엔드포인트 추가
  - `backend/app.py`에 SimpleForecaster 인스턴스 생성


  - `POST /api/forecast/run` 엔드포인트 구현
  - forecaster.run_forecast_all_models() 호출 및 결과 반환
  - curl 또는 Postman으로 엔드포인트 테스트
  - _Requirements: 3.4_




- [ ] 9. 프론트엔드에 recharts 설치
  - `frontend` 폴더에서 `npm install recharts` 실행
  - package.json에 recharts 의존성 추가 확인

  - _Requirements: 3.5_



- [ ] 10. ForecastPage 컴포넌트 구현
  - [ ] 10.1 ForecastPage 컴포넌트 기본 구조 작성
    - `frontend/src/components/ForecastPage.tsx` 생성
    - 'use client' 지시어 추가


    - useState로 forecasts, loading, error 상태 관리
    - TypeScript 인터페이스 정의 (ForecastData)
    - _Requirements: 3.5_
  


  - [ ] 10.2 예측 실행 함수 및 UI 구현
    - runForecast 함수 작성 (POST /api/forecast/run 호출)
    - "예측 실행" 버튼 추가 (loading 중 비활성화)
    - 에러 메시지 표시 영역 추가



    - _Requirements: 3.5_
  
  - [ ] 10.3 차트 및 요약 통계 구현
    - formatChartData 함수 작성 (날짜 포맷 변환)
    - 모델별 LineChart 렌더링 (예측값, 상한, 하한 라인)


    - 요약 통계 카드 3개 추가 (평균 예측, 예측 기간, 총 예측량)
    - 한글 레이블 사용
    - _Requirements: 3.5, 3.6_




- [ ] 11. 홈 페이지에 예측 페이지 연결
  - `frontend/src/app/page.tsx` 수정
  - currentPage 상태에 'forecast' 추가
  - renderPage 함수에서 ForecastPage 렌더링


  - "생산량 예측" 카드 버튼 추가 (클릭 시 페이지 전환)
  - "홈으로 돌아가기" 버튼 추가
  - 브라우저에서 예측 실행 및 차트 표시 확인
  - _Requirements: 3.5, 3.6_



- [ ] 12. StubOptimizer 클래스 구현
  - [ ] 12.1 StubOptimizer 클래스 기본 구조 작성
    - `backend/optimizer.py` 생성
    - StubOptimizer 클래스 정의 (__init__에서 DataLoader, SimpleForecaster 인스턴스 생성)


    - _Requirements: 4.1_
  
  - [ ] 12.2 simple_line_assignment 메서드 구현
    - 라인별 지원 모델 파싱 (eligible_models 쉼표 분리)



    - 예측 데이터에서 주간 총 수요 계산 (첫 7일 합계)
    - 각 모델을 지원 가능한 라인에 균등 분배
    - mix_plan 리스트 생성 (period, line_id, model, planned_units, line_utilization)

    - KPI 계산 (total_demand, total_planned, fulfillment_rate)


    - _Requirements: 4.2, 4.3, 4.4_
  
  - [x] 12.3 run_optimization 메서드 및 테스트 함수 구현


    - 예측 실행 후 simple_line_assignment 호출
    - 결과 딕셔너리 반환 (status, mix_plan, kpi)
    - test_optimizer() 함수 작성 (총 생산량, 충족률 출력)
    - 스크립트 실행하여 최적화 결과 확인
    - _Requirements: 4.1, 4.5_



- [ ] 13. 믹스 최적화 API 엔드포인트 추가
  - `backend/app.py`에 StubOptimizer 인스턴스 생성
  - `POST /api/mix/optimize` 엔드포인트 구현
  - optimizer.run_optimization() 호출 및 결과 반환
  - curl 또는 Postman으로 엔드포인트 테스트

  - _Requirements: 4.5_



- [ ] 14. OptimizePage 컴포넌트 구현
  - [ ] 14.1 OptimizePage 컴포넌트 기본 구조 작성
    - `frontend/src/components/OptimizePage.tsx` 생성
    - 'use client' 지시어 추가


    - useState로 mixPlan, kpi, loading, error 상태 관리
    - TypeScript 인터페이스 정의 (MixPlan, KPI)
    - _Requirements: 4.6_



  
  - [ ] 14.2 최적화 실행 함수 및 KPI 카드 구현
    - runOptimization 함수 작성 (POST /api/mix/optimize 호출)
    - "최적화 실행" 버튼 추가

    - KPI 카드 4개 추가 (총 수요, 계획 생산, 충족률, 예상 비용)


    - _Requirements: 4.5, 4.7_
  
  - [ ] 14.3 차트 및 테이블 구현
    - 모델별 생산 비중 파이 차트 추가 (PieChart, Pie, Cell)
    - 라인별 계획 바 차트 추가 (BarChart, Bar)

    - 상세 계획 테이블 추가 (라인, 모델, 계획생산량, 가동률)
    - 한글 레이블 사용
    - _Requirements: 4.6, 4.7_


- [ ] 15. 홈 페이지에 최적화 페이지 연결
  - `frontend/src/app/page.tsx` 수정
  - currentPage 상태에 'optimize' 추가
  - renderPage 함수에서 OptimizePage 렌더링
  - "생산 믹스" 카드 버튼 추가 (클릭 시 페이지 전환)
  - 브라우저에서 최적화 실행 및 차트 표시 확인

  - _Requirements: 4.6, 4.7_

- [ ] 16. OR-Tools 설치
  - `backend` 폴더에서 `pip install ortools` 실행
  - requirements.txt 업데이트


  - _Requirements: 5.1_

- [x] 17. MilpOptimizer 클래스 구현



  - [ ] 17.1 MilpOptimizer 클래스 기본 구조 및 데이터 로딩
    - `backend/optimizer.py`에 MilpOptimizer 클래스 추가

    - __init__ 메서드 작성 (DataLoader, SimpleForecaster 인스턴스 생성)


    - run_optimization 메서드 시작 (데이터 로드 및 주간 수요 집계)
    - _Requirements: 5.1, 5.2_
  

  - [ ] 17.2 MILP 모델 변수 정의
    - OR-Tools SCIP 솔버 생성
    - Q[l,m,w] 변수 정의 (생산량, 정수)

    - Y[l,m,w] 변수 정의 (생산 여부, 불리언)

    - _Requirements: 5.2_
  
  - [ ] 17.3 MILP 제약 조건 구현
    - 라인당 주간 단일 모델 제약 (Σ_m Y[l,m,w] ≤ 1)

    - 생산량-생산여부 연결 제약 (Q[l,m,w] ≤ Y[l,m,w] * capacity)
    - 수요 충족 제약 (Σ_l Q[l,m,w] ≥ demand[m,w])
    - 라인 적격성 제약 (eligible_models 확인)
    - _Requirements: 5.3, 5.4, 5.5_

  
  - [ ] 17.4 목적 함수 및 솔버 실행
    - 목적 함수 정의 (생산 비용 최소화, 단가 1000 가정)

    - 솔버 실행 (Solve 호출)

    - 결과 파싱 (mix_plan, KPI 계산)
    - 에러 핸들링 (해 없음, 솔버 없음)
    - _Requirements: 5.6, 5.7, 5.8_

- [x] 18. optimizer.py에서 MILP 사용하도록 전환

  - `backend/app.py`에서 StubOptimizer 대신 MilpOptimizer 사용
  - 또는 환경 변수로 전환 가능하도록 구현
  - 브라우저에서 MILP 최적화 결과 확인
  - _Requirements: 5.1-5.8_

- [ ] 19. StubScheduler 클래스 구현
  - [ ] 19.1 StubScheduler 클래스 기본 구조 작성
    - `backend/scheduler.py` 생성
    - StubScheduler 클래스 정의 (__init__에서 DataLoader 인스턴스 생성)
    - _Requirements: 6.1_
  
  - [ ] 19.2 run_stub_schedule 메서드 구현
    - mix_plan을 입력으로 받음
    - 필요 인원 산정 (100대당 1명, 주간/야간 2교대)
    - 작업자를 연차 높은 순으로 정렬
    - Greedy 방식으로 작업자 배정
    - schedule 리스트 생성 (date, line_id, shift, worker_id, worker_name)
    - 결과 딕셔너리 반환 (status, schedule)
    - _Requirements: 6.2, 6.3, 6.4_

- [ ] 20. 스케줄링 API 엔드포인트 추가
  - `backend/app.py`에 StubScheduler 인스턴스 생성
  - `POST /api/schedule/run` 엔드포인트 구현 (body로 mix_plan 받음)
  - scheduler.run_stub_schedule(mix_plan) 호출 및 결과 반환
  - curl 또는 Postman으로 엔드포인트 테스트
  - _Requirements: 6.5_

- [ ] 21. SchedulePage 컴포넌트 구현
  - [ ] 21.1 SchedulePage 컴포넌트 기본 구조 작성
    - `frontend/src/components/SchedulePage.tsx` 생성

    - 'use client' 지시어 추가


    - useState로 schedule, kpi, loading, error 상태 관리
    - TypeScript 인터페이스 정의 (ScheduleItem, ScheduleKPI)
    - _Requirements: 6.6_
  

  - [ ] 21.2 스케줄링 실행 함수 및 테이블 구현
    - runScheduling 함수 작성 (POST /api/schedule/run 호출, mix_plan 전달)
    - "스케줄링 실행" 버튼 추가
    - 스케줄 테이블 추가 (날짜, 라인, 교대, 작업자 ID, 작업자 이름)
    - _Requirements: 6.5, 6.6_


- [ ] 22. OptimizePage에서 SchedulePage로 연결
  - OptimizePage에 "이 계획으로 스케줄링" 버튼 추가

  - 버튼 클릭 시 mixPlan을 전달하며 schedule 페이지로 이동
  - 홈 페이지에 "인력 스케줄링" 카드 추가
  - 브라우저에서 예측 → 믹스 → 스케줄링 전체 플로우 테스트
  - _Requirements: 6.6_


- [ ] 23. CpsatScheduler 클래스 구현
  - [ ] 23.1 CpsatScheduler 클래스 기본 구조 및 데이터 준비
    - `backend/scheduler.py`에 CpsatScheduler 클래스 추가
    - __init__ 메서드 작성

    - run_cpsat_schedule 메서드 시작 (mix_plan 입력, 데이터 로드)
    - 필요 인원 산정 및 날짜/교대 리스트 생성
    - _Requirements: 7.1_
  

  - [ ] 23.2 CP-SAT 모델 변수 정의
    - OR-Tools CP-SAT 모델 생성
    - x[w,d,s] 변수 정의 (작업자-날짜-교대 근무 여부, 불리언)
    - _Requirements: 7.2_
  
  - [ ] 23.3 CP-SAT 제약 조건 구현
    - 하루 최대 1교대 제약 (Σ_s x[w,d,s] ≤ 1)
    - 주간 최대 근무시간 제약 (Σ_d,s (x[w,d,s] * 8) ≤ max_hours_week)
    - 연속 야간 근무 제한 (3일 이하)
    - 라인별 필요 인원 충족 제약
    - _Requirements: 7.3, 7.4, 7.5_
  
  - [ ] 23.4 목적 함수 및 솔버 실행
    - 목적 함수 정의 (총 인건비 + 선호도 위반 페널티 최소화)
    - 솔버 실행 (Solve 호출)
    - 결과 파싱 (schedule, KPI 계산)
    - 에러 핸들링
    - _Requirements: 7.6, 7.7_

- [ ] 24. scheduler.py에서 CP-SAT 사용하도록 전환
  - `backend/app.py`에서 StubScheduler 대신 CpsatScheduler 사용
  - 또는 환경 변수로 전환 가능하도록 구현
  - _Requirements: 7.1-7.7_

- [ ] 25. SchedulePage에 KPI 카드 추가
  - KPI 카드 3개 추가 (총 인건비, 총 OT 시간, 야간 편중 지수)
  - 브라우저에서 CP-SAT 스케줄링 결과 및 KPI 확인
  - _Requirements: 7.8_

- [ ] 26. 워크플로우 원클릭 체이닝 구현
  - [ ] 26.1 ForecastPage에 "이 결과로 믹스 최적화" 버튼 추가
    - 버튼 클릭 시 자동으로 optimize 페이지로 이동
    - 페이지 로드 시 자동으로 최적화 실행
    - _Requirements: 8.1_
  
  - [ ] 26.2 OptimizePage에 "이 계획으로 스케줄링" 버튼 추가
    - 버튼 클릭 시 자동으로 schedule 페이지로 이동
    - 페이지 로드 시 자동으로 스케줄링 실행 (mix_plan 전달)
    - _Requirements: 8.2_

- [ ] 27. 백엔드 에러 핸들링 강화
  - [ ] 27.1 DataLoader 에러 메시지 개선
    - 필수 컬럼 누락 시 구체적인 컬럼명 포함
    - 결측치 존재 시 명확한 메시지
    - _Requirements: 8.3, 8.4_
  
  - [ ] 27.2 Solver 에러 핸들링 추가
    - 솔버 타임아웃 시 "제약 조건을 완화해보세요" 제안
    - 해 없음 시 suggestion 필드 추가
    - _Requirements: 8.5_
  
  - [ ] 27.3 모든 API 엔드포인트에 try-except 추가
    - 예외 발생 시 서버 중단 방지
    - {"status": "error", "message": str(e)} 반환
    - _Requirements: 8.7_

- [ ] 28. 프론트엔드 에러 핸들링 강화
  - [ ] 28.1 API 호출 에러 처리 개선
    - 모든 fetch 호출을 try-catch로 감싸기
    - data.status === 'error' 확인 및 에러 메시지 표시
    - suggestion 필드 있으면 함께 표시
    - _Requirements: 8.3, 8.4, 8.5_
  
  - [ ] 28.2 사용자 피드백 UI 개선
    - 에러 메시지를 빨간색 박스로 표시
    - 로딩 중 버튼 비활성화 및 "실행중..." 텍스트
    - API 호출 실패 시 "백엔드 서버를 확인하세요" 메시지
    - _Requirements: 8.6_

- [ ] 29. 홈 대시보드 개선
  - [ ] 29.1 핵심 KPI 카드 4개 추가
    - 예측 정확도, 비용 절감률, OT 감소율, 충족률 카드
    - 각 API에서 KPI 데이터 가져오기
    - _Requirements: 9.1_
  
  - [ ] 29.2 워크플로우 Progress Bar 추가
    - 예측 → 믹스 → 스케줄링 진행 상황 시각화
    - 현재 단계 하이라이트
    - _Requirements: 9.2_

- [ ] 30. 각 페이지에 설명 박스 추가
  - ForecastPage, OptimizePage, SchedulePage에 "이 화면은 무엇을 해결하나요?" 설명 추가
  - 자동차 부품 산업 용어 사용
  - _Requirements: 9.3, 9.4_

- [ ] 31. 네비게이션 개선
  - 모든 페이지에 "홈으로 돌아가기" 버튼 표시
  - 버튼 스타일 통일
  - _Requirements: 9.5_

- [ ] 32. 차트 한글화
  - 모든 차트의 레이블, 툴팁을 한글로 변경
  - 날짜 포맷을 한국 형식으로 변경
  - _Requirements: 9.6_

- [ ] 33. README.md 작성
  - [ ] 33.1 프로젝트 개요 및 기술 스택 작성
    - LineMind MVP 소개
    - 핵심 기능 설명
    - 기술 스택 리스트 (FastAPI, Next.js, OR-Tools, Recharts)
    - _Requirements: 10.1_
  
  - [ ] 33.2 설치 및 실행 방법 작성
    - 백엔드 설치 및 실행 명령어
    - 프론트엔드 설치 및 실행 명령어
    - 필수 요구사항 (Python 3.9+, Node.js 18+)
    - _Requirements: 10.1_
  
  - [ ] 33.3 개발 단계 체크리스트 추가
    - STEP 0-9 각 단계의 체크리스트
    - 각 단계의 커밋 메시지 예시
    - _Requirements: 10.2_

- [ ] 34. 의존성 파일 최종 확인
  - backend/requirements.txt 모든 의존성 포함 확인
  - frontend/package.json 모든 의존성 포함 확인
  - _Requirements: 10.3_

- [ ] 35. 스크린샷 및 문서 준비
  - 주요 화면 스크린샷 캡처 (홈, 예측, 믹스, 스케줄링)
  - docs 폴더에 이미지 저장
  - 가능하면 전체 플로우 GIF 생성
  - _Requirements: 10.4_

- [ ] 36. .gitignore 파일 확인
  - venv, node_modules, __pycache__, .next, .env 제외 확인
  - CSV 파일은 포함 (시드 데이터)
  - _Requirements: 10.5_

- [ ] 37. 최종 커밋 및 검토
  - 모든 변경사항 커밋
  - 의미 있는 커밋 메시지 사용 (feat, fix, docs 등)
  - Git 로그 확인
  - _Requirements: 10.6_

- [ ] 38. 전체 플로우 E2E 테스트
  - 백엔드 서버 실행 확인
  - 프론트엔드 서버 실행 확인
  - 홈 → 예측 → 믹스 → 스케줄링 전체 플로우 테스트
  - 각 단계에서 차트 및 KPI 표시 확인
  - 에러 시나리오 테스트 (잘못된 CSV, 솔버 실패 등)
  - _Requirements: 1.1-10.6_
