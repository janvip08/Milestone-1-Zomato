'use client'

import React from 'react'
import { useRouter } from 'next/navigation'

export function BackButton() {
  const router = useRouter()

  return (
    <button
      onClick={() => router.back()}
      className="material-symbols-outlined text-on-surface-variant cursor-pointer hover:text-on-surface transition-colors"
    >
      arrow_back
    </button>
  )
}
