'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '../contexts/AuthContext';

interface SQLResult {
  success: boolean;
  question: string;
  sql: string | null;
  data: Record<string, any>[] | null;
  row_count: number | null;
  columns: string[] | null;
  error: string | null;
  rows_affected?: number;
  query_type?: string;
  message?: string;
  is_write_operation?: boolean;
}

export default function NL2SQLPage() {
  const { user, token, logout, isLoading: authLoading } = useAuth();
  const router = useRouter();
  const [question, setQuestion] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<SQLResult | null>(null);
  const [schemaVisible, setSchemaVisible] = useState(false);
  const [schema, setSchema] = useState<string>('');
  const [showConfirmation, setShowConfirmation] = useState(false);
  const [pendingQuery, setPendingQuery] = useState<string>('');

  // Redirect to login if not authenticated
  if (!authLoading && !user) {
    router.push('/login');
    return null;
  }

  const fetchSchema = async () => {
    try {
      setIsLoading(true);
      const response = await fetch('http://localhost:8001/api/nl-to-sql/schema', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch schema');
      }

      const data = await response.json();
      setSchema(data.schema);
      setSchemaVisible(true);
    } catch (error) {
      console.error('Error fetching schema:', error);
      alert('Failed to fetch database schema');
    } finally {
      setIsLoading(false);
    }
  };

  const executeQuery = async (e: React.FormEvent, confirmed: boolean = false) => {
    e.preventDefault();
    
    if (!question.trim() || isLoading) return;

    setIsLoading(true);
    setResult(null);

    try {
      const response = await fetch('http://localhost:8001/api/nl-to-sql/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ 
          question: question.trim(),
          confirm: confirmed 
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        if (response.status === 401) {
          logout();
          throw new Error('Session expired');
        }
        throw new Error(errorData.detail || 'Failed to execute query');
      }

      const data = await response.json();
      setResult(data);
      
      // If it's a write operation requiring confirmation, show modal
      if (data.is_write_operation && !confirmed) {
        setShowConfirmation(true);
        setPendingQuery(question.trim());
      }
    } catch (error) {
      console.error('Error:', error);
      setResult({
        success: false,
        question: question,
        sql: null,
        data: null,
        row_count: null,
        columns: null,
        error: error instanceof Error ? error.message : 'Unknown error occurred',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const confirmExecution = async () => {
    setShowConfirmation(false);
    setQuestion(pendingQuery);
    
    // Create a synthetic event
    const syntheticEvent = { preventDefault: () => {} } as React.FormEvent;
    await executeQuery(syntheticEvent, true);
  };

  const cancelExecution = () => {
    setShowConfirmation(false);
    setPendingQuery('');
  };

  const exampleQuestions = [
    "How many users are in the database?",
    "Show all chat threads",
    "List users created today",
    "Count documents by file type",
    "Show the most recent chat messages",
    "Insert a test user with email demo@test.com",
    "Update user email where id = 1",
  ];

  if (authLoading || !user) {
    return (
      <div className="flex h-screen items-center justify-center bg-gray-900">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700 px-6 py-4 shadow-sm">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => router.push('/')}
              className="text-gray-400 hover:text-white transition-colors"
              title="Back to Chat"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
            </button>
            <div>
              <h1 className="text-xl font-bold text-white">Natural Language to SQL</h1>
              <p className="text-sm text-gray-400">Ask questions about your database in plain English</p>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <button
              onClick={fetchSchema}
              disabled={isLoading}
              className="text-sm bg-gray-700 hover:bg-gray-600 text-white px-4 py-2 rounded-lg transition-colors disabled:opacity-50"
            >
              {schemaVisible ? 'Hide Schema' : 'Show Schema'}
            </button>
            <span className="text-sm text-gray-300">{user.full_name || user.username}</span>
            <button 
              onClick={logout}
              className="text-sm text-red-400 hover:text-red-300 font-medium transition-colors"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Schema Panel */}
        {schemaVisible && schema && (
          <div className="mb-6 bg-gray-800 rounded-lg p-4 border border-gray-700">
            <div className="flex justify-between items-center mb-3">
              <h2 className="text-lg font-semibold text-white">Database Schema</h2>
              <button
                onClick={() => setSchemaVisible(false)}
                className="text-gray-400 hover:text-white"
              >
                ✕
              </button>
            </div>
            <pre className="text-sm text-gray-300 overflow-x-auto whitespace-pre-wrap">
              {schema}
            </pre>
          </div>
        )}

        {/* Query Input */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 mb-6">
          <form onSubmit={executeQuery}>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Ask a question about your database
            </label>
            <div className="flex space-x-3">
              <input
                type="text"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="e.g., How many users are registered?"
                disabled={isLoading}
                className="flex-1 rounded-lg border border-gray-600 bg-gray-700 text-white px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed placeholder-gray-400"
              />
              <button
                type="submit"
                disabled={isLoading || !question.trim()}
                className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? (
                  <span className="flex items-center space-x-2">
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    <span>Running...</span>
                  </span>
                ) : (
                  'Execute'
                )}
              </button>
            </div>
          </form>

          {/* Example Questions */}
          <div className="mt-4">
            <p className="text-sm text-gray-400 mb-2">Example questions:</p>
            <div className="flex flex-wrap gap-2">
              {exampleQuestions.map((example, idx) => (
                <button
                  key={idx}
                  onClick={() => setQuestion(example)}
                  disabled={isLoading}
                  className="text-xs bg-gray-700 hover:bg-gray-600 text-gray-300 px-3 py-1.5 rounded-full transition-colors disabled:opacity-50"
                >
                  {example}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Results */}
        {result && (
          <div className="space-y-4">
            {/* Generated SQL */}
            {result.sql && (
              <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-sm font-semibold text-gray-300">Generated SQL</h3>
                  <div className="flex items-center space-x-2">
                    {result.query_type && (
                      <span className={`text-xs px-2 py-1 rounded font-medium ${
                        result.query_type === 'SELECT' 
                          ? 'bg-blue-900/30 text-blue-400' 
                          : 'bg-orange-900/30 text-orange-400'
                      }`}>
                        {result.query_type}
                      </span>
                    )}
                    {result.success && (
                      <span className="text-xs bg-green-900/30 text-green-400 px-2 py-1 rounded">
                        ✓ Safe Query
                      </span>
                    )}
                  </div>
                </div>
                <pre className="bg-gray-900 rounded p-3 text-sm text-blue-300 overflow-x-auto">
                  {result.sql}
                </pre>
              </div>
            )}

            {/* Success Message for Write Operations */}
            {result.success && result.message && (
              <div className="bg-green-900/20 border border-green-800 rounded-lg p-4">
                <div className="flex items-start space-x-2">
                  <svg className="w-5 h-5 text-green-400 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  <div>
                    <h3 className="text-sm font-semibold text-green-400 mb-1">Success</h3>
                    <p className="text-sm text-green-300">{result.message}</p>
                    {result.rows_affected !== undefined && result.rows_affected > 0 && (
                      <p className="text-xs text-green-400 mt-1">
                        Rows affected: {result.rows_affected}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Error Message */}
            {!result.success && result.error && (
              <div className="bg-red-900/20 border border-red-800 rounded-lg p-4">
                <div className="flex items-start space-x-2">
                  <svg className="w-5 h-5 text-red-400 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                  <div>
                    <h3 className="text-sm font-semibold text-red-400 mb-1">Error</h3>
                    <p className="text-sm text-red-300">{result.error}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Data Results */}
            {result.success && result.data && result.data.length > 0 && (
              <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-sm font-semibold text-gray-300">
                    Results ({result.row_count} {result.row_count === 1 ? 'row' : 'rows'})
                  </h3>
                </div>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-700">
                    <thead className="bg-gray-900">
                      <tr>
                        {result.columns?.map((col, idx) => (
                          <th
                            key={idx}
                            className="px-4 py-2 text-left text-xs font-medium text-gray-400 uppercase tracking-wider"
                          >
                            {col}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className="bg-gray-800 divide-y divide-gray-700">
                      {result.data.map((row, rowIdx) => (
                        <tr key={rowIdx} className="hover:bg-gray-750">
                          {result.columns?.map((col, colIdx) => (
                            <td
                              key={colIdx}
                              className="px-4 py-2 text-sm text-gray-300 whitespace-nowrap"
                            >
                              {row[col] !== null && row[col] !== undefined
                                ? String(row[col])
                                : <span className="text-gray-500 italic">null</span>}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Empty Results */}
            {result.success && result.data && result.data.length === 0 && (
              <div className="bg-gray-800 rounded-lg p-8 border border-gray-700 text-center">
                <svg className="w-12 h-12 text-gray-600 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
                </svg>
                <p className="text-gray-400">No results found</p>
              </div>
            )}
          </div>
        )}

        {/* Info Panel */}
        {!result && (
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <h3 className="text-lg font-semibold text-white mb-3">How it works</h3>
            <div className="space-y-2 text-sm text-gray-300">
              <p>✓ Type your question in natural language</p>
              <p>✓ AI converts it to SQL automatically</p>
              <p>✓ Query is validated for security</p>
              <p>✓ Results are displayed in a table</p>
            </div>
            <div className="mt-4 p-3 bg-blue-900/20 border border-blue-800 rounded">
              <p className="text-xs text-blue-300">
                🔒 <strong>Security:</strong> SELECT, INSERT, UPDATE, DELETE allowed. Write operations require confirmation. Dangerous operations (DROP, ALTER, TRUNCATE) are blocked.
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Confirmation Modal */}
      {showConfirmation && result && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-gray-800 rounded-lg shadow-2xl max-w-2xl w-full border border-gray-700">
            <div className="p-6">
              <div className="flex items-start space-x-3 mb-4">
                <svg className="w-8 h-8 text-orange-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                <div className="flex-1">
                  <h3 className="text-xl font-bold text-white mb-1">Confirm {result.query_type} Operation</h3>
                  <p className="text-sm text-gray-300">
                    You are about to execute a write operation. Please review carefully before proceeding.
                  </p>
                </div>
              </div>

              <div className="bg-gray-900 rounded-lg p-4 mb-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-semibold text-gray-400 uppercase">Generated SQL</span>
                  <span className={`text-xs px-2 py-1 rounded font-medium bg-orange-900/30 text-orange-400`}>
                    {result.query_type}
                  </span>
                </div>
                <pre className="text-sm text-blue-300 overflow-x-auto whitespace-pre-wrap">
                  {result.sql}
                </pre>
              </div>

              <div className="bg-yellow-900/20 border border-yellow-800 rounded-lg p-3 mb-6">
                <p className="text-xs text-yellow-300">
                  ⚠️ <strong>Warning:</strong> This operation will modify your database. Make sure you understand what this query does before confirming.
                </p>
              </div>

              <div className="flex justify-end space-x-3">
                <button
                  onClick={cancelExecution}
                  className="px-6 py-2 text-sm font-medium text-gray-300 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={confirmExecution}
                  className="px-6 py-2 text-sm font-medium text-white bg-orange-600 hover:bg-orange-700 rounded-lg transition-colors"
                >
                  Confirm & Execute
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
