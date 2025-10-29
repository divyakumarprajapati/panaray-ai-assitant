/**
 * API service for communicating with the backend
 * Follows Single Responsibility Principle
 */

import { QueryResponse, HealthStatus, IndexStatus } from '@/types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

class ApiError extends Error {
  constructor(message: string, public status?: number) {
    super(message);
    this.name = 'ApiError';
  }
}

/**
 * Make a request to the API
 */
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  try {
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new ApiError(
        errorData.detail || `Request failed with status ${response.status}`,
        response.status
      );
    }

    return await response.json();
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError('Network error or server unavailable');
  }
}

/**
 * Query the assistant with a question
 */
export async function queryAssistant(query: string): Promise<QueryResponse> {
  return apiRequest<QueryResponse>('/query', {
    method: 'POST',
    body: JSON.stringify({ query }),
  });
}

/**
 * Check the health status of the API
 */
export async function checkHealth(): Promise<HealthStatus> {
  return apiRequest<HealthStatus>('/health');
}

/**
 * Index or reindex data
 */
export async function indexData(forceReindex: boolean = false): Promise<IndexStatus> {
  return apiRequest<IndexStatus>('/index', {
    method: 'POST',
    body: JSON.stringify({ force_reindex: forceReindex }),
  });
}

export { ApiError };
