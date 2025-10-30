import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Utility function to merge class names with tailwind-merge
 * This combines clsx for conditional classes and tailwind-merge for proper Tailwind CSS class merging
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * Format a timestamp into a readable time string
 */
export function formatTimestamp(timestamp: string | Date): string {
  const date = typeof timestamp === 'string' ? new Date(timestamp) : timestamp;
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  
  // Less than a minute
  if (diff < 60000) {
    return 'Just now';
  }
  
  // Less than an hour
  if (diff < 3600000) {
    const minutes = Math.floor(diff / 60000);
    return `${minutes}m ago`;
  }
  
  // Less than a day
  if (diff < 86400000) {
    const hours = Math.floor(diff / 3600000);
    return `${hours}h ago`;
  }
  
  // Otherwise, show time
  return date.toLocaleTimeString('en-US', { 
    hour: 'numeric', 
    minute: '2-digit',
    hour12: true 
  });
}

/**
 * Get emoji representation for an emotion
 */
export function getEmotionEmoji(emotion: string): string {
  const emojiMap: Record<string, string> = {
    joy: '😊',
    sadness: '😢',
    anger: '😠',
    fear: '😰',
    surprise: '😲',
    love: '❤️',
    neutral: '😐',
    admiration: '🤩',
    excitement: '🎉',
    gratitude: '🙏',
    optimism: '🌟',
    pride: '😌',
    amusement: '😄',
    approval: '👍',
    caring: '🤗',
    desire: '😍',
    relief: '😌',
    annoyance: '😒',
    confusion: '😕',
    curiosity: '🤔',
    disappointment: '😞',
    disapproval: '👎',
    disgust: '🤢',
    embarrassment: '😳',
    grief: '😭',
    nervousness: '😬',
    remorse: '😔',
  };
  
  return emojiMap[emotion.toLowerCase()] || '💬';
}

/**
 * Get Tailwind color class for an emotion
 */
export function getEmotionColor(emotion: string): string {
  const colorMap: Record<string, string> = {
    joy: 'text-yellow-600',
    sadness: 'text-blue-600',
    anger: 'text-red-600',
    fear: 'text-purple-600',
    surprise: 'text-orange-600',
    love: 'text-pink-600',
    neutral: 'text-gray-600',
    admiration: 'text-indigo-600',
    excitement: 'text-orange-500',
    gratitude: 'text-green-600',
    optimism: 'text-cyan-600',
    pride: 'text-violet-600',
    amusement: 'text-yellow-500',
    approval: 'text-green-500',
    caring: 'text-pink-500',
    desire: 'text-rose-600',
    relief: 'text-teal-600',
    annoyance: 'text-orange-700',
    confusion: 'text-slate-600',
    curiosity: 'text-blue-500',
    disappointment: 'text-gray-700',
    disapproval: 'text-red-700',
    disgust: 'text-green-800',
    embarrassment: 'text-pink-700',
    grief: 'text-indigo-800',
    nervousness: 'text-purple-500',
    remorse: 'text-slate-700',
  };
  
  return colorMap[emotion.toLowerCase()] || 'text-slate-600';
}
