"""
LineMind 인력 스케줄링 모듈

생산 계획(mix_plan)을 바탕으로 필요한 작업자를 배정합니다.
Phase 1에서는 간단한 Greedy 방식(연차 순)을 사용하고,
Phase 2에서는 OR-Tools CP-SAT를 사용하여 제약 조건을 고려한 최적화를 수행합니다.

주요 기능:
- 생산 계획으로부터 필요 인원 산정
- 작업자를 연차 높은 순으로 배정 (Greedy)
- 스케줄 결과 및 KPI 반환
"""

import pandas as pd
from data_loader import DataLoader
from typing import List, Dict


class StubScheduler:
    """
    간단한 Greedy 방식의 인력 스케줄링 클래스
    
    실제 최적화 알고리즘 없이 연차가 높은 작업자부터 순서대로 배정합니다.
    전체 플로우를 검증하기 위한 더미 구현입니다.
    
    Attributes:
        data_loader (DataLoader): CSV 데이터를 로드하는 DataLoader 인스턴스
    """
    
    def __init__(self):
        """
        StubScheduler 초기화
        
        DataLoader 인스턴스를 생성합니다.
        """
        self.data_loader = DataLoader()

    
    def run_stub_schedule(self, mix_plan: List[Dict]) -> dict:
        """
        간단한 Greedy 스케줄링 알고리즘
        
        생산 계획으로부터 필요 인원을 산정하고,
        연차가 높은 작업자부터 순서대로 배정합니다.
        
        알고리즘:
        1. 생산 계획으로부터 라인/교대별 필요 인원 산정 (100대당 1명)
        2. 작업자를 연차 높은 순으로 정렬
        3. 필요한 슬롯에 순서대로 배정 (Round-robin)
        
        Args:
            mix_plan (List[Dict]): 생산 계획 리스트
                - period (int): 주차
                - line_id (str): 라인 ID
                - model (str): 모델명
                - planned_units (int): 계획 생산량
        
        Returns:
            dict: 스케줄링 결과
                성공 시:
                    - status (str): "success"
                    - schedule (list): 스케줄 리스트
                        - date (str): 날짜 (Week X, Day Y)
                        - line_id (str): 라인 ID
                        - shift (str): 교대 (Day/Night)
                        - worker_id (str): 작업자 ID
                        - worker_name (str): 작업자 이름
                실패 시:
                    - status (str): "error"
                    - message (str): 에러 메시지
        """
        try:
            # 1. 작업자 데이터 로드 (연차 높은 순으로 정렬)
            data = self.data_loader.load_all_data()
            workers_df = data['workers'].sort_values('years', ascending=False)
            
            # 2. 필요 인원 산정
            schedule = []
            required_slots = []
            
            for plan in mix_plan:
                # 주간 계획을 일간으로 분배
                daily_units = plan['planned_units'] / 7
                
                # 필요 인원 계산 (100대당 1명)
                required_staff = round(daily_units / 100)
                
                # 주간 계획을 7일로 분배
                for day in range(7):
                    # 주간/야간 2교대 가정
                    for shift in ['Day', 'Night']:
                        if required_staff > 0:
                            required_slots.append({
                                'week': plan['period'],
                                'day': day,
                                'line_id': plan['line_id'],
                                'shift': shift,
                                'required': required_staff // 2  # 교대당 인원
                            })
            
            # 3. 연차 높은 순으로 작업자 배정 (Round-robin)
            worker_list = workers_df.to_dict('records')
            worker_idx = 0
            
            for slot in required_slots:
                for _ in range(slot['required']):
                    # 작업자 순환 배정
                    worker = worker_list[worker_idx % len(worker_list)]
                    
                    schedule.append({
                        'date': f"Week {slot['week']}, Day {slot['day']+1}",
                        'line_id': slot['line_id'],
                        'shift': slot['shift'],
                        'worker_id': worker['worker_id'],
                        'worker_name': worker['name']
                    })
                    
                    worker_idx += 1
            
            # 4. 결과 반환
            return {
                "status": "success",
                "schedule": schedule
            }
            
        except Exception as e:
            # 에러 발생 시 에러 응답 반환
            return {
                "status": "error",
                "message": str(e)
            }


def test_scheduler():
    """
    StubScheduler의 기능을 테스트하는 함수
    
    더미 생산 계획으로 스케줄링을 실행하고 결과를 출력합니다.
    """
    # StubScheduler 인스턴스 생성
    scheduler = StubScheduler()
    
    # 더미 생산 계획
    dummy_mix_plan = [
        {'period': 1, 'line_id': 'L1', 'model': 'ModelA', 'planned_units': 700},
        {'period': 1, 'line_id': 'L2', 'model': 'ModelB', 'planned_units': 1400},
    ]
    
    # 스케줄링 실행
    result = scheduler.run_stub_schedule(dummy_mix_plan)
    
    # 결과 출력
    print(f"스케줄링 결과: {result['status']}")
    
    if result['status'] == 'success':
        # 성공 시 스케줄 항목 수 출력
        print(f"  스케줄 항목 수: {len(result['schedule'])}")
    else:
        # 실패 시 에러 메시지 출력
        print(f"  에러: {result['message']}")


# 이 파일을 직접 실행할 때만 테스트 함수 실행
if __name__ == "__main__":
    test_scheduler()
