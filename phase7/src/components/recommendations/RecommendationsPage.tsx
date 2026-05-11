'use client'

import React, { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { RestaurantCard } from './RestaurantCard'
import { BackButton } from './BackButton'
import { apiClient, RecommendationRequest } from '@/lib/api'


export default function RecommendationsPage() {
  const router = useRouter()
  const [restaurants, setRestaurants] = useState<any[]>([])
  const [preferences, setPreferences] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Load preferences from localStorage
    const savedPreferences = localStorage.getItem('userPreferences')
    if (savedPreferences) {
      setPreferences(JSON.parse(savedPreferences))
    }

    // Simulate API call to get recommendations
    const fetchRecommendations = async () => {
      setIsLoading(true)
      
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      // Mock restaurant data based on the Phase 4 test results
      const mockRestaurants: Restaurant[] = [
        {
          id: '1',
          name: 'Toit - Brewpub & Kitchen',
          cuisine: 'European & Indian Fusion',
          rating: 4.3,
          costForTwo: 1800,
          location: 'Indiranagar, Bangalore',
          specialties: ['Pork Belly', 'Beer Battered Fish', 'Craft Beers'],
          recommendationReason: 'Excellent fusion cuisine with great ambiance, perfect for date night within budget',
          priceRange: 'Moderate to High',
          aiScore: 95
        },
        {
          id: '2',
          name: 'The Black Sheep - Bistro & Bar',
          cuisine: 'Continental',
          rating: 4.1,
          costForTwo: 1600,
          location: 'Koramangala, Bangalore',
          specialties: ['Lamb Chops', 'Truffle Fries', 'Craft Cocktails'],
          recommendationReason: 'Upscale bistro experience with excellent service, great value for money',
          priceRange: 'Moderate',
          aiScore: 92
        },
        {
          id: '3',
          name: 'Meghana Foods',
          cuisine: 'Andhra',
          rating: 4.0,
          costForTwo: 800,
          location: 'Multiple Locations, Bangalore',
          specialties: ['Biryani', 'Chicken 65', 'Andhra Meals'],
          recommendationReason: 'Authentic Andhra cuisine, excellent value, leaves budget for drinks/desserts',
          priceRange: 'Budget Friendly',
          aiScore: 88
        },
        {
          id: '4',
          name: 'Caperberry',
          cuisine: 'European',
          rating: 4.4,
          costForTwo: 1900,
          location: 'Koramangala, Bangalore',
          specialties: ['Slow Cooked Meats', 'Artisanal Breads', 'Wine Selection'],
          recommendationReason: 'Fine dining experience with European techniques, just within budget',
          priceRange: 'High',
          aiScore: 96
        },
        {
          id: '5',
          name: 'Gramin',
          cuisine: 'North Indian',
          rating: 4.2,
          costForTwo: 1200,
          location: 'Whitefield, Bangalore',
          specialties: ['Dal Makhani', 'Butter Chicken', 'Roti Selection'],
          recommendationReason: 'Authentic North Indian flavors with modern presentation, comfortable pricing',
          priceRange: 'Moderate',
          aiScore: 90
        }
      ]

      setRestaurants(mockRestaurants)
      setIsLoading(false)
    }

    fetchRecommendations()
  }, [])

  if (isLoading) {
    return (
      <div className="bg-surface text-on-surface min-h-screen">
        {/* TopAppBar */}
        <header className="fixed top-0 left-0 w-full z-50 flex justify-between items-center px-margin-mobile h-16 bg-surface">
          <div className="flex items-center">
            <BackButton />
          </div>
          <h1 className="font-headline-lg-mobile text-headline-lg-mobile text-primary tracking-tight">AI Recommendations</h1>
          <div className="w-8 h-8"></div>
        </header>

        <main className="pt-20 px-margin-mobile max-w-container-max mx-auto">
          {/* Loading State */}
          <div className="space-y-lg">
            <div className="text-center py-lg">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-fixed rounded-full mb-md">
                <span className="material-symbols-outlined text-primary text-2xl animate-spin">refresh</span>
              </div>
              <h2 className="font-headline-lg text-headline-lg text-on-surface mb-xs">AI is Working</h2>
              <p className="font-body-lg text-body-lg text-on-surface-variant">
                Analyzing your preferences to find the perfect restaurants...
              </p>
            </div>

            {/* Shimmer Cards */}
            {[1, 2, 3].map(i => (
              <div key={i} className="bg-surface-container-low rounded-xl p-md ai-shimmer">
                <div className="flex gap-md">
                  <div className="w-20 h-20 bg-surface-variant rounded-lg"></div>
                  <div className="flex-1 space-y-sm">
                    <div className="h-6 bg-surface-variant rounded w-3/4"></div>
                    <div className="h-4 bg-surface-variant rounded w-1/2"></div>
                    <div className="h-4 bg-surface-variant rounded w-2/3"></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </main>
      </div>
    )
  }

  return (
    <div className="bg-surface text-on-surface min-h-screen">
      {/* TopAppBar */}
      <header className="fixed top-0 left-0 w-full z-50 flex justify-between items-center px-margin-mobile h-16 bg-surface">
        <div className="flex items-center">
          <BackButton />
        </div>
        <h1 className="font-headline-lg-mobile text-headline-lg-mobile text-primary tracking-tight">AI Recommendations</h1>
        <div className="w-8 h-8"></div>
      </header>

      <main className="pt-20 px-margin-mobile max-w-container-max mx-auto">
        {/* Results Header */}
        <section className="mb-lg">
          <div className="flex items-center gap-2 mb-xs">
            <span className="material-symbols-outlined text-primary" style={{ fontVariationSettings: "'FILL' 1" }}>
              auto_awesome
            </span>
            <h2 className="font-headline-lg text-headline-lg text-on-surface">Your Perfect Matches</h2>
          </div>
          <p className="font-body-lg text-body-lg text-on-surface-variant">
            Found {restaurants.length} restaurants tailored to your preferences
          </p>
        </section>

        {/* Restaurant Cards */}
        <div className="space-y-lg">
          {restaurants.map((restaurant, index) => (
            <RestaurantCard 
              key={restaurant.id} 
              restaurant={restaurant} 
              index={index}
            />
          ))}
        </div>

        {/* CTA Section */}
        <section className="mt-xl mb-lg text-center">
          <div className="bg-primary-fixed rounded-xl p-lg ai-gradient-border">
            <span className="material-symbols-outlined text-primary text-3xl mb-sm">psychology</span>
            <h3 className="font-headline-lg text-headline-lg text-primary mb-xs">Want More Options?</h3>
            <p className="font-body-lg text-body-lg text-on-surface-variant mb-md">
              Refine your preferences to discover even more perfect matches
            </p>
            <button 
              onClick={() => router.push('/preferences')}
              className="px-6 py-3 bg-primary text-on-primary rounded-xl font-body-lg font-bold active:scale-95 transition-transform"
            >
              Adjust Preferences
            </button>
          </div>
        </section>
      </main>
    </div>
  )
}
