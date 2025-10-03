"""
LineMind 데이터 로더 모듈

CSV 파일 기반의 시드 데이터를 로드하고 검증하는 중앙 데이터 접근 계층입니다.
모든 백엔드 모듈(예측, 최적화, 스케줄링)은 이 DataLoader를 통해 데이터에 접근합니다.

주요 기능:
- CSV 파일 존재 여부 확인
- 필수 컬럼 검증
- 결측치(NA) 검증
- 명확한 에러 메시지 제공
"""

import pandas as pd
import os
from typing import Dict

class DataLoader:
    """
    CSV 파일 로딩 및 검증을 담당하는 데이터 로더 클래스
    
    Attributes:
        data_dir (str): CSV 파일이 저장된 디렉토리 경로
    """
    
    def __init__(self, data_dir: str = "data/seed"):
        """
        DataLoader 초기화
        
        Args:
            data_dir (str): CSV 파일이 저장된 디렉토리 경로 (기본값: "data/seed")
        """
        self.data_dir = data_dir

    
    def load_csv(self, filename: str, required_columns: list) -> pd.DataFrame:
        """
        CSV 파일을 로드하고 필수 컬럼 및 결측치를 검증합니다.
        
        Args:
            filename (str): 로드할 CSV 파일명 (예: "production_history.csv")
            required_columns (list): 필수로 존재해야 하는 컬럼 리스트
        
        Returns:
            pd.DataFrame: 로드된 데이터프레임
        
        Raises:
            FileNotFoundError: CSV 파일이 존재하지 않을 때
            ValueError: 필수 컬럼이 누락되었거나 결측치가 있을 때
            pd.errors.EmptyDataError: CSV 파일이 비어있을 때
        
        Example:
            >>> loader = DataLoader()
            >>> df = loader.load_csv('lines.csv', ['line_id', 'base_daily_capacity'])
        """
        # CSV 파일의 전체 경로 생성
        filepath = os.path.join(self.data_dir, filename)
        
        # 1. 파일 존재 여부 확인
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"CSV 파일이 없습니다: {filepath}")
        
        try:
            # 2. CSV 파일 로드
            df = pd.read_csv(filepath)
            
            # 3. 필수 컬럼 검증
            # 필수 컬럼 중 데이터프레임에 없는 컬럼 찾기
            missing_cols = [col for col in required_columns if col not in df.columns]
            if missing_cols:
                raise ValueError(f"필수 컬럼이 없습니다: {missing_cols}")
            
            # 4. 결측치(NA) 검증
            # 필수 컬럼에 결측치가 있는지 확인
            if df[required_columns].isnull().any().any():
                raise ValueError(f"데이터에 결측치가 있습니다")
            
            return df
            
        except pd.errors.EmptyDataError:
            # CSV 파일이 비어있는 경우
            raise ValueError("빈 CSV 파일입니다")
        except Exception as e:
            # 기타 예외 처리 (인코딩 에러, 파싱 에러 등)
            raise ValueError(f"CSV 로드 실패: {str(e)}")

    
    def load_all_data(self) -> Dict[str, pd.DataFrame]:
        """
        모든 핵심 CSV 데이터를 로드합니다.
        
        Returns:
            Dict[str, pd.DataFrame]: 데이터셋 이름을 키로, 데이터프레임을 값으로 하는 딕셔너리
                - 'production': 생산 이력 데이터
                - 'lines': 라인 정보 데이터
                - 'workers': 작업자 정보 데이터
                - 'costs': 체인지오버 비용 데이터
        
        Raises:
            FileNotFoundError: CSV 파일이 존재하지 않을 때
            ValueError: 필수 컬럼이 누락되었거나 결측치가 있을 때
        
        Example:
            >>> loader = DataLoader()
            >>> data = loader.load_all_data()
            >>> print(f"생산 이력: {len(data['production'])} 행")
        """
        data = {}
        
        # 1. 생산 이력 데이터 로드
        # 필수 컬럼: 날짜, 라인ID, 모델, 교대, 생산량
        data['production'] = self.load_csv(
            'production_history.csv',
            ['date', 'line_id', 'model', 'shift', 'produced_units']
        )
        
        # 2. 라인 정보 데이터 로드
        # 필수 컬럼: 라인ID, 지원 가능 모델, 일일 기본 생산 용량
        data['lines'] = self.load_csv(
            'lines.csv',
            ['line_id', 'eligible_models', 'base_daily_capacity']
        )
        
        # 3. 작업자 정보 데이터 로드
        # 필수 컬럼: 작업자ID, 연차, 시급, 주간 최대 근무 시간
        data['workers'] = self.load_csv(
            'workers.csv',
            ['worker_id', 'years', 'wage_per_hour', 'max_hours_week']
        )
        
        # 4. 체인지오버 비용 데이터 로드
        # 필수 컬럼: 출발 모델, 도착 모델, 체인지오버 시간, 체인지오버 비용
        data['costs'] = self.load_csv(
            'cost_params.csv',
            ['from_model', 'to_model', 'changeover_hours', 'changeover_cost']
        )
        
        return data


def test_data_loading():
    """
    DataLoader의 기능을 테스트하는 함수
    
    모든 CSV 파일을 로드하고 각 데이터셋의 행 개수를 출력합니다.
    에러가 발생하면 에러 메시지를 출력합니다.
    """
    # DataLoader 인스턴스 생성
    loader = DataLoader()
    
    try:
        # 모든 데이터 로드 시도
        data = loader.load_all_data()
        
        # 성공 메시지 출력
        print("✅ 모든 CSV 로드 성공")
        
        # 각 데이터셋의 행 개수 출력
        for key, df in data.items():
            print(f"  {key}: {len(df)} 행")
        
        return data
        
    except Exception as e:
        # 에러 발생 시 에러 메시지 출력
        print(f"❌ 데이터 로드 실패: {e}")
        return None


# 이 파일을 직접 실행할 때만 테스트 함수 실행
if __name__ == "__main__":
    test_data_loading()
