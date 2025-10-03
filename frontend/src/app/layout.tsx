/**
 * LineMind 루트 레이아웃 컴포넌트
 * 
 * Next.js App Router의 루트 레이아웃입니다.
 * 모든 페이지에 공통으로 적용되는 HTML 구조와 메타데이터를 정의합니다.
 */

import type { Metadata } from 'next'
import './globals.css'

// 페이지 메타데이터 설정
export const metadata: Metadata = {
  title: 'LineMind - AI 기반 생산 관리 시스템',
  description: '생산 예측, 믹스 최적화, 인력 스케줄링을 제공하는 제조 현장 관리 시스템',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ko">
      <body>{children}</body>
    </html>
  )
}
