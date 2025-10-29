/**
 * Individual chat message component
 */

import { Message } from '@/types';
import { cn, formatTimestamp, getEmotionEmoji, getEmotionColor } from '@/lib/utils';
import { User, Bot, Clock, TrendingUp } from 'lucide-react';

interface ChatMessageProps {
  message: Message;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user';

  return (
    <div
      className={cn(
        'flex gap-3 p-4 rounded-lg transition-all',
        isUser ? 'bg-slate-50 ml-8' : 'bg-blue-50 mr-8'
      )}
    >
      {/* Avatar */}
      <div
        className={cn(
          'flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center',
          isUser ? 'bg-slate-900 text-white' : 'bg-blue-600 text-white'
        )}
      >
        {isUser ? <User size={20} /> : <Bot size={20} />}
      </div>

      {/* Content */}
      <div className="flex-1 space-y-2">
        {/* Header */}
        <div className="flex items-center gap-2 text-xs text-slate-600">
          <span className="font-semibold">
            {isUser ? 'You' : 'Assistant'}
          </span>
          <Clock size={12} />
          <span>{formatTimestamp(message.timestamp)}</span>
        </div>

        {/* Message content */}
        <div className="text-slate-800 leading-relaxed whitespace-pre-wrap">
          {message.content}
        </div>

        {/* Metadata (only for assistant) */}
        {!isUser && message.emotion && (
          <div className="flex flex-wrap gap-3 pt-2 text-xs border-t border-slate-200">
            {/* Emotion */}
            <div className="flex items-center gap-1.5">
              <span className="text-slate-500">Emotion:</span>
              <span className={cn('font-medium', getEmotionColor(message.emotion.emotion))}>
                {getEmotionEmoji(message.emotion.emotion)} {message.emotion.emotion}
              </span>
              <span className="text-slate-400">
                ({Math.round(message.emotion.confidence * 100)}%)
              </span>
            </div>

            {/* Sources */}
            {message.sourcesUsed !== undefined && (
              <div className="flex items-center gap-1.5">
                <span className="text-slate-500">Sources:</span>
                <span className="font-medium text-slate-700">
                  {message.sourcesUsed}
                </span>
              </div>
            )}

            {/* Confidence */}
            {message.confidence !== undefined && (
              <div className="flex items-center gap-1.5">
                <TrendingUp size={12} className="text-slate-500" />
                <span className="text-slate-500">Confidence:</span>
                <span className="font-medium text-slate-700">
                  {Math.round(message.confidence * 100)}%
                </span>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
