import { create } from 'zustand'

export interface City {
  id: string
  name: string
  country: string
  state: string
  coordinates: {
    latitude: number
    longitude: number
  }
  timezone: string
  currency: string
  language: string
  popularCuisines: string[]
  averageCostForTwo: number
  restaurantCount: number
  isActive: boolean
  metadata: Record<string, any>
}

export interface CityOptimizationConfig {
  defaultCity: string
  supportedCities: string[]
  autoDetectLocation: boolean
  locationDetectionMethod: 'gps' | 'ip' | 'manual'
  cacheStrategy: 'memory' | 'localStorage' | 'indexedDB'
  maxCachedCities: number
  nearbyCityRadius: number // in km
}

export interface LocationData {
  latitude: number
  longitude: number
  accuracy: number
  timestamp: number
  source: 'gps' | 'ip' | 'manual'
}

interface MultiCityStore {
  cities: Record<string, City>
  currentCityId: string | null
  userLocation: LocationData | null
  nearbyCities: City[]
  config: CityOptimizationConfig
  isLoading: boolean
  error: string | null
  
  // Actions
  loadCities: () => Promise<void>
  setCurrentCity: (cityId: string) => void
  detectUserLocation: () => Promise<LocationData | null>
  updateCity: (id: string, updates: Partial<City>) => Promise<void>
  addCity: (city: Omit<City, 'id'>) => Promise<City>
  removeCity: (id: string) => Promise<void>
  getNearbyCities: (latitude: number, longitude: number, radius?: number) => City[]
  searchCities: (query: string) => City[]
  optimizeForCity: (cityId: string, preferences: any) => Promise<any>
  updateConfig: (config: Partial<CityOptimizationConfig>) => void
}

export const useMultiCityStore = create<MultiCityStore>((set, get) => ({
  cities: {},
  currentCityId: null,
  userLocation: null,
  nearbyCities: [],
  config: {
    defaultCity: 'bangalore',
    supportedCities: ['bangalore', 'mumbai', 'delhi', 'chennai', 'hyderabad', 'kolkata', 'pune', 'jaipur', 'ahmedabad', 'chandigarh'],
    autoDetectLocation: true,
    locationDetectionMethod: 'gps',
    cacheStrategy: 'localStorage',
    maxCachedCities: 50,
    nearbyCityRadius: 50
  },
  isLoading: false,
  error: null,

  loadCities: async () => {
    set({ isLoading: true, error: null })
    
    try {
      // Try to load from cache first
      const cachedCities = get().loadCitiesFromCache()
      if (cachedCities && Object.keys(cachedCities).length > 0) {
        set({ cities: cachedCities, isLoading: false })
        return
      }
      
      // Load from API
      const response = await fetch('/api/cities')
      
      if (!response.ok) {
        throw new Error('Failed to load cities')
      }
      
      const citiesData: City[] = await response.json()
      
      // Convert to record
      const citiesRecord = citiesData.reduce((acc, city) => {
        acc[city.id] = city
        return acc
      }, {} as Record<string, City>)
      
      // Cache cities
      get().saveCitiesToCache(citiesRecord)
      
      set({ 
        cities: citiesRecord, 
        isLoading: false 
      })
    } catch (error) {
      set({ 
        isLoading: false, 
        error: error instanceof Error ? error.message : 'Unknown error' 
      })
    }
  },

  setCurrentCity: (cityId) => {
    const city = get().cities[cityId]
    if (city) {
      set({ currentCityId: cityId })
      get().saveCurrentCityToStorage(cityId)
    }
  },

  detectUserLocation: async () => {
    const config = get().config
    
    if (!config.autoDetectLocation) {
      return null
    }
    
    set({ isLoading: true, error: null })
    
    try {
      let locationData: LocationData | null = null
      
      switch (config.locationDetectionMethod) {
        case 'gps':
          locationData = await get().detectLocationFromGPS()
          break
        case 'ip':
          locationData = await get().detectLocationFromIP()
          break
        case 'manual':
          locationData = await get().detectLocationFromManual()
          break
      }
      
      if (locationData) {
        const nearbyCities = get().getNearbyCities(
          locationData.latitude, 
          locationData.longitude, 
          config.nearbyCityRadius
        )
        
        set({ 
          userLocation: locationData, 
          nearbyCities,
          isLoading: false 
        })
        
        // Auto-select nearest city if no current city
        if (!get().currentCityId && nearbyCities.length > 0) {
          get().setCurrentCity(nearbyCities[0].id)
        }
      } else {
        set({ isLoading: false })
      }
      
      return locationData
    } catch (error) {
      set({ 
        isLoading: false, 
        error: error instanceof Error ? error.message : 'Location detection failed' 
      })
      return null
    }
  },

  updateCity: async (id, updates) => {
    set({ isLoading: true, error: null })
    
    try {
      const response = await fetch(`/api/cities/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates)
      })
      
      if (!response.ok) {
        throw new Error('Failed to update city')
      }
      
      const updatedCity: City = await response.json()
      
      set(state => ({
        cities: { ...state.cities, [id]: updatedCity },
        isLoading: false
      }))
      
      // Update cache
      get().saveCitiesToCache({ ...get().cities, [id]: updatedCity })
    } catch (error) {
      set({ 
        isLoading: false, 
        error: error instanceof Error ? error.message : 'Unknown error' 
      })
      throw error
    }
  },

  addCity: async (cityData) => {
    set({ isLoading: true, error: null })
    
    try {
      const response = await fetch('/api/cities', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(cityData)
      })
      
      if (!response.ok) {
        throw new Error('Failed to add city')
      }
      
      const newCity: City = await response.json()
      
      set(state => ({
        cities: { ...state.cities, [newCity.id]: newCity },
        isLoading: false
      }))
      
      // Update cache
      get().saveCitiesToCache({ ...get().cities, [newCity.id]: newCity })
      
      return newCity
    } catch (error) {
      set({ 
        isLoading: false, 
        error: error instanceof Error ? error.message : 'Unknown error' 
      })
      throw error
    }
  },

  removeCity: async (id) => {
    set({ isLoading: true, error: null })
    
    try {
      const response = await fetch(`/api/cities/${id}`, {
        method: 'DELETE'
      })
      
      if (!response.ok) {
        throw new Error('Failed to remove city')
      }
      
      const cities = get().cities
      delete cities[id]
      
      set(state => ({
        cities,
        currentCityId: state.currentCityId === id ? null : state.currentCityId,
        isLoading: false
      }))
      
      // Update cache
      get().saveCitiesToCache(cities)
    } catch (error) {
      set({ 
        isLoading: false, 
        error: error instanceof Error ? error.message : 'Unknown error' 
      })
      throw error
    }
  },

  getNearbyCities: (latitude, longitude, radius = 50) => {
    const cities = Object.values(get().cities)
    const nearbyCities: City[] = []
    
    for (const city of cities) {
      if (!city.coordinates) continue
      
      const distance = calculateDistance(
        latitude, longitude,
        city.coordinates.latitude,
        city.coordinates.longitude
      )
      
      if (distance <= radius) {
        nearbyCities.push({ ...city, distance })
      }
    }
    
    return nearbyCities.sort((a, b) => (a.distance || 0) - (b.distance || 0))
  },

  searchCities: (query) => {
    const cities = Object.values(get().cities)
    const lowercaseQuery = query.toLowerCase()
    
    return cities.filter(city => 
      city.name.toLowerCase().includes(lowercaseQuery) ||
      city.state.toLowerCase().includes(lowercaseQuery) ||
      city.country.toLowerCase().includes(lowercaseQuery) ||
      city.popularCuisines.some(cuisine => 
        cuisine.toLowerCase().includes(lowercaseQuery)
      )
    )
  },

  optimizeForCity: async (cityId, preferences) => {
    const city = get().cities[cityId]
    if (!city) {
      throw new Error(`City ${cityId} not found`)
    }
    
    set({ isLoading: true, error: null })
    
    try {
      // Optimize preferences for the specific city
      const optimizedPreferences = {
        ...preferences,
        location: city.name,
        maxCostForTwo: Math.min(
          preferences.maxCostForTwo || 2000,
          city.averageCostForTwo * 1.5 // Allow 50% above city average
        ),
        currency: city.currency,
        timezone: city.timezone,
        popularCuisines: city.popularCuisines
      }
      
      // Get city-specific restaurant data
      const restaurantResponse = await fetch(`/api/restaurants?city=${cityId}`)
      
      if (!restaurantResponse.ok) {
        throw new Error('Failed to load city restaurants')
      }
      
      const cityRestaurants = await restaurantResponse.json()
      
      // Apply city-specific optimizations
      const cityOptimizedData = {
        preferences: optimizedPreferences,
        restaurants: cityRestaurants,
        city: {
          id: city.id,
          name: city.name,
          coordinates: city.coordinates,
          timezone: city.timezone,
          currency: city.currency
        },
        optimizations: {
          priceAdjustment: city.averageCostForTwo / 1000, // Price adjustment factor
          cuisineBoost: city.popularCuisines, // Boost popular cuisines
          locationBias: city.coordinates, // Location-based bias
          searchRadius: get().config.nearbyCityRadius
        }
      }
      
      set({ isLoading: false })
      return cityOptimizedData
    } catch (error) {
      set({ 
        isLoading: false, 
        error: error instanceof Error ? error.message : 'City optimization failed' 
      })
      throw error
    }
  },

  updateConfig: (configUpdates) => {
    set(state => ({
      config: { ...state.config, ...configUpdates }
    }))
  },

  // Location detection methods
  detectLocationFromGPS: async (): Promise<LocationData | null> => {
    return new Promise((resolve) => {
      if (!navigator.geolocation) {
        resolve(null)
        return
      }
      
      navigator.geolocation.getCurrentPosition(
        (position) => {
          resolve({
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
            accuracy: position.coords.accuracy,
            timestamp: Date.now(),
            source: 'gps'
          })
        },
        (error) => {
          console.error('GPS location error:', error)
          resolve(null)
        },
        {
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 300000 // 5 minutes
        }
      )
    })
  },

  detectLocationFromIP: async (): Promise<LocationData | null> => {
    try {
      const response = await fetch('https://ipapi.co/json/')
      
      if (!response.ok) {
        throw new Error('Failed to get location from IP')
      }
      
      const data = await response.json()
      
      return {
        latitude: data.latitude,
        longitude: data.longitude,
        accuracy: 1000, // IP-based location is less accurate
        timestamp: Date.now(),
        source: 'ip'
      }
    } catch (error) {
      console.error('IP location detection error:', error)
      return null
    }
  },

  detectLocationFromManual: async (): Promise<LocationData | null> => {
    // This would typically show a modal for manual location entry
    // For now, return null
    return null
  },

  // Cache management
  loadCitiesFromCache: (): Record<string, City> | null => {
    const config = get().config
    
    try {
      switch (config.cacheStrategy) {
        case 'localStorage':
          const cached = localStorage.getItem('cities')
          return cached ? JSON.parse(cached) : null
        case 'indexedDB':
          return get().loadFromIndexedDB()
        case 'memory':
        default:
          return null
      }
    } catch (error) {
      console.error('Error loading cities from cache:', error)
      return null
    }
  },

  saveCitiesToCache: (cities: Record<string, City>) => {
    const config = get().config
    
    try {
      switch (config.cacheStrategy) {
        case 'localStorage':
          localStorage.setItem('cities', JSON.stringify(cities))
          break
        case 'indexedDB':
          get().saveToIndexedDB(cities)
          break
        case 'memory':
        default:
          // Memory caching is handled by Zustand persist
          break
      }
    } catch (error) {
      console.error('Error saving cities to cache:', error)
    }
  },

  saveCurrentCityToStorage: (cityId: string) => {
    try {
      localStorage.setItem('currentCity', cityId)
    } catch (error) {
      console.error('Error saving current city:', error)
    }
  },

  loadCurrentCityFromStorage: (): string | null => {
    try {
      return localStorage.getItem('currentCity')
    } catch (error) {
      console.error('Error loading current city:', error)
      return null
    }
  },

  // IndexedDB operations (simplified)
  loadFromIndexedDB: async (): Promise<Record<string, City> | null> => {
    // Simplified IndexedDB implementation
    return new Promise((resolve) => {
      const request = indexedDB.open('CitiesDB', 1)
      
      request.onerror = () => {
        console.error('IndexedDB error')
        resolve(null)
      }
      
      request.onsuccess = () => {
        const db = request.result
        const transaction = db.transaction(['cities'], 'readonly')
        const store = transaction.objectStore('cities')
        const getAllRequest = store.getAll()
        
        getAllRequest.onsuccess = () => {
          const cities = getAllRequest.result.reduce((acc, city: any) => {
            acc[city.id] = city
            return acc
          }, {})
          resolve(cities)
        }
      }
    })
  },

  saveToIndexedDB: async (cities: Record<string, City>) => {
    // Simplified IndexedDB implementation
    return new Promise((resolve, reject) => {
      const request = indexedDB.open('CitiesDB', 1)
      
      request.onerror = () => {
        reject(new Error('IndexedDB error'))
      }
      
      request.onsuccess = () => {
        const db = request.result
        const transaction = db.transaction(['cities'], 'readwrite')
        const store = transaction.objectStore('cities')
        
        // Clear existing data
        store.clear()
        
        // Add all cities
        Object.values(cities).forEach((city: any) => {
          store.add(city)
        })
        
        transaction.oncomplete = () => {
          resolve()
        }
        
        transaction.onerror = () => {
          reject(new Error('IndexedDB transaction error'))
        }
      }
    })
  }
}))

// Utility functions
function calculateDistance(
  lat1: number, 
  lon1: number, 
  lat2: number, 
  lon2: number
): number {
  const R = 6371 // Earth's radius in km
  const dLat = toRadians(lat2 - lat1)
  const dLon = toRadians(lon2 - lon1)
  
  const a = 
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(toRadians(lat1)) * Math.cos(toRadians(lat2)) *
    Math.sin(dLon / 2) * Math.sin(dLon / 2)
  
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
  
  return R * c
}

function toRadians(degrees: number): number {
  return degrees * (Math.PI / 180)
}

// Selectors
export const useCurrentCity = () => {
  const currentCityId = useMultiCityStore(state => state.currentCityId)
  const cities = useMultiCityStore(state => state.cities)
  return currentCityId ? cities[currentCityId] : null
}

export const useNearbyCities = () => {
  return useMultiCityStore(state => state.nearbyCities)
}

export const useSupportedCities = () => {
  const cities = useMultiCityStore(state => state.cities)
  const supportedCityIds = useMultiCityStore(state => state.config.supportedCities)
  
  return supportedCityIds
    .map(id => cities[id])
    .filter(city => city && city.isActive)
    .sort((a, b) => a.name.localeCompare(b.name))
}

export const useCityById = (id: string) => {
  const cities = useMultiCityStore(state => state.cities)
  return cities[id]
}

export const useCitiesByCountry = (country: string) => {
  const cities = useMultiCityStore(state => state.cities)
  return Object.values(cities).filter(city => 
    city.country.toLowerCase() === country.toLowerCase()
  )
}

export const useCitiesByState = (state: string) => {
  const cities = useMultiCityStore(state => state.cities)
  return Object.values(cities).filter(city => 
    city.state.toLowerCase() === state.toLowerCase()
  )
}
