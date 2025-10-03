/**
 * 생산량 예측 페이지 컴포넌트
 * 
 * 백엔드 예측 API를 호출하여 각 모델의 30일 생산량 예측을 실행하고,
 * 결과를 라인 차트와 요약 통계로 시각화합니다.
 * 
 * 주요 기능:
 * - 예측 실행 버튼
 * - 모델별 라인 차트 (예측값, 상한, 하한)
 * - 요약 통계 (평균 예측, 예측 기간, 총 예측량)
 */

'use client'

import { useState } from 'react'
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer 
} from 'recharts'

/**
 * 예측 데이터 인터페이스
 */
interface ForecastData {
  date: string          // 예측 날짜 (YYYY-MM-DD)
  model: string         // 모델명
  forecast_units: number // 예측 생산량
  conf_lo: number       // 신뢰구간 하한
  conf_hi: number       // 신뢰구간 상한
}

export default function ForecastPage() {
  // 예측 결과를 저장하는 state
  // 모델명을 키로, 예측 데이터 배열을 값으로 하는 객체
  const [forecasts, setForecasts] = useState<{[model: string]: ForecastData[]}>({})
  
  // 로딩 상태를 관리하는 state
  const [loading, setLoading] = useState(false)
  
  // 에러 메시지를 저장하는 state
  const [error, setError] = useState<string | null>(null)

  
  /**
   * 예측 실행 함수
   * 
   * 백엔드 /api/forecast/run 엔드포인트를 호출하여 예측을 실행합니다.
   * 성공 시 forecasts state를 업데이트하고, 실패 시 에러 메시지를 표시합니다.
   */
  const runForecast = async () => {
    // 로딩 시작
    setLoading(true)
    setError(null)
    
    try {
      // 백엔드 예측 API 호출
      const response = await fetch('http://localhost:8000/api/forecast/run', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      })
      
      // 응답 JSON 파싱
      const data = await response.json()
      
      // 응답 상태 확인
      if (data.status === 'success') {
        // 성공 시 예측 결과를 state에 저장
        setForecasts(data.forecasts)
      } else {
        // 백엔드에서 에러 응답을 받은 경우
        setError(data.message)
      }
    } catch (err) {
      // 네트워크 에러 또는 백엔드 서버가 실행되지 않은 경우
      setError('API 호출 실패. 백엔드 서버를 확인하세요.')
      console.error('예측 API 에러:', err)
    } finally {
      // 로딩 종료
      setLoading(false)
    }
  }
  
  return (
    <div className="min-h-screen p-8 bg-gradient-to-b from-blue-50 to-gray-100">
      <div className="max-w-7xl mx-auto">
        {/* 페이지 헤더 */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">
            📊 생산량 예측
          </h1>
          <p className="text-gray-600">
            과거 생산 이력을 기반으로 미래 30일간의 생산량을 예측합니다
          </p>
        </div>
        
        {/* 예측 실행 버튼 */}
        <div className="mb-6">
          <button
            onClick={runForecast}
            disabled={loading}
            className={`
              px-6 py-3 rounded-md font-medium text-white
              ${loading 
                ? 'bg-blue-300 cursor-not-allowed' 
                : 'bg-blue-500 hover:bg-blue-600'
              }
              transition-colors duration-200
            `}
          >
            {loading ? '예측 실행중...' : '예측 실행'}
          </button>
        </div>
        
        {/* 에러 메시지 표시 */}
        {error && (
          <div className="mb-6 p-4 bg-red-100 border border-red-300 text-red-700 rounded-md">
            <p className="font-medium">오류 발생</p>
            <p className="text-sm mt-1">{error}</p>
          </div>
        )}

        
        {/* 예측 결과 표시 */}
        {Object.keys(forecasts).length > 0 && (
          <div className="space-y-8">
            {Object.entries(forecasts).map(([model, data]) => {
              /**
               * 차트 데이터 포맷 변환 함수
               * 
               * 백엔드에서 받은 데이터를 Recharts가 이해할 수 있는 형식으로 변환합니다.
               * 날짜를 한국어 형식으로 포맷팅합니다.
               */
              const formatChartData = (modelData: ForecastData[]) => {
                return modelData.map(item => ({
                  // 날짜를 "1월 8일" 형식으로 변환
                  date: new Date(item.date).toLocaleDateString('ko-KR', {
                    month: 'short',
                    day: 'numeric'
                  }),
                  예측값: item.forecast_units,
                  하한: item.conf_lo,
                  상한: item.conf_hi
                }))
              }
              
              // 요약 통계 계산
              const avgForecast = Math.round(
                data.reduce((sum, d) => sum + d.forecast_units, 0) / data.length
              )
              const totalForecast = data.reduce((sum, d) => sum + d.forecast_units, 0)
              
              return (
                <div key={model} className="bg-white rounded-lg shadow-md p-6">
                  {/* 모델명 헤더 */}
                  <h3 className="text-xl font-semibold text-gray-800 mb-4">
                    {model} 예측 결과
                  </h3>
                  
                  {/* 라인 차트 */}
                  <div className="h-80 mb-6">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={formatChartData(data)}>
                        {/* 그리드 */}
                        <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
                        
                        {/* X축 (날짜) */}
                        <XAxis 
                          dataKey="date" 
                          tick={{ fontSize: 12 }}
                          interval="preserveStartEnd"
                        />
                        
                        {/* Y축 (생산량) */}
                        <YAxis 
                          tick={{ fontSize: 12 }}
                          label={{ value: '생산량 (대)', angle: -90, position: 'insideLeft' }}
                        />
                        
                        {/* 툴팁 */}
                        <Tooltip 
                          contentStyle={{ 
                            backgroundColor: 'white', 
                            border: '1px solid #ccc',
                            borderRadius: '4px'
                          }}
                        />
                        
                        {/* 범례 */}
                        <Legend />
                        
                        {/* 예측값 라인 (파란색, 굵게) */}
                        <Line 
                          type="monotone" 
                          dataKey="예측값" 
                          stroke="#2563eb" 
                          strokeWidth={3}
                          dot={{ r: 3 }}
                        />
                        
                        {/* 하한 라인 (연한 파란색, 점선) */}
                        <Line 
                          type="monotone" 
                          dataKey="하한" 
                          stroke="#93c5fd" 
                          strokeWidth={2}
                          strokeDasharray="5 5"
                          dot={false}
                        />
                        
                        {/* 상한 라인 (연한 파란색, 점선) */}
                        <Line 
                          type="monotone" 
                          dataKey="상한" 
                          stroke="#93c5fd" 
                          strokeWidth={2}
                          strokeDasharray="5 5"
                          dot={false}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                  
                  {/* 요약 통계 카드 */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {/* 평균 예측 */}
                    <div className="bg-blue-50 p-4 rounded-lg text-center">
                      <div className="text-sm font-medium text-gray-600 mb-1">
                        평균 예측
                      </div>
                      <div className="text-2xl font-bold text-blue-600">
                        {avgForecast}
                      </div>
                      <div className="text-xs text-gray-500 mt-1">
                        대/일
                      </div>
                    </div>
                    
                    {/* 예측 기간 */}
                    <div className="bg-green-50 p-4 rounded-lg text-center">
                      <div className="text-sm font-medium text-gray-600 mb-1">
                        예측 기간
                      </div>
                      <div className="text-2xl font-bold text-green-600">
                        {data.length}
                      </div>
                      <div className="text-xs text-gray-500 mt-1">
                        일
                      </div>
                    </div>
                    
                    {/* 총 예측량 */}
                    <div className="bg-purple-50 p-4 rounded-lg text-center">
                      <div className="text-sm font-medium text-gray-600 mb-1">
                        총 예측량
                      </div>
                      <div className="text-2xl font-bold text-purple-600">
                        {totalForecast.toLocaleString()}
                      </div>
                      <div className="text-xs text-gray-500 mt-1">
                        대
                      </div>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}
