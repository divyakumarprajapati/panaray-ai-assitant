/**
 * Type definitions for the application
 */

export interface QueryResponse {
  answer: string;
  sources_used: number;
  confidence: number;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
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
