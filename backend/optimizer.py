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



class MilpOptimizer:
    """
    MILP(Mixed Integer Linear Programming) 기반 생산 믹스 최적화 클래스
    
    OR-Tools의 SCIP 솔버를 사용하여 체인지오버 비용과 라인 용량을 고려한
    실제 최적화를 수행합니다.
    
    최적화 목표:
    - 총 비용(생산 비용 + 체인지오버 비용) 최소화
    
    제약 조건:
    - 라인당 주간 단일 모델 생산
    - 라인 용량 제한
    - 수요 충족
    - 라인별 지원 가능 모델 제한
    
    Attributes:
        data_loader (DataLoader): CSV 데이터를 로드하는 DataLoader 인스턴스
        forecaster (SimpleForecaster): 생산량 예측을 수행하는 Forecaster 인스턴스
    """
    
    def __init__(self):
        """
        MilpOptimizer 초기화
        
        DataLoader와 SimpleForecaster 인스턴스를 생성합니다.
        """
        self.data_loader = DataLoader()
        self.forecaster = SimpleForecaster()
    
    def run_optimization(self) -> dict:
        """
        MILP 최적화 실행
        
        1. 데이터 로드 및 전처리
        2. MILP 모델 생성 및 변수 정의
        3. 제약 조건 추가
        4. 목적 함수 정의
        5. 솔버 실행
        6. 결과 파싱 및 KPI 계산
        
        Returns:
            dict: 최적화 결과
                성공 시:
                    - status (str): "success"
                    - mix_plan (list): 생산 계획
                    - kpi (dict): KPI
                실패 시:
                    - status (str): "error"
                    - message (str): 에러 메시지
        """
        try:
            # 1. 데이터 로드
            data = self.data_loader.load_all_data()
            lines_df = data['lines']
            costs_df = data['costs']
            
            # 예측 실행
            forecast_result = self.forecaster.run_forecast_all_models()
            if forecast_result['status'] != 'success':
                return forecast_result
            
            # 2. 주간 수요 집계 (첫 4주)
            demands = {}
            for model, forecast in forecast_result['forecasts'].items():
                demands[model] = {}
                for week in range(4):
                    start_day = week * 7
                    end_day = start_day + 7
                    # 해당 주의 예측값 합계
                    weekly_demand = sum(
                        d['forecast_units'] 
                        for d in forecast[start_day:end_day] 
                        if start_day <= forecast.index(d) < end_day
                    )
                    demands[model][week] = weekly_demand
            
            # 3. MILP 모델 생성
            from ortools.linear_solver import pywraplp
            
            # SCIP 솔버 생성
            solver = pywraplp.Solver.CreateSolver('SCIP')
            if not solver:
                return {
                    "status": "error",
                    "message": "SCIP 솔버를 사용할 수 없습니다. OR-Tools가 올바르게 설치되었는지 확인하세요."
                }
            
            # 4. 변수 정의
            # 라인, 모델, 주차 리스트
            lines = lines_df['line_id'].tolist()
            models = list(demands.keys())
            weeks = range(4)  # 4주
            
            # Q[l, m, w]: 라인 l에서 모델 m을 주차 w에 생산하는 수량 (정수 변수)
            Q = {}
            # Y[l, m, w]: 라인 l에서 모델 m을 주차 w에 생산하면 1, 아니면 0 (불리언 변수)
            Y = {}
            
            for l in lines:
                for m in models:
                    for w in weeks:
                        # 최대 생산량 = 일일 용량 * 7일
                        max_prod = lines_df[lines_df['line_id'] == l]['base_daily_capacity'].iloc[0] * 7
                        
                        # 생산량 변수 (0 ~ max_prod)
                        Q[l, m, w] = solver.IntVar(0, max_prod, f'Q_{l}_{m}_{w}')
                        
                        # 생산 여부 변수 (0 또는 1)
                        Y[l, m, w] = solver.BoolVar(f'Y_{l}_{m}_{w}')
            
            # 5. 제약 조건 추가
            
            # 제약 1: 라인당 주간 단일 모델 생산
            # 각 라인은 한 주에 최대 하나의 모델만 생산할 수 있음
            for l in lines:
                for w in weeks:
                    solver.Add(sum(Y[l, m, w] for m in models) <= 1)
            
            # 제약 2: 생산량-생산여부 연결
            # 모델을 생산하지 않으면 (Y=0) 생산량도 0이어야 함
            # 모델을 생산하면 (Y=1) 생산량은 최대 용량까지 가능
            for l in lines:
                for m in models:
                    for w in weeks:
                        max_prod = lines_df[lines_df['line_id'] == l]['base_daily_capacity'].iloc[0] * 7
                        solver.Add(Q[l, m, w] <= Y[l, m, w] * max_prod)
            
            # 제약 3: 수요 충족
            # 각 모델의 주간 수요는 모든 라인의 생산량 합으로 충족되어야 함
            for m in models:
                for w in weeks:
                    if m in demands and w in demands[m]:
                        solver.Add(sum(Q[l, m, w] for l in lines) >= demands[m][w])
            
            # 제약 4: 라인 적격성
            # 각 라인은 지원 가능한 모델만 생산할 수 있음
            for l in lines:
                # 라인의 지원 가능 모델 리스트
                eligible = lines_df[lines_df['line_id'] == l]['eligible_models'].iloc[0].split(',')
                eligible_models = [m.strip() for m in eligible]
                
                for m in models:
                    if m not in eligible_models:
                        # 지원하지 않는 모델은 생산 불가
                        for w in weeks:
                            solver.Add(Y[l, m, w] == 0)
            
            # 6. 목적 함수: 총 비용 최소화
            objective = solver.Objective()
            objective.SetMinimization()
            
            # 생산 비용 (단순화: 모델별 생산 단가 1000원/대)
            for l in lines:
                for m in models:
                    for w in weeks:
                        objective.SetCoefficient(Q[l, m, w], 1000)
            
            # 체인지오버 비용은 Phase 1에서는 생략 (단순화)
            # Phase 2에서 추가 구현 가능
            
            # 7. 솔버 실행
            status = solver.Solve()
            
            # 8. 결과 파싱
            if status == pywraplp.Solver.OPTIMAL:
                # 최적해를 찾은 경우
                mix_plan = []
                total_planned = 0
                
                for w in weeks:
                    for l in lines:
                        for m in models:
                            # Y 값이 1이면 (해당 모델을 생산하면)
                            if Y[l, m, w].solution_value() > 0.5:
                                planned_units = int(Q[l, m, w].solution_value())
                                total_planned += planned_units
                                
                                # 라인 가동률 계산
                                line_capacity = lines_df[lines_df['line_id'] == l]['base_daily_capacity'].iloc[0]
                                weekly_capacity = line_capacity * 7
                                line_utilization = min(planned_units / weekly_capacity, 1.0)
                                
                                mix_plan.append({
                                    'period': w + 1,  # 1주차부터 시작
                                    'line_id': l,
                                    'model': m,
                                    'planned_units': planned_units,
                                    'line_utilization': round(line_utilization, 2)
                                })
                
                # KPI 계산
                total_demand = sum(d for m_d in demands.values() for d in m_d.values())
                fulfillment_rate = (total_planned / total_demand * 100) if total_demand > 0 else 100
                
                return {
                    "status": "success",
                    "mix_plan": mix_plan,
                    "kpi": {
                        "total_cost": int(solver.Objective().Value()),
                        "changeovers": 0,  # Phase 1에서는 계산 생략
                        "changeover_hours": 0,
                        "fulfillment_rate": round(fulfillment_rate, 1),
                        "estimated_ot": 0
                    }
                }
            else:
                # 최적해를 찾지 못한 경우
                return {
                    "status": "error",
                    "message": "최적해를 찾을 수 없습니다. 제약 조건을 완화해보세요.",
                    "suggestion": "수요를 줄이거나 라인 용량을 늘려보세요."
                }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"최적화 실패: {str(e)}"
            }
