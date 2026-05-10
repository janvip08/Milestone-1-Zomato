'use client'

import React from 'react'

interface CuisineTagProps {
  cuisine: string
  isSelected: boolean
  onClick: () => void
}

export function CuisineTag({ cuisine, isSelected, onClick }: CuisineTagProps) {
  return (
    <span
      onClick={onClick}
      className={`
        px-4 py-2 rounded-full border font-body-sm cursor-pointer transition-colors flex items-center gap-1
        ${isSelected 
          ? 'bg-primary text-on-primary font-bold shadow-md' 
          : 'border-outline-variant bg-surface-container-lowest text-on-surface hover:bg-primary-fixed hover:border-primary'
        }
      `}
    >
      {cuisine}
      {isSelected && (
        <span className="material-symbols-outlined text-sm">close</span>
      )}
    </span>
  )
}
