"""
LineMind API - FastAPI 백엔드 애플리케이션

이 모듈은 LineMind MVP의 메인 API 서버입니다.
생산 예측, 믹스 최적화, 인력 스케줄링 기능을 제공하는 RESTful API 엔드포인트를 정의합니다.

주요 엔드포인트:
- GET /health: 서버 상태 확인
- GET /api/data/status: 데이터 로딩 상태 확인
- POST /api/forecast/run: 생산량 예측 실행
- POST /api/mix/optimize: 생산 믹스 최적화 실행
- POST /api/schedule/run: 인력 스케줄링 실행
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from data_loader import DataLoader
from forecast import SimpleForecaster

# FastAPI 애플리케이션 인스턴스 생성
# title: API 문서에 표시될 제목
# version: API 버전 정보
app = FastAPI(
    title="LineMind API",
    version="1.0.0",
    description="AI 기반 생산 관리 시스템 API"
)

# DataLoader 인스턴스 생성
# 모든 API 엔드포인트에서 공유하여 사용
data_loader = DataLoader()

# SimpleForecaster 인스턴스 생성
# 생산량 예측 기능 제공
forecaster = SimpleForecaster()

# CORS (Cross-Origin Resource Sharing) 미들웨어 설정
# 프론트엔드(localhost:3000)에서 백엔드 API를 호출할 수 있도록 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js 개발 서버 주소
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용 (GET, POST, PUT, DELETE 등)
    allow_headers=["*"],  # 모든 HTTP 헤더 허용
)


@app.get("/health")
async def health_check():
    """
    서버 상태 확인 엔드포인트
    
    프론트엔드에서 백엔드 서버가 정상적으로 실행 중인지 확인하는 용도로 사용됩니다.
    
    Returns:
        dict: 서버 상태 정보
            - status (str): 서버 상태 메시지
            - message (str): 추가 정보
    
    Example:
        GET /health
        Response: {"status": "LineMind API is running", "message": "Hello World"}
    """
    return {
        "status": "LineMind API is running",
        "message": "Hello World"
    }


@app.get("/api/data/status")
async def data_status():
    """
    데이터 로딩 상태 확인 엔드포인트
    
    모든 CSV 파일을 로드하고 각 데이터셋의 행 개수를 반환합니다.
    데이터 로딩에 실패하면 에러 메시지를 반환합니다.
    
    Returns:
        dict: 데이터 상태 정보
            성공 시:
                - status (str): "success"
                - data_counts (dict): 각 데이터셋의 행 개수
            실패 시:
                - status (str): "error"
                - message (str): 에러 메시지
    
    Example:
        GET /api/data/status
        Success Response: {
            "status": "success",
            "data_counts": {
                "production": 19,
                "lines": 3,
                "workers": 7,
                "costs": 6
            }
        }
        Error Response: {
            "status": "error",
            "message": "CSV 파일이 없습니다: data/seed/lines.csv"
        }
    """
    try:
        # DataLoader를 사용하여 모든 데이터 로드
        data = data_loader.load_all_data()
        
        # 각 데이터셋의 행 개수 계산
        data_counts = {name: len(df) for name, df in data.items()}
        
        # 성공 응답 반환
        return {
            "status": "success",
            "data_counts": data_counts
        }
    except Exception as e:
        # 에러 발생 시 에러 응답 반환
        # 서버가 중단되지 않고 에러 메시지만 반환
        return {
            "status": "error",
            "message": str(e)
        }


@app.post("/api/forecast/run")
async def run_forecast():
    """
    생산량 예측 실행 엔드포인트
    
    모든 모델에 대해 30일간의 생산량 예측을 실행합니다.
    이동평균 알고리즘을 사용하여 과거 생산 이력을 기반으로 미래 수요를 예측합니다.
    
    Returns:
        dict: 예측 결과
            성공 시:
                - status (str): "success"
                - forecasts (dict): 모델별 예측 데이터
                    - date (str): 예측 날짜 (YYYY-MM-DD)
                    - model (str): 모델명
                    - forecast_units (int): 예측 생산량
                    - conf_lo (int): 신뢰구간 하한
                    - conf_hi (int): 신뢰구간 상한
                - message (str): 성공 메시지
            실패 시:
                - status (str): "error"
                - message (str): 에러 메시지
    
    Example:
        POST /api/forecast/run
        Response: {
            "status": "success",
            "forecasts": {
                "ModelA": [
                    {
                        "date": "2024-01-08",
                        "model": "ModelA",
                        "forecast_units": 125,
                        "conf_lo": 100,
                        "conf_hi": 150
                    },
                    ...
                ],
                "ModelB": [...],
                "ModelC": [...]
            },
            "message": "3개 모델 예측 완료"
        }
    """
    # SimpleForecaster를 사용하여 예측 실행
    # 모든 에러 핸들링은 forecaster 내부에서 처리됨
    return forecaster.run_forecast_all_models()


# 애플리케이션 실행 진입점
# 이 파일을 직접 실행할 때만 uvicorn 서버를 시작합니다
if __name__ == "__main__":
    import uvicorn
    
    # uvicorn 서버 실행
    # - app: FastAPI 애플리케이션 인스턴스
    # - host: 0.0.0.0으로 설정하여 외부 접근 허용
    # - port: 8000번 포트 사용
    # - reload: 코드 변경 시 자동 재시작 (개발 모드)
    uvicorn.run(app, host="0.0.0.0", port=8000)
