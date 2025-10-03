/**
 * 생산 믹스 최적화 페이지 컴포넌트
 * 
 * 백엔드 최적화 API를 호출하여 각 라인에 어떤 모델을 배정할지 결정하고,
 * 결과를 파이 차트, 바 차트, 테이블로 시각화합니다.
 * 
 * 주요 기능:
 * - 최적화 실행 버튼
 * - KPI 카드 4개 (총 수요, 계획 생산, 충족률, 예상 비용)
 * - 모델별 생산 비중 파이 차트
 * - 라인별 계획 바 차트
 * - 상세 계획 테이블
 */

'use client'

import { useState } from 'react'
import { 
  PieChart, 
  Pie, 
  Cell, 
  ResponsiveContainer, 
  Tooltip,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Legend
} from 'recharts'

/**
 * 생산 계획 인터페이스
 */
interface MixPlan {
  period: number           // 주차
  line_id: string         // 라인 ID
  model: string           // 모델명
  planned_units: number   // 계획 생산량
  line_utilization: number // 라인 가동률 (0~1)
}

/**
 * KPI 인터페이스
 */
interface KPI {
  total_demand: number      // 총 수요
  total_planned: number     // 계획 생산량
  fulfillment_rate: number  // 수요 충족률 (%)
  total_changeovers: number // 체인지오버 횟수
  estimated_cost: number    // 예상 비용
}

export default function OptimizePage() {
  // 생산 계획을 저장하는 state
  const [mixPlan, setMixPlan] = useState<MixPlan[]>([])
  
  // KPI를 저장하는 state
  const [kpi, setKpi] = useState<KPI | null>(null)
  
  // 로딩 상태를 관리하는 state
  const [loading, setLoading] = useState(false)
  
  // 에러 메시지를 저장하는 state
  const [error, setError] = useState<string | null>(null)

  
  /**
   * 최적화 실행 함수
   * 
   * 백엔드 /api/mix/optimize 엔드포인트를 호출하여 최적화를 실행합니다.
   * 성공 시 mixPlan과 kpi state를 업데이트하고, 실패 시 에러 메시지를 표시합니다.
   */
  const runOptimization = async () => {
    // 로딩 시작
    setLoading(true)
    setError(null)
    
    try {
      // 백엔드 최적화 API 호출
      const response = await fetch('http://localhost:8000/api/mix/optimize', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      })
      
      // 응답 JSON 파싱
      const data = await response.json()
      
      // 응답 상태 확인
      if (data.status === 'success') {
        // 성공 시 생산 계획과 KPI를 state에 저장
        setMixPlan(data.mix_plan)
        setKpi(data.kpi)
      } else {
        // 백엔드에서 에러 응답을 받은 경우
        setError(data.message)
      }
    } catch (err) {
      // 네트워크 에러 또는 백엔드 서버가 실행되지 않은 경우
      setError('API 호출 실패. 백엔드 서버를 확인하세요.')
      console.error('최적화 API 에러:', err)
    } finally {
      // 로딩 종료
      setLoading(false)
    }
  }
  
  return (
    <div className="min-h-screen p-8 bg-gradient-to-b from-green-50 to-gray-100">
      <div className="max-w-7xl mx-auto">
        {/* 페이지 헤더 */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">
            ⚙️ 생산 믹스 최적화
          </h1>
          <p className="text-gray-600">
            예측된 수요를 바탕으로 각 라인에 최적의 모델을 배정합니다
          </p>
        </div>
        
        {/* 최적화 실행 버튼 */}
        <div className="mb-6">
          <button
            onClick={runOptimization}
            disabled={loading}
            className={`
              px-6 py-3 rounded-md font-medium text-white
              ${loading 
                ? 'bg-green-300 cursor-not-allowed' 
                : 'bg-green-500 hover:bg-green-600'
              }
              transition-colors duration-200
            `}
          >
            {loading ? '최적화 실행중...' : '최적화 실행'}
          </button>
        </div>
        
        {/* 에러 메시지 표시 */}
        {error && (
          <div className="mb-6 p-4 bg-red-100 border border-red-300 text-red-700 rounded-md">
            <p className="font-medium">오류 발생</p>
            <p className="text-sm mt-1">{error}</p>
          </div>
        )}
        
        {/* KPI 카드 */}
        {kpi && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            {/* 총 수요 */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="text-sm font-medium text-gray-600 mb-2">
                총 수요
              </div>
              <div className="text-3xl font-bold text-blue-600">
                {kpi.total_demand.toLocaleString()}
              </div>
              <div className="text-xs text-gray-500 mt-1">
                대
              </div>
            </div>
            
            {/* 계획 생산 */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="text-sm font-medium text-gray-600 mb-2">
                계획 생산
              </div>
              <div className="text-3xl font-bold text-green-600">
                {kpi.total_planned.toLocaleString()}
              </div>
              <div className="text-xs text-gray-500 mt-1">
                대
              </div>
            </div>
            
            {/* 충족률 */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="text-sm font-medium text-gray-600 mb-2">
                충족률
              </div>
              <div className="text-3xl font-bold text-purple-600">
                {kpi.fulfillment_rate}%
              </div>
              <div className="text-xs text-gray-500 mt-1">
                수요 대비
              </div>
            </div>
            
            {/* 예상 비용 */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="text-sm font-medium text-gray-600 mb-2">
                예상 비용
              </div>
              <div className="text-3xl font-bold text-orange-600">
                {(kpi.estimated_cost / 1000000).toFixed(1)}M
              </div>
              <div className="text-xs text-gray-500 mt-1">
                원
              </div>
            </div>
          </div>
        )}

        
        {/* 차트 및 테이블 */}
        {mixPlan.length > 0 && (
          <div className="space-y-8">
            {/* 차트 섹션 */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* 모델별 생산 비중 파이 차트 */}
              <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-xl font-semibold text-gray-800 mb-4">
                  모델별 생산 비중
                </h3>
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={
                          // 모델별로 생산량 합산
                          mixPlan.reduce((acc: any[], item) => {
                            const existing = acc.find(d => d.model === item.model)
                            if (existing) {
                              existing.value += item.planned_units
                            } else {
                              acc.push({ 
                                model: item.model, 
                                value: item.planned_units 
                              })
                            }
                            return acc
                          }, [])
                        }
                        dataKey="value"
                        nameKey="model"
                        cx="50%"
                        cy="50%"
                        outerRadius={100}
                        label={(entry) => `${entry.model}: ${entry.value}대`}
                      >
                        {/* 색상 배열 */}
                        {['#2563eb', '#16a34a', '#dc2626', '#ca8a04', '#9333ea'].map((color, index) => (
                          <Cell key={`cell-${index}`} fill={color} />
                        ))}
                      </Pie>
                      <Tooltip 
                        formatter={(value: number) => `${value.toLocaleString()}대`}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </div>
              
              {/* 라인별 계획 바 차트 */}
              <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-xl font-semibold text-gray-800 mb-4">
                  라인별 계획
                </h3>
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={mixPlan.map(item => ({
                        라인: item.line_id,
                        모델: item.model,
                        계획생산량: item.planned_units,
                        가동률: Math.round(item.line_utilization * 100)
                      }))}
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="라인" />
                      <YAxis 
                        yAxisId="left"
                        label={{ value: '생산량 (대)', angle: -90, position: 'insideLeft' }}
                      />
                      <YAxis 
                        yAxisId="right" 
                        orientation="right"
                        label={{ value: '가동률 (%)', angle: 90, position: 'insideRight' }}
                      />
                      <Tooltip />
                      <Legend />
                      <Bar 
                        yAxisId="left"
                        dataKey="계획생산량" 
                        fill="#2563eb" 
                      />
                      <Bar 
                        yAxisId="right"
                        dataKey="가동률" 
                        fill="#16a34a" 
                      />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
            
            {/* 상세 계획 테이블 */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-xl font-semibold text-gray-800 mb-4">
                상세 계획표
              </h3>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        주차
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        라인
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        모델
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        계획 생산량
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        가동률
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {mixPlan.map((item, index) => (
                      <tr key={index} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {item.period}주차
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {item.line_id}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {item.model}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {item.planned_units.toLocaleString()}대
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          <div className="flex items-center">
                            <div className="flex-1 bg-gray-200 rounded-full h-2 mr-2">
                              <div 
                                className="bg-green-500 h-2 rounded-full" 
                                style={{ width: `${Math.round(item.line_utilization * 100)}%` }}
                              />
                            </div>
                            <span>{Math.round(item.line_utilization * 100)}%</span>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
