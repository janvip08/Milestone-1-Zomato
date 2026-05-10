import { create } from 'zustand'

export interface Experiment {
  id: string
  name: string
  description: string
  type: 'prompt' | 'ranking' | 'ui' | 'feature'
  status: 'draft' | 'active' | 'paused' | 'completed'
  variants: ExperimentVariant[]
  trafficSplit: Record<string, number>
  startDate: string
  endDate?: string
  targetMetrics: string[]
  successCriteria: {
    metric: string
    operator: 'greater_than' | 'less_than' | 'equals'
    threshold: number
    statisticalSignificance: number // p-value threshold
  }[]
  createdAt: string
  updatedAt: string
}

export interface ExperimentVariant {
  id: string
  name: string
  config: Record<string, any>
  weight: number
  isEnabled: boolean
}

export interface ExperimentResult {
  experimentId: string
  variantId: string
  userId?: string
  sessionId: string
  timestamp: string
  metrics: Record<string, number>
  metadata: Record<string, any>
}

export interface ABTestingConfig {
  enabled: boolean
  defaultTrafficSplit: 'equal' | 'weighted'
  statisticalSignificanceLevel: number // 0.05 for 95% confidence
  minSampleSize: number
  maxRunningExperiments: number
  cookieConsentRequired: boolean
  dataRetentionDays: number
}

interface ABTestingStore {
  experiments: Record<string, Experiment>
  userAssignments: Record<string, string> // userId -> variantId
  results: ExperimentResult[]
  config: ABTestingConfig
  isLoading: boolean
  error: string | null
  
  // Actions
  createExperiment: (experiment: Omit<Experiment, 'id' | 'createdAt' | 'updatedAt'>) => Promise<Experiment>
  updateExperiment: (id: string, updates: Partial<Experiment>) => Promise<void>
  deleteExperiment: (id: string) => Promise<void>
  getExperiment: (id: string) => Promise<Experiment | null>
  getActiveExperiments: () => Experiment[]
  assignUserToVariant: (experimentId: string, userId: string) => string | null
  trackExperimentResult: (result: Omit<ExperimentResult, 'id'>) => Promise<void>
  getExperimentResults: (experimentId: string, startDate?: string, endDate?: string) => Promise<ExperimentResult[]>
  analyzeExperiment: (experimentId: string) => Promise<{
    winner: string | null
    confidence: number
    statisticalSignificance: boolean
    metrics: Record<string, any>
  }>
  updateConfig: (config: Partial<ABTestingConfig>) => void
}

export const useABTestingStore = create<ABTestingStore>((set, get) => ({
  experiments: {},
  userAssignments: {},
  results: [],
  config: {
    enabled: true,
    defaultTrafficSplit: 'equal',
    statisticalSignificanceLevel: 0.05,
    minSampleSize: 1000,
    maxRunningExperiments: 10,
    cookieConsentRequired: true,
    dataRetentionDays: 90
  },
  isLoading: false,
  error: null,

  createExperiment: async (experimentData) => {
    set({ isLoading: true, error: null })
    
    try {
      const experiment: Experiment = {
        ...experimentData,
        id: `exp_${Date.now()}`,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      }
      
      const response = await fetch('/api/experiments', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(experiment)
      })
      
      if (!response.ok) {
        throw new Error('Failed to create experiment')
      }
      
      const savedExperiment: Experiment = await response.json()
      
      set(state => ({
        experiments: { ...state.experiments, [savedExperiment.id]: savedExperiment },
        isLoading: false
      }))
      
      return savedExperiment
    } catch (error) {
      set({ isLoading: false, error: error instanceof Error ? error.message : 'Unknown error' })
      throw error
    }
  },

  updateExperiment: async (id, updates) => {
    set({ isLoading: true, error: null })
    
    try {
      const response = await fetch(`/api/experiments/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...updates, updatedAt: new Date().toISOString() })
      })
      
      if (!response.ok) {
        throw new Error('Failed to update experiment')
      }
      
      const updatedExperiment: Experiment = await response.json()
      
      set(state => ({
        experiments: { ...state.experiments, [id]: updatedExperiment },
        isLoading: false
      }))
    } catch (error) {
      set({ isLoading: false, error: error instanceof Error ? error.message : 'Unknown error' })
      throw error
    }
  },

  deleteExperiment: async (id) => {
    set({ isLoading: true, error: null })
    
    try {
      const response = await fetch(`/api/experiments/${id}`, {
        method: 'DELETE'
      })
      
      if (!response.ok) {
        throw new Error('Failed to delete experiment')
      }
      
      const experiments = get().experiments
      delete experiments[id]
      
      set(state => ({
        experiments,
        isLoading: false
      }))
    } catch (error) {
      set({ isLoading: false, error: error instanceof Error ? error.message : 'Unknown error' })
      throw error
    }
  },

  getExperiment: async (id) => {
    const cached = get().experiments[id]
    if (cached) {
      return cached
    }
    
    try {
      const response = await fetch(`/api/experiments/${id}`)
      
      if (!response.ok) {
        throw new Error('Failed to get experiment')
      }
      
      const experiment: Experiment = await response.json()
      
      set(state => ({
        experiments: { ...state.experiments, [id]: experiment }
      }))
      
      return experiment
    } catch (error) {
      console.error('Error getting experiment:', error)
      return null
    }
  },

  getActiveExperiments: () => {
    const experiments = Object.values(get().experiments)
    return experiments.filter(exp => exp.status === 'active')
  },

  assignUserToVariant: (experimentId, userId) => {
    const experiment = get().experiments[experimentId]
    if (!experiment || experiment.status !== 'active') {
      return null
    }
    
    // Check if user is already assigned
    const existingAssignment = get().userAssignments[userId]
    if (existingAssignment) {
      return existingAssignment
    }
    
    // Assign variant based on traffic split
    const variantId = get().selectVariant(experimentId)
    
    // Store assignment
    const assignments = get().userAssignments
    assignments[userId] = variantId
    
    set(state => ({
      userAssignments: assignments
    }))
    
    return variantId
  },

  selectVariant: (experimentId) => {
    const experiment = get().experiments[experimentId]
    if (!experiment) {
      return null
    }
    
    const trafficSplit = experiment.trafficSplit
    const totalWeight = Object.values(trafficSplit).reduce((sum, weight) => sum + weight, 0)
    
    // Generate random number between 0 and totalWeight
    const random = Math.random() * totalWeight
    let cumulativeWeight = 0
    
    for (const [variantId, weight] of Object.entries(trafficSplit)) {
      cumulativeWeight += weight
      if (random <= cumulativeWeight) {
        return variantId
      }
    }
    
    // Fallback to first variant
    return Object.keys(trafficSplit)[0]
  },

  trackExperimentResult: async (resultData) => {
    const result: ExperimentResult = {
      ...resultData,
      id: `result_${Date.now()}`,
      timestamp: new Date().toISOString()
    }
    
    try {
      const response = await fetch('/api/experiment-results', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(result)
      })
      
      if (!response.ok) {
        throw new Error('Failed to track experiment result')
      }
      
      const savedResult: ExperimentResult = await response.json()
      
      set(state => ({
        results: [...state.results, savedResult]
      }))
    } catch (error) {
      console.error('Error tracking experiment result:', error)
      throw error
    }
  },

  getExperimentResults: async (experimentId, startDate, endDate) => {
    try {
      const params = new URLSearchParams()
      params.append('experimentId', experimentId)
      if (startDate) params.append('startDate', startDate)
      if (endDate) params.append('endDate', endDate)
      
      const response = await fetch(`/api/experiment-results?${params}`)
      
      if (!response.ok) {
        throw new Error('Failed to get experiment results')
      }
      
      const results: ExperimentResult[] = await response.json()
      return results
    } catch (error) {
      console.error('Error getting experiment results:', error)
      return []
    }
  },

  analyzeExperiment: async (experimentId) => {
    const experiment = get().experiments[experimentId]
    if (!experiment) {
      throw new Error(`Experiment ${experimentId} not found`)
    }
    
    const results = await get().getExperimentResults(experimentId)
    
    if (results.length < get().config.minSampleSize) {
      return {
        winner: null,
        confidence: 0,
        statisticalSignificance: false,
        metrics: {}
      }
    }
    
    // Group results by variant
    const variantResults: Record<string, ExperimentResult[]> = {}
    for (const result of results) {
      if (!variantResults[result.variantId]) {
        variantResults[result.variantId] = []
      }
      variantResults[result.variantId].push(result)
    }
    
    // Calculate metrics for each variant
    const variantMetrics: Record<string, Record<string, number>> = {}
    for (const [variantId, variantData] of Object.entries(variantResults)) {
      variantMetrics[variantId] = {}
      
      for (const metric of experiment.targetMetrics) {
        const values = variantData.map(r => r.metrics[metric] || 0)
        variantMetrics[variantId][metric] = {
          mean: values.reduce((sum, val) => sum + val, 0) / values.length,
          median: values.sort((a, b) => a - b)[Math.floor(values.length / 2)],
          min: Math.min(...values),
          max: Math.max(...values),
          count: values.length
        }
      }
    }
    
    // Determine winner for each metric
    const winners: Record<string, string> = {}
    for (const metric of experiment.targetMetrics) {
      let bestVariant = ''
      let bestValue = -Infinity
      
      for (const [variantId, metrics] of Object.entries(variantMetrics)) {
        const value = metrics[metric].mean
        if (value > bestValue) {
          bestValue = value
          bestVariant = variantId
        }
      }
      
      winners[metric] = bestVariant
    }
    
    // Calculate statistical significance (simplified chi-square test)
    const significance = get().calculateStatisticalSignificance(variantResults)
    
    return {
      winner: winners[experiment.targetMetrics[0]] || null,
      confidence: significance.confidence,
      statisticalSignificance: significance.isSignificant,
      metrics: variantMetrics
    }
  },

  calculateStatisticalSignificance: (variantResults: Record<string, ExperimentResult[]>) => {
    const variants = Object.keys(variantResults)
    if (variants.length !== 2) {
      return { confidence: 0, isSignificant: false }
    }
    
    const [variantA, variantB] = variants
    const resultsA = variantResults[variantA]
    const resultsB = variantResults[variantB]
    
    // Simplified chi-square test for conversion rates
    const conversionsA = resultsA.filter(r => r.metrics.conversion === 1).length
    const conversionsB = resultsB.filter(r => r.metrics.conversion === 1).length
    
    const totalA = resultsA.length
    const totalB = resultsB.length
    const totalConversions = conversionsA + conversionsB
    
    if (totalConversions === 0) {
      return { confidence: 0, isSignificant: false }
    }
    
    // Expected conversions under null hypothesis (equal performance)
    const expectedConversionsA = totalA * totalConversions / (totalA + totalB)
    const expectedConversionsB = totalB * totalConversions / (totalA + totalB)
    
    // Chi-square statistic
    const chiSquare = 
      Math.pow(conversionsA - expectedConversionsA, 2) / expectedConversionsA +
      Math.pow(conversionsB - expectedConversionsB, 2) / expectedConversionsB
    
    // Degrees of freedom = 1
    const pValue = 1 - get().chiSquareCDF(chiSquare, 1)
    
    return {
      confidence: 1 - pValue,
      isSignificant: pValue < get().config.statisticalSignificanceLevel
    }
  },

  chiSquareCDF: (x, df) => {
    // Simplified chi-square CDF approximation
    if (x <= 0) return 0
    if (df === 1) {
      return get().normalCDF(Math.sqrt(x) - Math.sqrt(df + 0.5))
    }
    // For other degrees of freedom, would use more complex approximation
    return get().normalCDF(Math.sqrt(2 * x) - Math.sqrt(2 * df - 1))
  },

  normalCDF: (x) => {
    // Standard normal CDF approximation
    return 0.5 * (1 + get().erf(x / Math.sqrt(2)))
  },

  erf: (x) => {
    // Error function approximation
    const a1 = 0.254829592
    const a2 = -0.284496736
    const a3 = 1.421413741
    const a4 = -1.453152027
    const a5 = 1.061405429
    
    const p = 0.3275911
    const sign = x >= 0 ? 1 : -1
    x = Math.abs(x) / Math.sqrt(2)
    
    const t = 1.0 / (1.0 + p * x)
    const t2 = t * t
    const t3 = t2 * t
    const t4 = t3 * t
    const t5 = t4 * t
    
    const y = 1 - (((((a5 * t5 + a4 * t4) + a3 * t3) + a2 * t2 + a1 * t) * t) * Math.exp(-x * x))
    
    return sign * y
  },

  updateConfig: (configUpdates) => {
    set(state => ({
      config: { ...state.config, ...configUpdates }
    }))
  }
}))

// Selectors
export const useActiveExperiments = () => {
  const experiments = useABTestingStore(state => state.experiments)
  return Object.values(experiments).filter(exp => exp.status === 'active')
}

export const useExperimentById = (id: string) => {
  const experiments = useABTestingStore(state => state.experiments)
  return experiments[id]
}

export const useUserVariant = (experimentId: string, userId: string) => {
  const userAssignments = useABTestingStore(state => state.userAssignments)
  return userAssignments[userId]
}

export const useExperimentResults = (experimentId: string) => {
  const results = useABTestingStore(state => state.results)
  return results.filter(result => result.experimentId === experimentId)
}

// Utility functions for common experiment types
export const createPromptExperiment = (
  name: string,
  description: string,
  promptA: string,
  promptB: string,
  trafficSplit: Record<string, number> = { 'prompt_a': 50, 'prompt_b': 50 }
) => {
  return {
    name,
    description,
    type: 'prompt' as const,
    variants: [
      {
        id: 'prompt_a',
        name: 'Prompt A',
        config: { prompt: promptA },
        weight: trafficSplit['prompt_a'],
        isEnabled: true
      },
      {
        id: 'prompt_b',
        name: 'Prompt B',
        config: { prompt: promptB },
        weight: trafficSplit['prompt_b'],
        isEnabled: true
      }
    ],
    trafficSplit,
    targetMetrics: ['conversion_rate', 'user_satisfaction', 'response_time'],
    successCriteria: [
      {
        metric: 'conversion_rate',
        operator: 'greater_than',
        threshold: 0.05, // 5% improvement
        statisticalSignificance: 0.05
      }
    ],
    status: 'draft' as const
  }
}

export const createRankingExperiment = (
  name: string,
  description: string,
  strategyA: string,
  strategyB: string,
  trafficSplit: Record<string, number> = { 'strategy_a': 50, 'strategy_b': 50 }
) => {
  return {
    name,
    description,
    type: 'ranking' as const,
    variants: [
      {
        id: 'strategy_a',
        name: 'Strategy A',
        config: { strategy: strategyA },
        weight: trafficSplit['strategy_a'],
        isEnabled: true
      },
      {
        id: 'strategy_b',
        name: 'Strategy B',
        config: { strategy: strategyB },
        weight: trafficSplit['strategy_b'],
        isEnabled: true
      }
    ],
    trafficSplit,
    targetMetrics: ['click_through_rate', 'user_rating', 'recommendation_accepted'],
    successCriteria: [
      {
        metric: 'click_through_rate',
        operator: 'greater_than',
        threshold: 0.02, // 2% improvement
        statisticalSignificance: 0.05
      }
    ],
    status: 'draft' as const
  }
}

export const createUIExperiment = (
  name: string,
  description: string,
  layoutA: string,
  layoutB: string,
  trafficSplit: Record<string, number> = { 'layout_a': 50, 'layout_b': 50 }
) => {
  return {
    name,
    description,
    type: 'ui' as const,
    variants: [
      {
        id: 'layout_a',
        name: 'Layout A',
        config: { layout: layoutA },
        weight: trafficSplit['layout_a'],
        isEnabled: true
      },
      {
        id: 'layout_b',
        name: 'Layout B',
        config: { layout: layoutB },
        weight: trafficSplit['layout_b'],
        isEnabled: true
      }
    ],
    trafficSplit,
    targetMetrics: ['user_engagement', 'time_on_page', 'conversion_rate'],
    successCriteria: [
      {
        metric: 'user_engagement',
        operator: 'greater_than',
        threshold: 0.1, // 10% improvement
        statisticalSignificance: 0.05
      }
    ],
    status: 'draft' as const
  }
}
