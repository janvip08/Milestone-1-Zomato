'use client'

import React, { useState } from 'react'
import { BudgetButton } from './BudgetButton'
import { RatingButton } from './RatingButton'
import { CuisineTag } from './CuisineTag'
import { DietaryToggle } from './DietaryToggle'
import { AIRecommendButton } from './AIRecommendButton'

export interface Preferences {
  budget: string
  rating: string
  cuisines: string[]
  dietary: {
    vegetarian: boolean
    glutenFree: boolean
    nonVegetarian: boolean
    vegan: boolean
  }
}

export default function PreferencesPage() {
  const [preferences, setPreferences] = useState<Preferences>({
    budget: '$$',
    rating: '4.5',
    cuisines: ['Japanese'],
    dietary: {
      vegetarian: true,
      glutenFree: false,
      nonVegetarian: true,
      vegan: false
    }
  })

  const budgetOptions = ['$', '$$', '$$$', '$$$$']
  const ratingOptions = ['Any', '4.0', '4.5']
  const cuisineOptions = ['Italian', 'Japanese', 'Mexican', 'Indian', 'Chinese', 'Thai', 'French']

  const handleBudgetChange = (budget: string) => {
    setPreferences(prev => ({ ...prev, budget }))
  }

  const handleRatingChange = (rating: string) => {
    setPreferences(prev => ({ ...prev, rating }))
  }

  const handleCuisineToggle = (cuisine: string) => {
    setPreferences(prev => ({
      ...prev,
      cuisines: prev.cuisines.includes(cuisine)
        ? prev.cuisines.filter(c => c !== cuisine)
        : [...prev.cuisines, cuisine]
    }))
  }

  const handleDietaryChange = (key: keyof Preferences['dietary']) => {
    setPreferences(prev => ({
      ...prev,
      dietary: {
        ...prev.dietary,
        [key]: !prev.dietary[key]
      }
    }))
  }

  const clearAllCuisines = () => {
    setPreferences(prev => ({ ...prev, cuisines: [] }))
  }

  return (
    <div className="bg-surface text-on-surface min-h-screen pb-32">
      {/* TopAppBar */}
      <header className="fixed top-0 left-0 w-full z-50 flex justify-between items-center px-margin-mobile h-16 bg-surface">
        <div className="flex items-center">
          <span className="material-symbols-outlined text-on-surface-variant cursor-pointer">menu</span>
        </div>
        <h1 className="font-headline-lg-mobile text-headline-lg-mobile text-primary tracking-tight">CraveAI</h1>
        <div className="w-8 h-8 rounded-full bg-surface-variant overflow-hidden border border-outline-variant">
          <img 
            alt="User" 
            src="/api/placeholder/32/32"
            className="w-full h-full object-cover"
          />
        </div>
      </header>

      <main className="pt-20 px-margin-mobile max-w-container-max mx-auto">
        {/* Header Section */}
        <section className="mb-lg">
          <h2 className="font-headline-xl text-headline-xl text-on-surface mb-xs">Refine Your Flavor</h2>
          <p className="font-body-lg text-body-lg text-on-surface-variant max-w-lg">
            Our AI analyzes your preferences to find the perfect bite. Adjust the filters below to get started.
          </p>
        </section>

        {/* Filters Container */}
        <div className="space-y-lg">
          {/* Budget Section */}
          <section>
            <h3 className="font-title-md text-title-md mb-md flex items-center gap-2">
              Budget
              <span className="material-symbols-outlined text-primary scale-75">payments</span>
            </h3>
            <div className="flex gap-sm overflow-x-auto pb-2 scrollbar-hide">
              {budgetOptions.map(budget => (
                <BudgetButton
                  key={budget}
                  budget={budget}
                  isSelected={preferences.budget === budget}
                  onClick={() => handleBudgetChange(budget)}
                />
              ))}
            </div>
          </section>

          {/* Rating Section */}
          <section>
            <h3 className="font-title-md text-title-md mb-md flex items-center gap-2">
              Minimum Rating
              <span className="material-symbols-outlined text-secondary scale-75">star</span>
            </h3>
            <div className="flex gap-sm">
              {ratingOptions.map(rating => (
                <RatingButton
                  key={rating}
                  rating={rating}
                  isSelected={preferences.rating === rating}
                  onClick={() => handleRatingChange(rating)}
                />
              ))}
            </div>
          </section>

          {/* Cuisine Section */}
          <section>
            <div className="flex justify-between items-center mb-md">
              <h3 className="font-title-md text-title-md flex items-center gap-2">
                Cuisine
                <span className="material-symbols-outlined text-primary scale-75">restaurant_menu</span>
              </h3>
              <span 
                className="font-label-caps text-label-caps text-primary cursor-pointer"
                onClick={clearAllCuisines}
              >
                Clear All
              </span>
            </div>
            <div className="flex flex-wrap gap-base">
              {cuisineOptions.map(cuisine => (
                <CuisineTag
                  key={cuisine}
                  cuisine={cuisine}
                  isSelected={preferences.cuisines.includes(cuisine)}
                  onClick={() => handleCuisineToggle(cuisine)}
                />
              ))}
            </div>
          </section>

          {/* Dietary Preferences Section */}
          <section className="bg-surface-container-low rounded-xl p-md">
            <h3 className="font-title-md text-title-md mb-md flex items-center gap-2">
              Dietary Requirements
              <span className="material-symbols-outlined text-tertiary scale-75">settings_heart</span>
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-md">
              <DietaryToggle
                label="Vegetarian"
                checked={preferences.dietary.vegetarian}
                onChange={() => handleDietaryChange('vegetarian')}
              />
              <DietaryToggle
                label="Gluten-Free"
                checked={preferences.dietary.glutenFree}
                onChange={() => handleDietaryChange('glutenFree')}
              />
              <DietaryToggle
                label="Non-Vegetarian"
                checked={preferences.dietary.nonVegetarian}
                onChange={() => handleDietaryChange('nonVegetarian')}
              />
              <DietaryToggle
                label="Vegan"
                checked={preferences.dietary.vegan}
                onChange={() => handleDietaryChange('vegan')}
              />
            </div>
          </section>
        </div>
      </main>

      {/* Sticky Recommendation Action */}
      <AIRecommendButton preferences={preferences} />
    </div>
  )
}
