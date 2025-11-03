/**
 * Main chat container component
 */

import { useEffect, useRef } from 'react';
import { Message } from '@/types';
import { ChatMessage } from './ChatMessage';
import { ChatInput } from './ChatInput';
import { ScrollArea } from '@/components/UI/ScrollArea';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/UI/Card';
import { Button } from '@/components/UI/Button';
import { MessageSquare, Trash2 } from 'lucide-react';

interface ChatContainerProps {
  messages: Message[];
  onSendMessage: (content: string) => void;
  onClearMessages: () => void;
  isLoading: boolean;
}

export function ChatContainer({
  messages,
  onSendMessage,
  onClearMessages,
  isLoading,
}: ChatContainerProps) {
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (scrollAreaRef.current) {
      const scrollElement = scrollAreaRef.current.querySelector('[data-radix-scroll-area-viewport]');
      if (scrollElement) {
        scrollElement.scrollTop = scrollElement.scrollHeight;
      }
    }
  }, [messages]);

  return (
    <Card className="flex flex-col h-full">
      {/* Header */}
      <CardHeader className="flex-shrink-0 border-b">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <MessageSquare className="h-6 w-6 text-blue-600" />
            <CardTitle>PANARAY Feature Assistant</CardTitle>
          </div>
          {messages.length > 0 && (
            <Button
              variant="ghost"
              size="sm"
              onClick={onClearMessages}
              className="text-slate-600"
            >
              <Trash2 className="h-4 w-4 mr-2" />
              Clear
            </Button>
          )}
        </div>
      </CardHeader>

      {/* Messages */}
      <CardContent className="flex-1 overflow-hidden p-0">
        <ScrollArea ref={scrollAreaRef} className="h-full p-4">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center p-8">
              <MessageSquare className="h-16 w-16 text-slate-300 mb-4" />
              <h3 className="text-lg font-semibold text-slate-700 mb-2">
                Welcome to PANARAY Feature Assistant
              </h3>
              <p className="text-slate-500 max-w-md">
                Ask me anything about PANARAY Datagraph features. I'll answer based on the product documentation.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {messages.map((message) => (
                <ChatMessage key={message.id} message={message} />
              ))}
            </div>
          )}
        </ScrollArea>
      </CardContent>

      {/* Input */}
      <div className="flex-shrink-0 p-4 border-t bg-slate-50">
        <ChatInput
          onSend={onSendMessage}
          isLoading={isLoading}
          disabled={isLoading}
        />
      </div>
    </Card>
  );
}
