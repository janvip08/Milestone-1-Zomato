'use client'

import React from 'react'
import { useRouter } from 'next/navigation'
import { Preferences } from './PreferencesPage'

interface AIRecommendButtonProps {
  preferences: Preferences
}

export function AIRecommendButton({ preferences }: AIRecommendButtonProps) {
  const router = useRouter()

  const handleRecommend = () => {
    // Store preferences in localStorage or state management
    localStorage.setItem('userPreferences', JSON.stringify(preferences))
    
    // Navigate to recommendations page
    router.push('/recommendations')
  }

  return (
    <div className="fixed bottom-20 left-0 w-full px-margin-mobile py-4 bg-gradient-to-t from-surface via-surface/90 to-transparent flex justify-center pointer-events-none">
      <button
        onClick={handleRecommend}
        className="pointer-events-auto w-full max-w-md h-16 bg-primary text-on-primary rounded-xl font-headline-lg-mobile text-headline-lg-mobile shadow-lg shadow-primary/20 flex items-center justify-center gap-3 active:scale-95 transition-transform"
      >
        <span className="material-symbols-outlined" style={{ fontVariationSettings: "'FILL' 1" }}>
          auto_awesome
        </span>
        AI Recommend!
      </button>
    </div>
  )
}
