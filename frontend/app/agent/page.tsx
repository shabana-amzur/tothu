'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function AgentTestPage() {
  const [message, setMessage] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [useAgent, setUseAgent] = useState(true);
  const router = useRouter();

  const sendMessage = async () => {
    if (!message.trim()) return;

    setLoading(true);
    setResponse('');

    try {
      const token = localStorage.getItem('token');
      
      if (!token) {
        router.push('/login');
        return;
      }

      const res = await fetch('http://localhost:8001/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          message: message,
          use_agent: useAgent,
        }),
      });

      if (!res.ok) {
        if (res.status === 401) {
          router.push('/login');
          return;
        }
        throw new Error('Failed to send message');
      }

      const data = await res.json();
      setResponse(data.message);
    } catch (error) {
      console.error('Error:', error);
      setResponse('Error: Failed to get response');
    } finally {
      setLoading(false);
    }
  };

  const examples = [
    { label: 'Math: 45 + 67', value: 'What is 45 + 67?', needsAgent: true },
    { label: 'Math: 100 - 37', value: 'Calculate 100 - 37', needsAgent: true },
    { label: 'Text: Reverse "Hello"', value: 'Reverse the word "Hello"', needsAgent: true },
    { label: 'Text: Count words', value: 'How many words are in "Hello World from LangChain"', needsAgent: true },
    { label: 'General: What is AI?', value: 'What is artificial intelligence?', needsAgent: false },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 p-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-2xl shadow-xl p-8 mb-6">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            🤖 Agent Test Page
          </h1>
          <p className="text-gray-600">
            Test the LangChain Agent with tools (Calculator & Text Utilities)
          </p>
        </div>

        {/* Mode Toggle */}
        <div className="bg-white rounded-2xl shadow-xl p-6 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-gray-800">Mode</h3>
              <p className="text-sm text-gray-600">
                {useAgent ? '🤖 Agent mode: Uses tools for math & text' : '💬 Chat mode: Direct LLM response'}
              </p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={useAgent}
                onChange={(e) => setUseAgent(e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-14 h-7 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-6 after:w-6 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>
        </div>

        {/* Examples */}
        <div className="bg-white rounded-2xl shadow-xl p-6 mb-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">📋 Example Queries</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {examples.map((example, idx) => (
              <button
                key={idx}
                onClick={() => {
                  setMessage(example.value);
                  setUseAgent(example.needsAgent);
                }}
                className="p-3 text-left bg-gradient-to-r from-purple-50 to-blue-50 hover:from-purple-100 hover:to-blue-100 rounded-lg transition-all border border-purple-200"
              >
                <div className="text-sm font-medium text-gray-700">{example.label}</div>
                <div className="text-xs text-gray-500 mt-1">
                  {example.needsAgent ? '🤖 Requires Agent' : '💬 Direct Chat'}
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Input Section */}
        <div className="bg-white rounded-2xl shadow-xl p-6 mb-6">
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            Your Message
          </label>
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Ask a question or request a calculation..."
            className="w-full p-4 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all resize-none"
            rows={3}
          />
          <button
            onClick={sendMessage}
            disabled={loading || !message.trim()}
            className="mt-4 w-full bg-gradient-to-r from-purple-600 to-blue-600 text-white font-semibold py-3 px-6 rounded-xl hover:from-purple-700 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg"
          >
            {loading ? '🔄 Processing...' : useAgent ? '🤖 Send to Agent' : '💬 Send Message'}
          </button>
        </div>

        {/* Response Section */}
        {(response || loading) && (
          <div className="bg-white rounded-2xl shadow-xl p-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">
              {loading ? '⏳ Agent Thinking...' : '✅ Response'}
            </h3>
            {loading ? (
              <div className="flex items-center justify-center py-8">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
              </div>
            ) : (
              <div className="bg-gradient-to-r from-purple-50 to-blue-50 p-6 rounded-xl border-2 border-purple-200">
                <p className="text-gray-800 whitespace-pre-wrap">{response}</p>
              </div>
            )}
          </div>
        )}

        {/* Info Section */}
        <div className="mt-6 bg-blue-50 rounded-2xl p-6 border-2 border-blue-200">
          <h3 className="text-lg font-semibold text-blue-800 mb-3">ℹ️ How it works</h3>
          <div className="space-y-2 text-sm text-blue-900">
            <p><strong>Agent Mode (🤖):</strong> The AI analyzes your request, decides if it needs tools, uses calculator or text utilities, and returns the result.</p>
            <p><strong>Chat Mode (💬):</strong> Standard AI chat without tool access - the LLM responds directly.</p>
            <p className="mt-4 pt-4 border-t border-blue-300">
              <strong>Available Tools:</strong>
            </p>
            <ul className="list-disc list-inside space-y-1 ml-2">
              <li><strong>Calculator:</strong> Addition and subtraction (e.g., "5+3", "100-45")</li>
              <li><strong>Text Utility:</strong> Reverse text or count words</li>
            </ul>
          </div>
        </div>

        {/* Back Button */}
        <button
          onClick={() => router.push('/')}
          className="mt-6 w-full bg-gray-100 hover:bg-gray-200 text-gray-700 font-semibold py-3 px-6 rounded-xl transition-all"
        >
          ← Back to Chat
        </button>
      </div>
    </div>
  );
}
