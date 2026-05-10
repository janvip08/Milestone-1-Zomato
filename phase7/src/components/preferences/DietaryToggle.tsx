'use client'

import React from 'react'

interface DietaryToggleProps {
  label: string
  checked: boolean
  onChange: () => void
}

export function DietaryToggle({ label, checked, onChange }: DietaryToggleProps) {
  return (
    <div className="flex items-center justify-between p-3 bg-surface rounded-lg shadow-sm">
      <span className="font-body-lg text-on-surface">{label}</span>
      <label className="relative inline-flex items-center cursor-pointer">
        <input
          checked={checked}
          onChange={onChange}
          className="sr-only toggle-checkbox"
          type="checkbox"
        />
        <div className="w-11 h-6 bg-outline-variant rounded-full transition-colors toggle-label">
          <div className="toggle-dot absolute top-1 left-1 bg-white w-4 h-4 rounded-full transition-transform shadow-md"></div>
        </div>
      </label>
    </div>
  )
}
