/**
 * LineMind 홈 페이지 컴포넌트
 * 
 * 메인 대시보드 역할을 하며, 백엔드 API 연결 상태를 확인하고
 * 각 기능(예측, 믹스, 스케줄링)으로 이동할 수 있는 네비게이션을 제공합니다.
 */

'use client'

import { useEffect, useState } from 'react'
import ForecastPage from '@/components/ForecastPage'
import OptimizePage from '@/components/OptimizePage'

export default function Home() {
  // 현재 페이지를 관리하는 state
  // 'home': 홈 대시보드, 'forecast': 예측 페이지, 'optimize': 최적화 페이지, 'schedule': 스케줄링 페이지
  const [currentPage, setCurrentPage] = useState<'home' | 'forecast' | 'optimize' | 'schedule'>('home')
  
  // API 연결 상태를 저장하는 state
  // 초기값은 "연결 확인 중..."
  const [apiStatus, setApiStatus] = useState<string>('연결 확인 중...')

  // 컴포넌트가 마운트될 때 백엔드 health 엔드포인트를 호출
  useEffect(() => {
    // 비동기 함수로 API 호출
    const checkApiHealth = async () => {
      try {
        // 백엔드 health 엔드포인트 호출
        const response = await fetch('http://localhost:8000/health')
        
        // 응답이 성공적이면 (status code 200-299)
        if (response.ok) {
          const data = await response.json()
          // 백엔드에서 받은 status 메시지를 state에 저장
          setApiStatus(data.status)
        } else {
          // HTTP 에러 응답인 경우
          setApiStatus(`연결 실패 (HTTP ${response.status})`)
        }
      } catch (error) {
        // 네트워크 에러 또는 백엔드 서버가 실행되지 않은 경우
        setApiStatus('백엔드 서버에 연결할 수 없습니다')
        console.error('API 연결 에러:', error)
      }
    }

    // API 상태 확인 함수 실행
    checkApiHealth()
  }, []) // 빈 의존성 배열: 컴포넌트 마운트 시 한 번만 실행

  /**
   * 페이지 렌더링 함수
   * 
   * currentPage state에 따라 적절한 페이지 컴포넌트를 렌더링합니다.
   */
  const renderPage = () => {
    switch (currentPage) {
      case 'forecast':
        return <ForecastPage />
      case 'optimize':
        return <OptimizePage />
      case 'home':
      default:
        return renderHomePage()
    }
  }

  /**
   * 홈 페이지 렌더링 함수
   */
  const renderHomePage = () => (
    <main className="min-h-screen p-8 bg-gradient-to-b from-gray-50 to-gray-100">
      {/* 페이지 헤더 */}
      <div className="max-w-6xl mx-auto">
        <h1 className="text-4xl font-bold text-gray-800 mb-2">
          LineMind Ready
        </h1>
        <p className="text-lg text-gray-600 mb-8">
          AI 기반 생산 관리 시스템
        </p>

        {/* API 상태 표시 카드 */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-700 mb-3">
            백엔드 API 상태
          </h2>
          <div className="flex items-center">
            {/* 상태 인디케이터 (점) */}
            <div 
              className={`w-3 h-3 rounded-full mr-3 ${
                apiStatus.includes('running') 
                  ? 'bg-green-500' 
                  : apiStatus.includes('확인 중') 
                  ? 'bg-yellow-500' 
                  : 'bg-red-500'
              }`}
            />
            {/* 상태 텍스트 */}
            <p className="text-gray-700 font-medium">
              {apiStatus}
            </p>
          </div>
        </div>

        {/* 기능 안내 섹션 */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-700 mb-4">
            주요 기능
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* 예측 기능 카드 (활성화) */}
            <button
              onClick={() => setCurrentPage('forecast')}
              className="border border-blue-300 rounded-lg p-4 bg-blue-50 hover:bg-blue-100 transition-colors text-left"
            >
              <div className="text-3xl mb-2">📊</div>
              <h3 className="font-bold text-gray-800 mb-1">생산량 예측</h3>
              <p className="text-sm text-gray-600">미래 수요 예측</p>
              <p className="text-xs text-blue-600 mt-2 font-medium">클릭하여 시작 →</p>
            </button>

            {/* 믹스 최적화 카드 (활성화) */}
            <button
              onClick={() => setCurrentPage('optimize')}
              className="border border-green-300 rounded-lg p-4 bg-green-50 hover:bg-green-100 transition-colors text-left"
            >
              <div className="text-3xl mb-2">⚙️</div>
              <h3 className="font-bold text-gray-800 mb-1">생산 믹스</h3>
              <p className="text-sm text-gray-600">라인별 최적 배분</p>
              <p className="text-xs text-green-600 mt-2 font-medium">클릭하여 시작 →</p>
            </button>

            {/* 스케줄링 카드 (준비 중) */}
            <div className="border border-gray-200 rounded-lg p-4 bg-gray-50">
              <div className="text-3xl mb-2">👥</div>
              <h3 className="font-bold text-gray-800 mb-1">인력 스케줄링</h3>
              <p className="text-sm text-gray-600">작업자 배정 최적화</p>
              <p className="text-xs text-gray-400 mt-2">준비 중...</p>
            </div>
          </div>
        </div>
      </div>
    </main>
  )

  return (
    <>
      {/* 홈이 아닌 페이지에서는 "홈으로 돌아가기" 버튼 표시 */}
      {currentPage !== 'home' && (
        <div className="fixed top-4 left-4 z-50">
          <button
            onClick={() => setCurrentPage('home')}
            className="bg-white px-4 py-2 rounded-md shadow-md hover:shadow-lg transition-shadow text-blue-600 hover:text-blue-700 font-medium"
          >
            ← 홈으로 돌아가기
          </button>
        </div>
      )}
      
      {/* 현재 페이지 렌더링 */}
      {renderPage()}
    </>
  )
}
