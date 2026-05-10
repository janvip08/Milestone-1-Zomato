'use client'

import React from 'react'

interface Restaurant {
  id: string
  name: string
  cuisine: string
  rating: number
  costForTwo: number
  location: string
  specialties: string[]
  recommendationReason: string
  priceRange: string
  imageUrl?: string
  aiScore?: number
}

interface RestaurantCardProps {
  restaurant: Restaurant
  index: number
}

export function RestaurantCard({ restaurant, index }: RestaurantCardProps) {
  return (
    <div className="bg-surface-container-low rounded-xl p-md shadow-sm hover:shadow-md transition-shadow">
      {/* AI Badge */}
      {restaurant.aiScore && (
        <div className="flex items-center gap-1 mb-sm">
          <span className="material-symbols-outlined text-primary text-sm" style={{ fontVariationSettings: "'FILL' 1" }}>
            auto_awesome
          </span>
          <span className="font-ai-recommendation text-ai-recommendation text-primary">
            {restaurant.aiScore}% AI Match
          </span>
        </div>
      )}

      <div className="flex gap-md">
        {/* Restaurant Image */}
        <div className="w-20 h-20 bg-surface-variant rounded-lg overflow-hidden flex-shrink-0">
          <img
            src={restaurant.imageUrl || `/api/placeholder/80/80`}
            alt={restaurant.name}
            className="w-full h-full object-cover"
          />
        </div>

        {/* Restaurant Info */}
        <div className="flex-1">
          <div className="flex items-start justify-between mb-xs">
            <div>
              <h3 className="font-title-md text-title-md text-on-surface">{restaurant.name}</h3>
              <p className="font-body-sm text-body-sm text-on-surface-variant">{restaurant.cuisine}</p>
            </div>
            <div className="text-right">
              <div className="flex items-center gap-1">
                <span className="material-symbols-outlined text-secondary text-sm" style={{ fontVariationSettings: "'FILL' 1" }}>
                  star
                </span>
                <span className="font-body-sm text-body-sm text-on-surface font-medium">
                  {restaurant.rating}
                </span>
              </div>
              <p className="font-body-sm text-body-sm text-on-surface-variant">
                {restaurant.priceRange}
              </p>
            </div>
          </div>

          <div className="space-y-xs">
            <div className="flex items-center gap-1">
              <span className="material-symbols-outlined text-tertiary text-sm">location_on</span>
              <span className="font-body-sm text-body-sm text-on-surface-variant">
                {restaurant.location}
              </span>
            </div>
            <div className="flex items-center gap-1">
              <span className="material-symbols-outlined text-tertiary text-sm">payments</span>
              <span className="font-body-sm text-body-sm text-on-surface-variant">
                Rs.{restaurant.costForTwo} for two
              </span>
            </div>
          </div>

          {/* Specialties */}
          <div className="mt-sm">
            <p className="font-body-sm text-body-sm text-on-surface-variant mb-xs">Specialties:</p>
            <div className="flex flex-wrap gap-xs">
              {restaurant.specialties.map((specialty, idx) => (
                <span
                  key={idx}
                  className="px-2 py-1 bg-surface-variant rounded text-xs font-body-sm text-on-surface"
                >
                  {specialty}
                </span>
              ))}
            </div>
          </div>

          {/* AI Recommendation */}
          <div className="mt-sm bg-primary-fixed rounded-lg p-sm">
            <div className="flex items-start gap-2">
              <span className="material-symbols-outlined text-primary text-sm mt-0.5" style={{ fontVariationSettings: "'FILL' 1" }}>
                lightbulb
              </span>
              <p className="font-body-sm text-body-sm text-primary text-xs leading-tight">
                {restaurant.recommendationReason}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-sm mt-md pt-md border-t border-outline-variant">
        <button className="flex-1 py-2 bg-surface rounded-lg font-body-sm text-body-sm text-on-surface hover:bg-surface-variant transition-colors">
          View Details
        </button>
        <button className="flex-1 py-2 bg-primary text-on-primary rounded-lg font-body-sm text-body-sm font-medium hover:bg-primary/90 transition-colors">
          Book Table
        </button>
      </div>
    </div>
  )
}
