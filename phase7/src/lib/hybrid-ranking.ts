import { create } from 'zustand'

export interface RankingStrategy {
  id: string
  name: string
  type: 'rule-based' | 'vector-based' | 'llm-based' | 'hybrid'
  weight: number
  enabled: boolean
  config: Record<string, any>
}

export interface RankingResult {
  restaurantId: string
  score: number
  strategy: string
  explanation: string
  metadata: Record<string, any>
}

export interface HybridRankingConfig {
  strategies: RankingStrategy[]
  fusionMethod: 'weighted-average' | 'rank-fusion' | 'reciprocal-rank-fusion'
  fallbackStrategy: string
  minStrategies: number
  maxResults: number
}

interface HybridRankingStore {
  config: HybridRankingConfig
  results: RankingResult[]
  isLoading: boolean
  error: string | null
  
  // Actions
  updateConfig: (config: Partial<HybridRankingConfig>) => void
  addStrategy: (strategy: RankingStrategy) => void
  removeStrategy: (strategyId: string) => void
  enableStrategy: (strategyId: string) => void
  disableStrategy: (strategyId: string) => void
  updateStrategyWeight: (strategyId: string, weight: number) => void
  rankRestaurants: (preferences: any, candidates: any[]) => Promise<RankingResult[]>
  getStrategyResults: (strategyId: string, preferences: any, candidates: any[]) => Promise<RankingResult[]>
}

export const useHybridRanking = create<HybridRankingStore>((set, get) => ({
  config: {
    strategies: [
      {
        id: 'rule-based',
        name: 'Rule-based Ranking',
        type: 'rule-based',
        weight: 0.3,
        enabled: true,
        config: {
          factors: ['rating', 'price', 'distance', 'popularity'],
          weights: { rating: 0.4, price: 0.3, distance: 0.2, popularity: 0.1 }
        }
      },
      {
        id: 'vector-based',
        name: 'Vector Similarity',
        type: 'vector-based',
        weight: 0.4,
        enabled: true,
        config: {
          similarityThreshold: 0.7,
          embeddingType: 'restaurant',
          distanceMetric: 'cosine'
        }
      },
      {
        id: 'llm-based',
        name: 'LLM Reasoning',
        type: 'llm-based',
        weight: 0.3,
        enabled: true,
        config: {
          model: 'llama3-8b-8192',
          promptTemplate: 'rank-restaurants',
          temperature: 0.7
        }
      }
    ],
    fusionMethod: 'weighted-average',
    fallbackStrategy: 'rule-based',
    minStrategies: 2,
    maxResults: 10
  },
  results: [],
  isLoading: false,
  error: null,

  updateConfig: (configUpdates) => {
    set(state => ({
      config: { ...state.config, ...configUpdates }
    }))
  },

  addStrategy: (strategy) => {
    set(state => ({
      config: {
        ...state.config,
        strategies: [...state.config.strategies, strategy]
      }
    }))
  },

  removeStrategy: (strategyId) => {
    set(state => ({
      config: {
        ...state.config,
        strategies: state.config.strategies.filter(s => s.id !== strategyId)
      }
    }))
  },

  enableStrategy: (strategyId) => {
    set(state => ({
      config: {
        ...state.config,
        strategies: state.config.strategies.map(s => 
          s.id === strategyId ? { ...s, enabled: true } : s
        )
      }
    }))
  },

  disableStrategy: (strategyId) => {
    set(state => ({
      config: {
        ...state.config,
        strategies: state.config.strategies.map(s => 
          s.id === strategyId ? { ...s, enabled: false } : s
        )
      }
    }))
  },

  updateStrategyWeight: (strategyId, weight) => {
    set(state => ({
      config: {
        ...state.config,
        strategies: state.config.strategies.map(s => 
          s.id === strategyId ? { ...s, weight } : s
        )
      }
    }))
  },

  rankRestaurants: async (preferences, candidates) => {
    set({ isLoading: true, error: null })
    
    try {
      const enabledStrategies = get().config.strategies.filter(s => s.enabled)
      
      if (enabledStrategies.length < get().config.minStrategies) {
        throw new Error(`At least ${get().config.minStrategies} strategies must be enabled`)
      }
      
      const strategyResults: Record<string, RankingResult[]> = {}
      
      // Execute each enabled strategy
      for (const strategy of enabledStrategies) {
        try {
          const results = await get().getStrategyResults(strategy.id, preferences, candidates)
          strategyResults[strategy.id] = results
        } catch (error) {
          console.error(`Strategy ${strategy.id} failed:`, error)
          // Use fallback strategy if available
          if (strategy.id !== get().config.fallbackStrategy) {
            try {
              const fallbackResults = await get().getStrategyResults(
                get().config.fallbackStrategy, 
                preferences, 
                candidates
              )
              strategyResults[strategy.id] = fallbackResults
            } catch (fallbackError) {
              console.error(`Fallback strategy failed:`, fallbackError)
              // Create empty results to avoid breaking fusion
              strategyResults[strategy.id] = []
            }
          }
        }
      }
      
      // Fuse results using configured method
      const fusedResults = get().fuseResults(strategyResults)
      
      set({
        results: fusedResults,
        isLoading: false
      })
      
      return fusedResults
    } catch (error) {
      set({
        isLoading: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      })
      throw error
    }
  },

  getStrategyResults: async (strategyId, preferences, candidates) => {
    const strategy = get().config.strategies.find(s => s.id === strategyId)
    if (!strategy) {
      throw new Error(`Strategy ${strategyId} not found`)
    }
    
    switch (strategy.type) {
      case 'rule-based':
        return get().executeRuleBasedRanking(strategy, preferences, candidates)
      case 'vector-based':
        return get().executeVectorBasedRanking(strategy, preferences, candidates)
      case 'llm-based':
        return get().executeLLMBasedRanking(strategy, preferences, candidates)
      default:
        throw new Error(`Unknown strategy type: ${strategy.type}`)
    }
  },

  executeRuleBasedRanking: async (strategy, preferences, candidates) => {
    const config = strategy.config
    const results: RankingResult[] = []
    
    for (const candidate of candidates) {
      let score = 0
      const factors = config.factors
      const weights = config.weights
      
      // Rating factor
      if (factors.includes('rating') && candidate.rating) {
        score += (candidate.rating / 5) * weights.rating
      }
      
      // Price factor
      if (factors.includes('price') && candidate.costForTwo) {
        const priceScore = Math.max(0, 1 - (candidate.costForTwo - preferences.maxCostForTwo) / preferences.maxCostForTwo)
        score += priceScore * weights.price
      }
      
      // Distance factor
      if (factors.includes('distance') && candidate.distance) {
        const distanceScore = Math.max(0, 1 - candidate.distance / 10) // 10km max
        score += distanceScore * weights.distance
      }
      
      // Popularity factor
      if (factors.includes('popularity') && candidate.popularity) {
        score += Math.min(1, candidate.popularity / 1000) * weights.popularity
      }
      
      results.push({
        restaurantId: candidate.id,
        score,
        strategy: strategy.id,
        explanation: `Score: ${score.toFixed(2)} based on ${factors.join(', ')}`,
        metadata: {
          factors,
          weights,
          individualScores: {
            rating: candidate.rating ? (candidate.rating / 5) * weights.rating : 0,
            price: candidate.costForTwo ? Math.max(0, 1 - (candidate.costForTwo - preferences.maxCostForTwo) / preferences.maxCostForTwo) * weights.price : 0,
            distance: candidate.distance ? Math.max(0, 1 - candidate.distance / 10) * weights.distance : 0,
            popularity: candidate.popularity ? Math.min(1, candidate.popularity / 1000) * weights.popularity : 0
          }
        }
      })
    }
    
    return results.sort((a, b) => b.score - a.score).slice(0, get().config.maxResults)
  },

  executeVectorBasedRanking: async (strategy, preferences, candidates) => {
    const config = strategy.config
    const results: RankingResult[] = []
    
    try {
      // Generate query embedding
      const queryEmbedding = await generateQueryEmbedding(
        `${preferences.cuisine} ${preferences.location} ${preferences.occasion || ''}`
      )
      
      // Search for similar restaurants
      const searchResults = await searchSimilarRestaurants(
        queryEmbedding,
        candidates.map(c => c.id),
        config.similarityThreshold
      )
      
      for (const result of searchResults) {
        results.push({
          restaurantId: result.id,
          score: result.similarity,
          strategy: strategy.id,
          explanation: `Vector similarity: ${result.similarity.toFixed(3)}`,
          metadata: {
            similarity: result.similarity,
            distance: result.distance,
            embeddingType: config.embeddingType
          }
        })
      }
      
      return results.slice(0, get().config.maxResults)
    } catch (error) {
      console.error('Vector-based ranking failed:', error)
      throw error
    }
  },

  executeLLMBasedRanking: async (strategy, preferences, candidates) => {
    const config = strategy.config
    const results: RankingResult[] = []
    
    try {
      // Prepare prompt for LLM
      const prompt = prepareLLMPrompt(preferences, candidates, config.promptTemplate)
      
      // Call LLM API
      const llmResponse = await callLLMAPI(prompt, config)
      
      // Parse LLM response
      const rankings = parseLLMResponse(llmResponse)
      
      for (const ranking of rankings) {
        results.push({
          restaurantId: ranking.restaurantId,
          score: ranking.score,
          strategy: strategy.id,
          explanation: ranking.explanation,
          metadata: {
            model: config.model,
            temperature: config.temperature,
            promptTemplate: config.promptTemplate,
            llmResponse: llmResponse
          }
        })
      }
      
      return results.slice(0, get().config.maxResults)
    } catch (error) {
      console.error('LLM-based ranking failed:', error)
      throw error
    }
  },

  fuseResults: (strategyResults: Record<string, RankingResult[]>) => {
    const fusionMethod = get().config.fusionMethod
    const enabledStrategies = Object.keys(strategyResults)
    
    if (enabledStrategies.length === 0) {
      return []
    }
    
    switch (fusionMethod) {
      case 'weighted-average':
        return get().weightedAverageFusion(strategyResults)
      case 'rank-fusion':
        return get().rankFusion(strategyResults)
      case 'reciprocal-rank-fusion':
        return get().reciprocalRankFusion(strategyResults)
      default:
        return get().weightedAverageFusion(strategyResults)
    }
  },

  weightedAverageFusion: (strategyResults: Record<string, RankingResult[]>) => {
    const config = get().config
    const restaurantScores: Record<string, { totalScore: number, count: number, explanations: string[] }> = {}
    
    // Collect scores from all strategies
    for (const [strategyId, results] of Object.entries(strategyResults)) {
      const strategy = config.strategies.find(s => s.id === strategyId)
      const weight = strategy?.weight || 0
      
      for (const result of results) {
        if (!restaurantScores[result.restaurantId]) {
          restaurantScores[result.restaurantId] = { totalScore: 0, count: 0, explanations: [] }
        }
        
        restaurantScores[result.restaurantId].totalScore += result.score * weight
        restaurantScores[result.restaurantId].count += 1
        restaurantScores[result.restaurantId].explanations.push(result.explanation)
      }
    }
    
    // Calculate average scores
    const fusedResults: RankingResult[] = []
    for (const [restaurantId, scoreData] of Object.entries(restaurantScores)) {
      const averageScore = scoreData.totalScore / scoreData.count
      fusedResults.push({
        restaurantId,
        score: averageScore,
        strategy: 'hybrid',
        explanation: scoreData.explanations.join('; '),
        metadata: {
          individualScores: strategyResults,
          averageScore,
          strategyCount: scoreData.count
        }
      })
    }
    
    return fusedResults.sort((a, b) => b.score - a.score).slice(0, config.maxResults)
  },

  rankFusion: (strategyResults: Record<string, RankingResult[]>) => {
    const config = get().config
    const restaurantRanks: Record<string, { totalRank: number, count: number, explanations: string[] }> = {}
    
    // Collect ranks from all strategies
    for (const [strategyId, results] of Object.entries(strategyResults)) {
      const strategy = config.strategies.find(s => s.id === strategyId)
      const weight = strategy?.weight || 0
      
      for (let i = 0; i < results.length; i++) {
        const result = results[i]
        if (!restaurantRanks[result.restaurantId]) {
          restaurantRanks[result.restaurantId] = { totalRank: 0, count: 0, explanations: [] }
        }
        
        restaurantRanks[result.restaurantId].totalRank += (i + 1) * weight
        restaurantRanks[result.restaurantId].count += 1
        restaurantRanks[result.restaurantId].explanations.push(result.explanation)
      }
    }
    
    // Calculate average ranks
    const fusedResults: RankingResult[] = []
    for (const [restaurantId, rankData] of Object.entries(restaurantRanks)) {
      const averageRank = rankData.totalRank / rankData.count
      const score = 1 / averageRank // Convert rank to score
      
      fusedResults.push({
        restaurantId,
        score,
        strategy: 'hybrid',
        explanation: rankData.explanations.join('; '),
        metadata: {
          individualRanks: strategyResults,
          averageRank,
          score,
          strategyCount: rankData.count
        }
      })
    }
    
    return fusedResults.sort((a, b) => b.score - a.score).slice(0, config.maxResults)
  },

  reciprocalRankFusion: (strategyResults: Record<string, RankingResult[]>) => {
    const config = get().config
    const k = 60 // Reciprocal rank fusion parameter
    const restaurantScores: Record<string, { totalScore: number, count: number, explanations: string[] }> = {}
    
    // Collect reciprocal scores from all strategies
    for (const [strategyId, results] of Object.entries(strategyResults)) {
      const strategy = config.strategies.find(s => s.id === strategyId)
      const weight = strategy?.weight || 0
      
      for (let i = 0; i < results.length; i++) {
        const result = results[i]
        const reciprocalScore = 1 / (k + i + 1)
        
        if (!restaurantScores[result.restaurantId]) {
          restaurantScores[result.restaurantId] = { totalScore: 0, count: 0, explanations: [] }
        }
        
        restaurantScores[result.restaurantId].totalScore += reciprocalScore * weight
        restaurantScores[result.restaurantId].count += 1
        restaurantScores[result.restaurantId].explanations.push(result.explanation)
      }
    }
    
    // Calculate total reciprocal scores
    const fusedResults: RankingResult[] = []
    for (const [restaurantId, scoreData] of Object.entries(restaurantScores)) {
      fusedResults.push({
        restaurantId,
        score: scoreData.totalScore,
        strategy: 'hybrid',
        explanation: scoreData.explanations.join('; '),
        metadata: {
          individualScores: strategyResults,
          reciprocalScore: scoreData.totalScore,
          strategyCount: scoreData.count,
          k
        }
      })
    }
    
    return fusedResults.sort((a, b) => b.score - a.score).slice(0, config.maxResults)
  }
}))

// Utility functions
async function generateQueryEmbedding(query: string): Promise<number[]> {
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

async function searchSimilarRestaurants(
  queryEmbedding: number[],
  restaurantIds: string[],
  threshold: number
): Promise<any[]> {
  try {
    const response = await fetch('/api/vector-database/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query: queryEmbedding,
        type: 'restaurant',
        limit: 50,
        threshold
      })
    })
    
    if (!response.ok) {
      throw new Error('Failed to search restaurants')
    }
    
    const results = await response.json()
    return results.filter(r => restaurantIds.includes(r.id))
  } catch (error) {
    console.error('Error searching restaurants:', error)
    throw error
  }
}

function prepareLLMPrompt(preferences: any, candidates: any[], template: string): string {
  const candidatesText = candidates.map((c, i) => 
    `${i + 1}. ${c.name} - Rating: ${c.rating}, Price: ${c.costForTwo}, Cuisine: ${c.cuisine}`
  ).join('\n')
  
  return `Please rank the following restaurants based on user preferences:
  
  User Preferences:
  - Location: ${preferences.location}
  - Cuisine: ${preferences.cuisine}
  - Max Price: ${preferences.maxCostForTwo}
  - Occasion: ${preferences.occasion || 'Not specified'}
  
  Restaurants:
  ${candidatesText}
  
  Please rank them from best to worst and provide a score (0-1) and explanation for each.`
}

async function callLLMAPI(prompt: string, config: any): Promise<string> {
  try {
    const response = await fetch('/api/llm/rank', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        prompt,
        model: config.model,
        temperature: config.temperature
      })
    })
    
    if (!response.ok) {
      throw new Error('Failed to call LLM API')
    }
    
    const result = await response.json()
    return result.response
  } catch (error) {
    console.error('Error calling LLM API:', error)
    throw error
  }
}

function parseLLMResponse(response: string): any[] {
  try {
    // Try to parse as JSON first
    if (response.trim().startsWith('[')) {
      return JSON.parse(response)
    }
    
    // Fallback: parse text response
    const lines = response.split('\n').filter(line => line.trim())
    const results = []
    
    for (const line of lines) {
      const match = line.match(/^(\d+)\.\s+(.+?)\s*-\s*Score:\s*([\d.]+)\s*-\s*(.+)$/)
      if (match) {
        results.push({
          restaurantId: match[1], // This would need to be mapped to actual restaurant ID
          score: parseFloat(match[2]),
          explanation: match[3]
        })
      }
    }
    
    return results
  } catch (error) {
    console.error('Error parsing LLM response:', error)
    return []
  }
}

// Selectors
export const useEnabledStrategies = () => {
  const config = useHybridRanking(state => state.config)
  return config.strategies.filter(s => s.enabled)
}

export const useStrategyConfig = (strategyId: string) => {
  const config = useHybridRanking(state => state.config)
  return config.strategies.find(s => s.id === strategyId)
}

export const useRankingResults = () => {
  return useHybridRanking(state => state.results)
}
