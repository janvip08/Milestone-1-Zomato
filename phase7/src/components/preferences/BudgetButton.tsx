'use client'

import React from 'react'

interface BudgetButtonProps {
  budget: string
  isSelected: boolean
  onClick: () => void
}

export function BudgetButton({ budget, isSelected, onClick }: BudgetButtonProps) {
  return (
    <button
      onClick={onClick}
      className={`
        px-6 py-3 rounded-xl border font-body-lg transition-all active:scale-95
        ${isSelected 
          ? 'border-2 border-primary bg-primary-fixed text-primary font-bold shadow-sm' 
          : 'border-outline-variant bg-surface-container-lowest text-on-surface hover:border-primary'
        }
      `}
    >
      {budget}
    </button>
  )
}
