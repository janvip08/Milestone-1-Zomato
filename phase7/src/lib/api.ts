// API Configuration for Phase 7 Frontend
// Connects to Phase 4 Backend API

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface RecommendationRequest {
  location: string;
  budget: number;
  rating: number;
  cuisine?: string[];
  dietary?: string[];
}

export interface Restaurant {
  id: string;
  name: string;
  cuisine: string;
  rating: number;
  costForTwo: number;
  location: string;
  specialties: string[];
  aiMatchScore: number;
  recommendationReason: string;
}

export interface RecommendationResponse {
  recommendations: Restaurant[];
  totalResults: number;
  processingTime: number;
  strategy: string;
}

class ApiClient {
  private baseUrl: string;

  constructor() {
    this.baseUrl = API_BASE_URL;
  }

  // Health check
  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    const response = await fetch(`${this.baseUrl}/health`);
    if (!response.ok) {
      throw new Error('Backend health check failed');
    }
    return response.json();
  }

  // Get restaurant recommendations
  async getRecommendations(request: RecommendationRequest): Promise<RecommendationResponse> {
    const response = await fetch(`${this.baseUrl}/recommend`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`Failed to get recommendations: ${response.statusText}`);
    }

    return response.json();
  }

  // Get available cuisines
  async getCuisines(): Promise<string[]> {
    const response = await fetch(`${this.baseUrl}/cuisines`);
    if (!response.ok) {
      throw new Error('Failed to get cuisines');
    }
    return response.json();
  }

  // Get restaurant details
  async getRestaurantDetails(id: string): Promise<Restaurant> {
    const response = await fetch(`${this.baseUrl}/restaurants/${id}`);
    if (!response.ok) {
      throw new Error('Failed to get restaurant details');
    }
    return response.json();
  }

  // User preferences (if implemented)
  async savePreferences(preferences: RecommendationRequest): Promise<{ success: boolean }> {
    const response = await fetch(`${this.baseUrl}/preferences`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(preferences),
    });

    if (!response.ok) {
      throw new Error('Failed to save preferences');
    }

    return response.json();
  }
}

// Export singleton instance
export const apiClient = new ApiClient();
