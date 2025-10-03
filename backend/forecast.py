"""
LineMind 생산량 예측 모듈

이동평균 기반의 간단한 예측 알고리즘을 사용하여 각 모델의 미래 생산량을 예측합니다.
Phase 1에서는 이동평균을 사용하고, Phase 2에서는 Prophet 또는 ARIMA 같은 고급 알고리즘으로 대체할 수 있습니다.

주요 기능:
- 최근 7일 이동평균 계산
- 정규분포 노이즈 추가로 변동성 반영
- 신뢰구간 계산 (예측값 ± 20%)
- 과거 데이터가 없는 모델에 대한 기본값 제공
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from data_loader import DataLoader


class SimpleForecaster:
    """
    이동평균 기반의 간단한 생산량 예측 클래스
    
    Attributes:
        data_loader (DataLoader): CSV 데이터를 로드하는 DataLoader 인스턴스
    """
    
    def __init__(self):
        """
        SimpleForecaster 초기화
        
        DataLoader 인스턴스를 생성하여 생산 이력 데이터에 접근할 수 있도록 합니다.
        """
        self.data_loader = DataLoader()

    
    def moving_average_forecast(self, df: pd.DataFrame, model: str, periods: int = 30) -> pd.DataFrame:
        """
        특정 모델에 대한 이동평균 기반 예측을 생성합니다.
        
        알고리즘:
        1. 해당 모델의 과거 생산 데이터 필터링
        2. 날짜별 총 생산량 계산 (여러 교대의 합계)
        3. 최근 7일 이동평균 계산
        4. 정규분포 노이즈 추가 (표준편차 = 평균 * 0.1)
        5. 신뢰구간 계산 (예측값 * 0.8 ~ 예측값 * 1.2)
        
        Args:
            df (pd.DataFrame): 생산 이력 데이터프레임
            model (str): 예측할 모델명 (예: "ModelA")
            periods (int): 예측 기간 (일 단위, 기본값: 30일)
        
        Returns:
            pd.DataFrame: 예측 결과 데이터프레임
                - date: 예측 날짜
                - model: 모델명
                - forecast_units: 예측 생산량
                - conf_lo: 신뢰구간 하한 (예측값 * 0.8)
                - conf_hi: 신뢰구간 상한 (예측값 * 1.2)
        
        Example:
            >>> forecaster = SimpleForecaster()
            >>> data = forecaster.data_loader.load_all_data()
            >>> forecast_df = forecaster.moving_average_forecast(data['production'], 'ModelA', 30)
        """
        # 1. 해당 모델의 데이터만 필터링
        model_data = df[df['model'] == model].copy()
        
        # 2. 과거 데이터가 없는 경우 기본값 반환
        if len(model_data) == 0:
            # 현재 날짜부터 periods일간의 날짜 생성
            dates = pd.date_range(datetime.now(), periods=periods, freq='D')
            
            # 기본값 100 units/day로 예측 생성
            return pd.DataFrame({
                'date': dates,
                'model': model,
                'forecast_units': [100] * periods,  # 기본 예측값
                'conf_lo': [80] * periods,          # 하한 (100 * 0.8)
                'conf_hi': [120] * periods          # 상한 (100 * 1.2)
            })
        
        # 3. 날짜별 총 생산량 계산
        # 같은 날짜에 여러 교대(Day, Night)가 있을 수 있으므로 합산
        daily_production = model_data.groupby('date')['produced_units'].sum()
        
        # 4. 최근 7일 이동평균 계산
        # 데이터가 7일 미만이면 가능한 모든 데이터 사용
        window_size = min(7, len(daily_production))
        recent_avg = daily_production.tail(window_size).mean()
        
        # 5. 미래 날짜 생성
        # 마지막 생산 날짜 다음날부터 periods일간
        last_date = pd.to_datetime(daily_production.index[-1])
        future_dates = pd.date_range(
            last_date + timedelta(days=1),
            periods=periods,
            freq='D'
        )
        
        # 6. 예측값 생성 (이동평균 + 정규분포 노이즈)
        # 재현 가능한 결과를 위해 시드 고정
        np.random.seed(42)
        
        # 정규분포 노이즈: 평균 0, 표준편차 = recent_avg * 0.1
        noise = np.random.normal(0, recent_avg * 0.1, periods)
        forecast_values = recent_avg + noise
        
        # 음수 제거 (생산량은 0 이상이어야 함)
        forecast_values = np.maximum(forecast_values, 0)
        
        # 7. 신뢰구간 계산
        # 하한: 예측값 * 0.8
        # 상한: 예측값 * 1.2
        conf_lo = forecast_values * 0.8
        conf_hi = forecast_values * 1.2
        
        # 8. 결과 데이터프레임 생성
        return pd.DataFrame({
            'date': future_dates,
            'model': model,
            'forecast_units': forecast_values.round().astype(int),
            'conf_lo': conf_lo.round().astype(int),
            'conf_hi': conf_hi.round().astype(int)
        })

    
    def run_forecast_all_models(self) -> dict:
        """
        모든 모델에 대한 예측을 실행합니다.
        
        생산 이력 데이터에서 모든 고유 모델을 찾아 각각에 대해 30일 예측을 생성합니다.
        
        Returns:
            dict: 예측 결과 딕셔너리
                성공 시:
                    - status (str): "success"
                    - forecasts (dict): 모델명을 키로, 예측 데이터 리스트를 값으로 하는 딕셔너리
                    - message (str): 성공 메시지
                실패 시:
                    - status (str): "error"
                    - message (str): 에러 메시지
        
        Example:
            >>> forecaster = SimpleForecaster()
            >>> result = forecaster.run_forecast_all_models()
            >>> if result['status'] == 'success':
            >>>     for model, forecast in result['forecasts'].items():
            >>>         print(f"{model}: {len(forecast)}일 예측")
        """
        try:
            # 1. 모든 데이터 로드
            data = self.data_loader.load_all_data()
            production_df = data['production']
            
            # 2. 생산 이력에서 고유 모델 목록 추출
            models = production_df['model'].unique()
            
            # 3. 각 모델에 대해 예측 실행
            forecasts = {}
            for model in models:
                # 예측 실행
                forecast_df = self.moving_average_forecast(production_df, model)
                
                # 데이터프레임을 딕셔너리 리스트로 변환
                # 날짜를 문자열로 변환하여 JSON 직렬화 가능하도록 함
                forecast_df['date'] = forecast_df['date'].dt.strftime('%Y-%m-%d')
                forecasts[model] = forecast_df.to_dict('records')
            
            # 4. 성공 응답 반환
            return {
                "status": "success",
                "forecasts": forecasts,
                "message": f"{len(models)}개 모델 예측 완료"
            }
            
        except Exception as e:
            # 에러 발생 시 에러 응답 반환
            return {
                "status": "error",
                "message": str(e)
            }


def test_forecast():
    """
    SimpleForecaster의 기능을 테스트하는 함수
    
    모든 모델에 대한 예측을 실행하고 결과를 출력합니다.
    """
    # SimpleForecaster 인스턴스 생성
    forecaster = SimpleForecaster()
    
    # 예측 실행
    result = forecaster.run_forecast_all_models()
    
    # 결과 출력
    print(f"예측 결과: {result['status']}")
    
    if result['status'] == 'success':
        # 성공 시 각 모델의 예측 일수 출력
        for model, forecast in result['forecasts'].items():
            print(f"  {model}: {len(forecast)}일 예측")
    else:
        # 실패 시 에러 메시지 출력
        print(f"  에러: {result['message']}")


# 이 파일을 직접 실행할 때만 테스트 함수 실행
if __name__ == "__main__":
    test_forecast()
