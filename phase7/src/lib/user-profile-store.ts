import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export interface UserProfile {
  id: string
  email: string
  name: string
  preferences: {
    cuisine: string[]
    priceRange: string
    dietaryRestrictions: string[]
    preferredLocations: string[]
    occasionPreferences: Record<string, number>
  }
  behavior: {
    averageRating: number
    priceSensitivity: number
    locationFlexibility: number
    cuisineAdventurousness: number
    lastActiveDate: string
    totalRecommendations: number
    feedbackHistory: {
      restaurantId: string
      rating: number
      feedback: string
      timestamp: string
    }[]
  }
  personalization: {
    learningModel: Record<string, number>
    recommendationHistory: {
      restaurantId: string
      score: number
      accepted: boolean
      timestamp: string
    }[]
    userEmbedding: number[]
    clusterId: string
  }
  createdAt: string
  updatedAt: string
}

interface UserProfileStore {
  profiles: Record<string, UserProfile>
  currentProfileId: string | null
  isLoading: boolean
  error: string | null
  
  // Actions
  createProfile: (profile: Omit<UserProfile, 'id' | 'createdAt' | 'updatedAt'>) => Promise<UserProfile>
  updateProfile: (id: string, updates: Partial<UserProfile>) => Promise<void>
  getProfile: (id: string) => Promise<UserProfile | null>
  setCurrentProfile: (id: string) => void
  updatePreferences: (id: string, preferences: Partial<UserProfile['preferences']>) => Promise<void>
  recordFeedback: (id: string, restaurantId: string, rating: number, feedback: string) => Promise<void>
  recordRecommendationInteraction: (id: string, restaurantId: string, score: number, accepted: boolean) => Promise<void>
  updateUserEmbedding: (id: string, embedding: number[]) => Promise<void>
  deleteProfile: (id: string) => Promise<void>
}

export const useUserProfileStore = create<UserProfileStore>()(
  persist(
    (set, get) => ({
      profiles: {},
      currentProfileId: null,
      isLoading: false,
      error: null,

      createProfile: async (profileData) => {
        set({ isLoading: true, error: null })
        
        try {
          const response = await fetch('/api/user-profiles', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(profileData)
          })
          
          if (!response.ok) {
            throw new Error('Failed to create profile')
          }
          
          const newProfile: UserProfile = await response.json()
          
          set(state => ({
            profiles: { ...state.profiles, [newProfile.id]: newProfile },
            currentProfileId: newProfile.id,
            isLoading: false
          }))
          
          return newProfile
        } catch (error) {
          set({ isLoading: false, error: error instanceof Error ? error.message : 'Unknown error' })
          throw error
        }
      },

      updateProfile: async (id, updates) => {
        set({ isLoading: true, error: null })
        
        try {
          const response = await fetch(`/api/user-profiles/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(updates)
          })
          
          if (!response.ok) {
            throw new Error('Failed to update profile')
          }
          
          const updatedProfile: UserProfile = await response.json()
          
          set(state => ({
            profiles: { ...state.profiles, [id]: updatedProfile },
            isLoading: false
          }))
        } catch (error) {
          set({ isLoading: false, error: error instanceof Error ? error.message : 'Unknown error' })
          throw error
        }
      },

      getProfile: async (id) => {
        // Check cache first
        const cached = get().profiles[id]
        if (cached) {
          return cached
        }
        
        set({ isLoading: true, error: null })
        
        try {
          const response = await fetch(`/api/user-profiles/${id}`)
          
          if (!response.ok) {
            throw new Error('Failed to get profile')
          }
          
          const profile: UserProfile = await response.json()
          
          set(state => ({
            profiles: { ...state.profiles, [id]: profile },
            isLoading: false
          }))
          
          return profile
        } catch (error) {
          set({ isLoading: false, error: error instanceof Error ? error.message : 'Unknown error' })
          return null
        }
      },

      setCurrentProfile: (id) => {
        set({ currentProfileId: id })
      },

      updatePreferences: async (id, preferences) => {
        const currentProfile = get().profiles[id]
        if (!currentProfile) return
        
        const updatedPreferences = { ...currentProfile.preferences, ...preferences }
        
        await get().updateProfile(id, { 
          preferences: updatedPreferences,
          updatedAt: new Date().toISOString()
        })
      },

      recordFeedback: async (id, restaurantId, rating, feedback) => {
        const currentProfile = get().profiles[id]
        if (!currentProfile) return
        
        const newFeedback = {
          restaurantId,
          rating,
          feedback,
          timestamp: new Date().toISOString()
        }
        
        const updatedFeedbackHistory = [...currentProfile.behavior.feedbackHistory, newFeedback]
        const updatedAverageRating = updatedFeedbackHistory.reduce((sum, f) => sum + f.rating, 0) / updatedFeedbackHistory.length
        
        await get().updateProfile(id, {
          behavior: {
            ...currentProfile.behavior,
            feedbackHistory: updatedFeedbackHistory,
            averageRating: updatedAverageRating,
            lastActiveDate: new Date().toISOString()
          }
        })
      },

      recordRecommendationInteraction: async (id, restaurantId, score, accepted) => {
        const currentProfile = get().profiles[id]
        if (!currentProfile) return
        
        const newInteraction = {
          restaurantId,
          score,
          accepted,
          timestamp: new Date().toISOString()
        }
        
        const updatedHistory = [...currentProfile.personalization.recommendationHistory, newInteraction]
        const totalRecommendations = currentProfile.behavior.totalRecommendations + 1
        
        await get().updateProfile(id, {
          personalization: {
            ...currentProfile.personalization,
            recommendationHistory: updatedHistory
          },
          behavior: {
            ...currentProfile.behavior,
            totalRecommendations,
            lastActiveDate: new Date().toISOString()
          }
        })
      },

      updateUserEmbedding: async (id, embedding) => {
        const currentProfile = get().profiles[id]
        if (!currentProfile) return
        
        await get().updateProfile(id, {
          personalization: {
            ...currentProfile.personalization,
            userEmbedding: embedding
          }
        })
      },

      deleteProfile: async (id) => {
        set({ isLoading: true, error: null })
        
        try {
          const response = await fetch(`/api/user-profiles/${id}`, {
            method: 'DELETE'
          })
          
          if (!response.ok) {
            throw new Error('Failed to delete profile')
          }
          
          const profiles = get().profiles
          delete profiles[id]
          
          set(state => ({
            profiles,
            currentProfileId: state.currentProfileId === id ? null : state.currentProfileId,
            isLoading: false
          }))
        } catch (error) {
          set({ isLoading: false, error: error instanceof Error ? error.message : 'Unknown error' })
          throw error
        }
      }
    }),
    {
      name: 'user-profile-store',
      partialize: (state) => ({
        profiles: state.profiles,
        currentProfileId: state.currentProfileId
      })
    }
  )
)

// Selectors
export const useCurrentProfile = () => {
  const store = useUserProfileStore()
  return store.currentProfileId ? store.profiles[store.currentProfileId] : null
}

export const useProfilePreferences = (profileId: string) => {
  const profiles = useUserProfileStore(state => state.profiles)
  return profiles[profileId]?.preferences || null
}

export const useProfileBehavior = (profileId: string) => {
  const profiles = useUserProfileStore(state => state.profiles)
  return profiles[profileId]?.behavior || null
}

export const useProfilePersonalization = (profileId: string) => {
  const profiles = useUserProfileStore(state => state.profiles)
  return profiles[profileId]?.personalization || null
}
