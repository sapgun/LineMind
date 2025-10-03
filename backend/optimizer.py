"""
LineMind 생산 믹스 최적화 모듈

예측된 수요를 바탕으로 각 라인에 어떤 모델을 배정할지 결정합니다.
Phase 1에서는 간단한 균등 분배 방식(Stub)을 사용하고,
Phase 2에서는 OR-Tools MILP를 사용하여 체인지오버 비용과 용량을 고려한 최적화를 수행합니다.

주요 기능:
- 예측 결과를 자동으로 가져와서 사용
- 라인별 지원 가능 모델 확인
- 수요를 여러 라인에 균등 분배
- KPI 계산 (총 수요, 계획 생산, 충족률)
"""

import pandas as pd
from data_loader import DataLoader
from forecast import SimpleForecaster
from typing import Dict, List


class StubOptimizer:
    """
    간단한 균등 분배 방식의 생산 믹스 최적화 클래스
    
    실제 최적화 알고리즘 없이 수요를 지원 가능한 라인에 균등하게 분배합니다.
    전체 플로우를 검증하기 위한 더미 구현입니다.
    
    Attributes:
        data_loader (DataLoader): CSV 데이터를 로드하는 DataLoader 인스턴스
        forecaster (SimpleForecaster): 생산량 예측을 수행하는 Forecaster 인스턴스
    """
    
    def __init__(self):
        """
        StubOptimizer 초기화
        
        DataLoader와 SimpleForecaster 인스턴스를 생성합니다.
        """
        self.data_loader = DataLoader()
        self.forecaster = SimpleForecaster()

    
    def simple_line_assignment(self, forecast_data: dict) -> dict:
        """
        간단한 라인 배정 알고리즘 (균등 분배)
        
        각 모델의 수요를 해당 모델을 생산할 수 있는 라인들에 균등하게 분배합니다.
        실제 최적화 없이 단순 분배만 수행하는 더미 구현입니다.
        
        알고리즘:
        1. 라인별 지원 가능 모델 파싱
        2. 예측 데이터에서 주간 총 수요 계산 (첫 7일)
        3. 각 모델을 지원 가능한 라인에 균등 분배
        4. KPI 계산 (총 수요, 계획 생산, 충족률)
        
        Args:
            forecast_data (dict): 모델별 예측 데이터
                - key: 모델명
                - value: 예측 데이터 리스트 (date, model, forecast_units, conf_lo, conf_hi)
        
        Returns:
            dict: 최적화 결과
                성공 시:
                    - status (str): "success"
                    - mix_plan (list): 생산 계획 리스트
                        - period (int): 주차 (1주차)
                        - line_id (str): 라인 ID
                        - model (str): 모델명
                        - planned_units (int): 계획 생산량
                        - line_utilization (float): 라인 가동률 (0~1)
                    - kpi (dict): 핵심 성과 지표
                        - total_demand (int): 총 수요
                        - total_planned (int): 계획 생산량
                        - fulfillment_rate (float): 수요 충족률 (%)
                        - total_changeovers (int): 체인지오버 횟수 (더미에서는 0)
                        - estimated_cost (int): 예상 비용
                실패 시:
                    - status (str): "error"
                    - message (str): 에러 메시지
        """
        try:
            # 1. 기본 데이터 로드
            data = self.data_loader.load_all_data()
            lines_df = data['lines']
            
            # 2. 라인별 지원 가능 모델 파싱
            # eligible_models는 "ModelA,ModelB" 형식의 문자열이므로 쉼표로 분리
            line_models = {}
            for _, line in lines_df.iterrows():
                line_id = line['line_id']
                eligible = line['eligible_models'].split(',')
                # 공백 제거하여 모델 리스트 생성
                line_models[line_id] = [model.strip() for model in eligible]
            
            # 3. 예측 데이터에서 주간 총 수요 계산
            # 첫 주 (7일) 수요만 사용
            model_demands = {}
            for model, forecast_list in forecast_data.items():
                # 첫 7일의 예측값 합계
                week1_demand = sum(item['forecast_units'] for item in forecast_list[:7])
                model_demands[model] = week1_demand
            
            # 4. 각 모델을 지원 가능한 라인에 균등 분배
            mix_plan = []
            for model, total_demand in model_demands.items():
                # 이 모델을 생산할 수 있는 라인 찾기
                capable_lines = [
                    line for line, models in line_models.items() 
                    if model in models
                ]
                
                if capable_lines:
                    # 수요를 라인 개수로 나누어 균등 분배
                    demand_per_line = total_demand // len(capable_lines)
                    remainder = total_demand % len(capable_lines)
                    
                    for i, line_id in enumerate(capable_lines):
                        # 기본 배정량
                        planned_units = demand_per_line
                        
                        # 나머지를 첫 번째 라인들에 분배
                        if i < remainder:
                            planned_units += 1
                        
                        # 라인 가동률 계산
                        # 가동률 = 계획 생산량 / (일일 용량 * 7일)
                        line_capacity = lines_df[lines_df['line_id'] == line_id]['base_daily_capacity'].iloc[0]
                        weekly_capacity = line_capacity * 7
                        line_utilization = min(planned_units / weekly_capacity, 1.0)
                        
                        # 생산 계획 추가
                        mix_plan.append({
                            'period': 1,  # 1주차
                            'line_id': line_id,
                            'model': model,
                            'planned_units': planned_units,
                            'line_utilization': round(line_utilization, 2)
                        })
            
            # 5. KPI 계산
            total_planned = sum(item['planned_units'] for item in mix_plan)
            total_demand = sum(model_demands.values())
            
            # 수요 충족률 계산 (%)
            fulfillment_rate = (total_planned / total_demand * 100) if total_demand > 0 else 100
            
            # 6. 결과 반환
            return {
                "status": "success",
                "mix_plan": mix_plan,
                "kpi": {
                    "total_demand": total_demand,
                    "total_planned": total_planned,
                    "fulfillment_rate": round(fulfillment_rate, 1),
                    "total_changeovers": 0,  # 더미 단계에서는 0
                    "estimated_cost": total_planned * 1000  # 임시 단위 비용 (1000원/대)
                }
            }
            
        except Exception as e:
            # 에러 발생 시 에러 응답 반환
            return {
                "status": "error",
                "message": str(e)
            }

    
    def run_optimization(self) -> dict:
        """
        최적화 실행 (예측 + 배정)
        
        1. 먼저 예측을 실행하여 각 모델의 수요를 파악합니다.
        2. 예측 결과를 바탕으로 라인별 생산 계획을 수립합니다.
        
        Returns:
            dict: 최적화 결과
                - status (str): "success" 또는 "error"
                - mix_plan (list): 생산 계획 (성공 시)
                - kpi (dict): KPI (성공 시)
                - message (str): 에러 메시지 (실패 시)
        """
        # 1. 먼저 예측 실행
        forecast_result = self.forecaster.run_forecast_all_models()
        
        # 예측 실패 시 에러 반환
        if forecast_result['status'] != 'success':
            return forecast_result
        
        # 2. 예측 결과로 생산 믹스 계산
        return self.simple_line_assignment(forecast_result['forecasts'])


def test_optimizer():
    """
    StubOptimizer의 기능을 테스트하는 함수
    
    최적화를 실행하고 결과를 출력합니다.
    """
    # StubOptimizer 인스턴스 생성
    optimizer = StubOptimizer()
    
    # 최적화 실행
    result = optimizer.run_optimization()
    
    # 결과 출력
    print(f"최적화 결과: {result['status']}")
    
    if result['status'] == 'success':
        # 성공 시 KPI 출력
        print(f"  계획된 총 생산량: {result['kpi']['total_planned']}")
        print(f"  수요 충족률: {result['kpi']['fulfillment_rate']}%")
        print(f"  생산 계획 항목 수: {len(result['mix_plan'])}")
    else:
        # 실패 시 에러 메시지 출력
        print(f"  에러: {result['message']}")


# 이 파일을 직접 실행할 때만 테스트 함수 실행
if __name__ == "__main__":
    test_optimizer()
