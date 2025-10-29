/**
 * Type definitions for the application
 */

export interface EmotionResult {
  emotion: string;
  confidence: number;
}

export interface QueryResponse {
  answer: string;
  emotion: EmotionResult;
  sources_used: number;
  confidence: number;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  emotion?: EmotionResult;
  sourcesUsed?: number;
  confidence?: number;
  timestamp: Date;
}

export interface HealthStatus {
  status: string;
  services: Record<string, string>;
}

export interface IndexStatus {
  indexed_count: number;
  status: string;
}
