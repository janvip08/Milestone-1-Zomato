'use client'

import React from 'react'

interface RatingButtonProps {
  rating: string
  isSelected: boolean
  onClick: () => void
}

export function RatingButton({ rating, isSelected, onClick }: RatingButtonProps) {
  return (
    <button
      onClick={onClick}
      className={`
        flex-1 py-3 rounded-xl border font-body-lg transition-all flex items-center justify-center gap-1
        ${isSelected 
          ? 'border-2 border-secondary bg-secondary-fixed text-on-secondary-fixed font-bold' 
          : 'border-outline-variant bg-surface-container-lowest text-on-surface hover:bg-surface-variant'
        }
      `}
    >
      {rating}
      {rating !== 'Any' && (
        <span className="material-symbols-outlined text-xs" style={{ fontVariationSettings: "'FILL' 1" }}>
          star
        </span>
      )}
    </button>
  )
}
