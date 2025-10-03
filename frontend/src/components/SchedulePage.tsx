/**
 * 인력 스케줄링 페이지 컴포넌트
 * 
 * 생산 계획을 바탕으로 작업자를 배정하고 결과를 테이블로 표시합니다.
 * 
 * 주요 기능:
 * - 스케줄링 실행 버튼
 * - 스케줄 테이블 (날짜, 라인, 교대, 작업자)
 */

'use client'

import { useState } from 'react'

/**
 * 스케줄 항목 인터페이스
 */
interface ScheduleItem {
  date: string        // 날짜
  line_id: string     // 라인 ID
  shift: string       // 교대 (Day/Night)
  worker_id: string   // 작업자 ID
  worker_name: string // 작업자 이름
}

/**
 * 생산 계획 인터페이스 (스케줄링 입력용)
 */
interface MixPlan {
  period: number
  line_id: string
  model: string
  planned_units: number
}

interface SchedulePageProps {
  mixPlan?: MixPlan[]  // 최적화 페이지에서 전달받은 생산 계획 (선택적)
}

export default function SchedulePage({ mixPlan }: SchedulePageProps) {
  // 스케줄을 저장하는 state
  const [schedule, setSchedule] = useState<ScheduleItem[]>([])
  
  // 로딩 상태를 관리하는 state
  const [loading, setLoading] = useState(false)
  
  // 에러 메시지를 저장하는 state
  const [error, setError] = useState<string | null>(null)

  
  /**
   * 스케줄링 실행 함수
   * 
   * 백엔드 /api/schedule/run 엔드포인트를 호출하여 스케줄링을 실행합니다.
   * mixPlan이 제공되지 않으면 더미 데이터를 사용합니다.
   */
  const runScheduling = async () => {
    // 로딩 시작
    setLoading(true)
    setError(null)
    
    try {
      // mixPlan이 없으면 더미 데이터 사용
      const planToUse = mixPlan || [
        { period: 1, line_id: 'L1', model: 'ModelA', planned_units: 700 },
        { period: 1, line_id: 'L2', model: 'ModelB', planned_units: 1400 },
      ]
      
      // 백엔드 스케줄링 API 호출
      const response = await fetch('http://localhost:8000/api/schedule/run', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(planToUse),
      })
      
      // 응답 JSON 파싱
      const data = await response.json()
      
      // 응답 상태 확인
      if (data.status === 'success') {
        // 성공 시 스케줄을 state에 저장
        setSchedule(data.schedule)
      } else {
        // 백엔드에서 에러 응답을 받은 경우
        setError(data.message)
      }
    } catch (err) {
      // 네트워크 에러 또는 백엔드 서버가 실행되지 않은 경우
      setError('API 호출 실패. 백엔드 서버를 확인하세요.')
      console.error('스케줄링 API 에러:', err)
    } finally {
      // 로딩 종료
      setLoading(false)
    }
  }
  
  return (
    <div className="min-h-screen p-8 bg-gradient-to-b from-purple-50 to-gray-100">
      <div className="max-w-7xl mx-auto">
        {/* 페이지 헤더 */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">
            👥 인력 스케줄링
          </h1>
          <p className="text-gray-600">
            생산 계획에 따라 작업자를 배정합니다
          </p>
        </div>
        
        {/* 스케줄링 실행 버튼 */}
        <div className="mb-6">
          <button
            onClick={runScheduling}
            disabled={loading}
            className={`
              px-6 py-3 rounded-md font-medium text-white
              ${loading 
                ? 'bg-purple-300 cursor-not-allowed' 
                : 'bg-purple-500 hover:bg-purple-600'
              }
              transition-colors duration-200
            `}
          >
            {loading ? '스케줄링 실행중...' : '스케줄링 실행'}
          </button>
        </div>
        
        {/* 에러 메시지 표시 */}
        {error && (
          <div className="mb-6 p-4 bg-red-100 border border-red-300 text-red-700 rounded-md">
            <p className="font-medium">오류 발생</p>
            <p className="text-sm mt-1">{error}</p>
          </div>
        )}
        
        {/* 스케줄 테이블 */}
        {schedule.length > 0 && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-xl font-semibold text-gray-800 mb-4">
              작업자 배정 결과
            </h3>
            
            {/* 요약 정보 */}
            <div className="mb-4 p-4 bg-purple-50 rounded-lg">
              <p className="text-sm text-gray-700">
                총 <span className="font-bold text-purple-600">{schedule.length}</span>개의 근무 배정이 생성되었습니다.
              </p>
            </div>
            
            {/* 테이블 */}
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      날짜
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      라인
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      교대
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      작업자 ID
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      작업자 이름
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {schedule.map((item, index) => (
                    <tr key={index} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {item.date}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {item.line_id}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        <span className={`
                          px-2 py-1 rounded-full text-xs font-medium
                          ${item.shift === 'Day' 
                            ? 'bg-yellow-100 text-yellow-800' 
                            : 'bg-blue-100 text-blue-800'
                          }
                        `}>
                          {item.shift === 'Day' ? '주간' : '야간'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {item.worker_id}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {item.worker_name}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
