'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { useUserProfileStore, useCurrentProfile } from '@/lib/user-profile-store'
import { useHybridRanking } from '@/lib/hybrid-ranking'
import { useMultiCityStore } from '@/lib/multi-city-optimization'
import { useABTestingStore } from '@/lib/ab-testing-framework'

export default function HomePage() {
  const [recommendations, setRecommendations] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  
  const currentProfile = useCurrentProfile()
  const { rankRestaurants } = useHybridRanking()
  const { detectUserLocation, currentCity } = useMultiCityStore()
  const { getActiveExperiments } = useABTestingStore()
  
  const activeExperiments = getActiveExperiments()
  
  useEffect(() => {
    // Initialize user location detection
    if (!currentCity) {
      detectUserLocation()
    }
    
    // Load active experiments
    if (activeExperiments.length > 0) {
      console.log('Active experiments:', activeExperiments)
    }
  }, [detectUserLocation, currentCity, activeExperiments])
  
  const handleGetRecommendations = async () => {
    if (!currentProfile) {
      alert('Please create a profile first')
      return
    }
    
    setIsLoading(true)
    
    try {
      const preferences = {
        location: currentProfile.preferences.preferredLocations[0] || 'Bangalore',
        cuisine: currentProfile.preferences.cuisine[0] || 'Italian',
        maxCostForTwo: 1000,
        occasion: 'dinner'
      }
      
      // Get sample restaurants (in real app, this would come from API)
      const sampleRestaurants = [
        {
          id: '1',
          name: 'Trattoria Italiana',
          rating: 4.5,
          costForTwo: 800,
          cuisine: 'Italian',
          distance: 2.5,
          popularity: 150
        },
        {
          id: '2',
          name: 'Pasta Paradise',
          rating: 4.2,
          costForTwo: 600,
          cuisine: 'Italian',
          distance: 3.1,
          popularity: 120
        },
        {
          id: '3',
          name: 'Pizza Express',
          rating: 4.8,
          costForTwo: 750,
          cuisine: 'Italian',
          distance: 1.8,
          popularity: 200
        }
      ]
      
      const results = await rankRestaurants(preferences, sampleRestaurants)
      setRecommendations(results)
    } catch (error) {
      console.error('Error getting recommendations:', error)
      alert('Failed to get recommendations. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }
  
  return (
    <div className="container mx-auto p-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Welcome Card */}
        <Card>
          <CardHeader>
            <CardTitle>Welcome to Advanced Restaurant Recommendations</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <p className="text-gray-600">
                Experience personalized restaurant recommendations powered by AI, vector search, and hybrid ranking algorithms.
              </p>
              
              {currentProfile ? (
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Profile:</span>
                    <Badge variant="secondary">{currentProfile.name}</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Current City:</span>
                    <Badge variant="outline">
                      {currentCity ? 'Loading...' : 'Not Set'}
                    </Badge>
                  </div>
                </div>
              ) : (
                <div className="text-center py-4">
                  <p className="text-gray-500 mb-4">No profile found</p>
                  <Button onClick={() => window.location.href = '/profile'}>
                    Create Profile
                  </Button>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
        
        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <Button 
                onClick={handleGetRecommendations}
                disabled={isLoading || !currentProfile}
                className="w-full"
              >
                {isLoading ? 'Getting Recommendations...' : 'Get Recommendations'}
              </Button>
              
              <Button 
                variant="outline"
                onClick={() => window.location.href = '/experiments'}
                className="w-full"
              >
                A/B Testing
              </Button>
              
              <Button 
                variant="outline"
                onClick={() => window.location.href = '/analytics'}
                className="w-full"
              >
                Analytics
              </Button>
            </div>
          </CardContent>
        </Card>
        
        {/* Active Experiments */}
        {activeExperiments.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Active Experiments</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {activeExperiments.map((experiment) => (
                  <div key={experiment.id} className="flex items-center justify-between p-3 border rounded">
                    <div>
                      <h4 className="font-medium">{experiment.name}</h4>
                      <p className="text-sm text-gray-600">{experiment.description}</p>
                    </div>
                    <Badge variant={experiment.status === 'active' ? 'default' : 'secondary'}>
                      {experiment.status}
                    </Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
        
        {/* Recommendations Display */}
        {recommendations.length > 0 && (
          <Card className="md:col-span-2 lg:col-span-3">
            <CardHeader>
              <CardTitle>Personalized Recommendations</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {recommendations.map((result, index) => (
                  <div key={result.restaurantId} className="border rounded-lg p-4">
                    <div className="flex items-start justify-between">
                      <div>
                        <h3 className="font-semibold text-lg">
                          {index + 1}. Restaurant {result.restaurantId}
                        </h3>
                        <p className="text-sm text-gray-600 mt-1">
                          Strategy: {result.strategy}
                        </p>
                        <p className="text-sm text-gray-500 mt-2">
                          {result.explanation}
                        </p>
                      </div>
                      <Badge variant="outline">
                        Score: {result.score.toFixed(3)}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
      
      {/* Feature Highlights */}
      <div className="mt-8">
        <h2 className="text-2xl font-bold mb-6">Phase 7 Advanced Features</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>🧠 Personalized Profiles</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600">
                User profiles with preference learning, behavior tracking, and recommendation memory.
              </p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle>🔍 Vector Search</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600">
                Advanced vector embeddings and similarity search for semantic restaurant matching.
              </p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle>⚖️ Hybrid Ranking</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600">
                Combines rule-based, vector-based, and LLM-powered ranking strategies.
              </p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle>🌍 Multi-City Support</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600">
                Optimized recommendations across multiple cities with location detection.
              </p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle>🧪 A/B Testing</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600">
                Experiment with different prompts, ranking strategies, and UI variations.
              </p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle>📊 Advanced Analytics</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600">
                Comprehensive analytics for experiments, user behavior, and system performance.
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
