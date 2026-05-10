import { create } from 'zustand'

export interface VectorEmbedding {
  id: string
  type: 'restaurant' | 'user' | 'query'
  embedding: number[]
  metadata: Record<string, any>
  createdAt: string
  updatedAt: string
}

export interface SimilaritySearchResult {
  id: string
  score: number
  metadata: Record<string, any>
  distance: number
}

export interface VectorDatabaseConfig {
  embeddingDimension: number
  similarityThreshold: number
  maxResults: number
  indexType: 'hnsw' | 'ivf' | 'flat'
}

interface VectorDatabaseStore {
  embeddings: Record<string, VectorEmbedding>
  config: VectorDatabaseConfig
  isLoading: boolean
  error: string | null
  
  // Actions
  addEmbedding: (embedding: Omit<VectorEmbedding, 'createdAt' | 'updatedAt'>) => Promise<VectorEmbedding>
  updateEmbedding: (id: string, updates: Partial<VectorEmbedding>) => Promise<void>
  getEmbedding: (id: string) => Promise<VectorEmbedding | null>
  deleteEmbedding: (id: string) => Promise<void>
  searchSimilar: (queryEmbedding: number[], type: VectorEmbedding['type'], limit?: number) => Promise<SimilaritySearchResult[]>
  batchAddEmbeddings: (embeddings: Omit<VectorEmbedding, 'createdAt' | 'updatedAt'>[]) => Promise<void>
  updateConfig: (config: Partial<VectorDatabaseConfig>) => void
  clearEmbeddings: () => Promise<void>
}

export const useVectorDatabase = create<VectorDatabaseStore>((set, get) => ({
  embeddings: {},
  config: {
    embeddingDimension: 384,
    similarityThreshold: 0.7,
    maxResults: 100,
    indexType: 'hnsw'
  },
  isLoading: false,
  error: null,

  addEmbedding: async (embeddingData) => {
    set({ isLoading: true, error: null })
    
    try {
      const embedding: VectorEmbedding = {
        ...embeddingData,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      }
      
      const response = await fetch('/api/vector-database/embeddings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(embedding)
      })
      
      if (!response.ok) {
        throw new Error('Failed to add embedding')
      }
      
      const savedEmbedding: VectorEmbedding = await response.json()
      
      set(state => ({
        embeddings: { ...state.embeddings, [savedEmbedding.id]: savedEmbedding },
        isLoading: false
      }))
      
      return savedEmbedding
    } catch (error) {
      set({ isLoading: false, error: error instanceof Error ? error.message : 'Unknown error' })
      throw error
    }
  },

  updateEmbedding: async (id, updates) => {
    set({ isLoading: true, error: null })
    
    try {
      const response = await fetch(`/api/vector-database/embeddings/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...updates, updatedAt: new Date().toISOString() })
      })
      
      if (!response.ok) {
        throw new Error('Failed to update embedding')
      }
      
      const updatedEmbedding: VectorEmbedding = await response.json()
      
      set(state => ({
        embeddings: { ...state.embeddings, [id]: updatedEmbedding },
        isLoading: false
      }))
    } catch (error) {
      set({ isLoading: false, error: error instanceof Error ? error.message : 'Unknown error' })
      throw error
    }
  },

  getEmbedding: async (id) => {
    const cached = get().embeddings[id]
    if (cached) {
      return cached
    }
    
    set({ isLoading: true, error: null })
    
    try {
      const response = await fetch(`/api/vector-database/embeddings/${id}`)
      
      if (!response.ok) {
        throw new Error('Failed to get embedding')
      }
      
      const embedding: VectorEmbedding = await response.json()
      
      set(state => ({
        embeddings: { ...state.embeddings, [id]: embedding },
        isLoading: false
      }))
      
      return embedding
    } catch (error) {
      set({ isLoading: false, error: error instanceof Error ? error.message : 'Unknown error' })
      return null
    }
  },

  deleteEmbedding: async (id) => {
    set({ isLoading: true, error: null })
    
    try {
      const response = await fetch(`/api/vector-database/embeddings/${id}`, {
        method: 'DELETE'
      })
      
      if (!response.ok) {
        throw new Error('Failed to delete embedding')
      }
      
      const embeddings = get().embeddings
      delete embeddings[id]
      
      set(state => ({
        embeddings,
        isLoading: false
      }))
    } catch (error) {
      set({ isLoading: false, error: error instanceof Error ? error.message : 'Unknown error' })
      throw error
    }
  },

  searchSimilar: async (queryEmbedding, type, limit = 10) => {
    set({ isLoading: true, error: null })
    
    try {
      const response = await fetch('/api/vector-database/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: queryEmbedding,
          type,
          limit,
          threshold: get().config.similarityThreshold
        })
      })
      
      if (!response.ok) {
        throw new Error('Failed to search embeddings')
      }
      
      const results: SimilaritySearchResult[] = await response.json()
      set({ isLoading: false })
      
      return results
    } catch (error) {
      set({ isLoading: false, error: error instanceof Error ? error.message : 'Unknown error' })
      throw error
    }
  },

  batchAddEmbeddings: async (embeddingsData) => {
    set({ isLoading: true, error: null })
    
    try {
      const embeddings: VectorEmbedding[] = embeddingsData.map(data => ({
        ...data,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      }))
      
      const response = await fetch('/api/vector-database/embeddings/batch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ embeddings })
      })
      
      if (!response.ok) {
        throw new Error('Failed to batch add embeddings')
      }
      
      const savedEmbeddings: VectorEmbedding[] = await response.json()
      
      const newEmbeddings = savedEmbeddings.reduce((acc, emb) => {
        acc[emb.id] = emb
        return acc
      }, {} as Record<string, VectorEmbedding>)
      
      set(state => ({
        embeddings: { ...state.embeddings, ...newEmbeddings },
        isLoading: false
      }))
    } catch (error) {
      set({ isLoading: false, error: error instanceof Error ? error.message : 'Unknown error' })
      throw error
    }
  },

  updateConfig: (configUpdates) => {
    set(state => ({
      config: { ...state.config, ...configUpdates }
    }))
  },

  clearEmbeddings: async () => {
    set({ isLoading: true, error: null })
    
    try {
      const response = await fetch('/api/vector-database/embeddings', {
        method: 'DELETE'
      })
      
      if (!response.ok) {
        throw new Error('Failed to clear embeddings')
      }
      
      set({
        embeddings: {},
        isLoading: false
      })
    } catch (error) {
      set({ isLoading: false, error: error instanceof Error ? error.message : 'Unknown error' })
      throw error
    }
  }
}))

// Utility functions
export const calculateCosineSimilarity = (vecA: number[], vecB: number[]): number => {
  if (vecA.length !== vecB.length) {
    throw new Error('Vectors must have same length')
  }
  
  let dotProduct = 0
  let normA = 0
  let normB = 0
  
  for (let i = 0; i < vecA.length; i++) {
    dotProduct += vecA[i] * vecB[i]
    normA += vecA[i] * vecA[i]
    normB += vecB[i] * vecB[i]
  }
  
  normA = Math.sqrt(normA)
  normB = Math.sqrt(normB)
  
  if (normA === 0 || normB === 0) {
    return 0
  }
  
  return dotProduct / (normA * normB)
}

export const calculateEuclideanDistance = (vecA: number[], vecB: number[]): number => {
  if (vecA.length !== vecB.length) {
    throw new Error('Vectors must have same length')
  }
  
  let sum = 0
  for (let i = 0; i < vecA.length; i++) {
    const diff = vecA[i] - vecB[i]
    sum += diff * diff
  }
  
  return Math.sqrt(sum)
}

export const generateRestaurantEmbedding = async (restaurant: any): Promise<number[]> => {
  try {
    const response = await fetch('/api/embeddings/restaurant', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(restaurant)
    })
    
    if (!response.ok) {
      throw new Error('Failed to generate restaurant embedding')
    }
    
    const result = await response.json()
    return result.embedding
  } catch (error) {
    console.error('Error generating restaurant embedding:', error)
    throw error
  }
}

export const generateUserEmbedding = async (userProfile: any): Promise<number[]> => {
  try {
    const response = await fetch('/api/embeddings/user', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(userProfile)
    })
    
    if (!response.ok) {
      throw new Error('Failed to generate user embedding')
    }
    
    const result = await response.json()
    return result.embedding
  } catch (error) {
    console.error('Error generating user embedding:', error)
    throw error
  }
}

export const generateQueryEmbedding = async (query: string): Promise<number[]> => {
  try {
    const response = await fetch('/api/embeddings/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query })
    })
    
    if (!response.ok) {
      throw new Error('Failed to generate query embedding')
    }
    
    const result = await response.json()
    return result.embedding
  } catch (error) {
    console.error('Error generating query embedding:', error)
    throw error
  }
}

// Selectors
export const useRestaurantEmbeddings = () => {
  const embeddings = useVectorDatabase(state => state.embeddings)
  return Object.values(embeddings).filter(emb => emb.type === 'restaurant')
}

export const useUserEmbeddings = () => {
  const embeddings = useVectorDatabase(state => state.embeddings)
  return Object.values(embeddings).filter(emb => emb.type === 'user')
}

export const useEmbeddingById = (id: string) => {
  const embeddings = useVectorDatabase(state => state.embeddings)
  return embeddings[id]
}
