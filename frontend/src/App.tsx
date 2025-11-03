/**
 * Main application component
 */

import { useChat } from '@/hooks/useChat';
import { ChatContainer } from '@/components/Chat/ChatContainer';
import { AlertCircle, Database, Activity } from 'lucide-react';
import { useEffect, useState } from 'react';
import { checkHealth } from '@/services/api';
import { HealthStatus } from '@/types';

function App() {
  const { messages, isLoading, error, sendMessage, clearMessages } = useChat();
  const [healthStatus, setHealthStatus] = useState<HealthStatus | null>(null);
  const [healthError, setHealthError] = useState<string | null>(null);

  // Check health on mount
  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const status = await checkHealth();
        setHealthStatus(status);
      } catch (err) {
        setHealthError('Unable to connect to backend');
      }
    };

    fetchHealth();
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 shadow-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-slate-900">
                PANARAY Feature Assistant
              </h1>
              <p className="text-sm text-slate-600 mt-1">
                RAG-powered assistant for product features
              </p>
            </div>
            
            {/* Status indicator */}
            <div className="flex items-center gap-2">
              {healthStatus ? (
                <>
                  <Activity className="h-4 w-4 text-green-500" />
                  <span className="text-sm text-slate-600">
                    {healthStatus.services.indexed_documents} docs indexed
                  </span>
                </>
              ) : healthError ? (
                <>
                  <AlertCircle className="h-4 w-4 text-red-500" />
                  <span className="text-sm text-red-600">{healthError}</span>
                </>
              ) : (
                <>
                  <Database className="h-4 w-4 text-slate-400 animate-pulse" />
                  <span className="text-sm text-slate-500">Connecting...</span>
                </>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="container mx-auto px-4 py-6">
        <div className="max-w-6xl mx-auto h-[calc(100vh-180px)]">
          {/* Error banner */}
          {error && (
            <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-2">
              <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-red-900">Error</p>
                <p className="text-sm text-red-700">{error}</p>
              </div>
            </div>
          )}

          {/* Chat container */}
          <ChatContainer
            messages={messages}
            onSendMessage={sendMessage}
            onClearMessages={clearMessages}
            isLoading={isLoading}
          />
        </div>
      </main>

      {/* Footer */}
      <footer className="fixed bottom-0 left-0 right-0 bg-white border-t border-slate-200 py-2">
        <div className="container mx-auto px-4">
          <p className="text-xs text-center text-slate-500">
            Powered by FastAPI, Pinecone, Llama 3, and Sentence Transformers
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
