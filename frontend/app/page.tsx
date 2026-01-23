'use client';

import { useState, useRef, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useAuth } from './contexts/AuthContext';
import ThreadSidebar from './components/ThreadSidebar';
import MarkdownRenderer from './components/MarkdownRenderer';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
  image_url?: string;
  is_image?: boolean;
}

interface ThreadSidebarProps {
  onSelectThread: (threadId: number | null) => void;
  currentThreadId: number | null;
  refreshTrigger?: number;
}

export default function Home() {
  const { user, token, logout, isLoading: authLoading, loginWithToken } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentThreadId, setCurrentThreadId] = useState<number | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);
  const [isProcessingOAuth, setIsProcessingOAuth] = useState(false);
  
  // Message history navigation
  const [messageHistory, setMessageHistory] = useState<string[]>([]);
  const [historyIndex, setHistoryIndex] = useState(-1);
  const inputRef = useRef<HTMLInputElement>(null);
  const [refreshThreads, setRefreshThreads] = useState(0);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  
  // File upload state
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploadingFile, setIsUploadingFile] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [uploadedExcelId, setUploadedExcelId] = useState<number | null>(null);
  const [excelFileName, setExcelFileName] = useState<string>('');
  const abortControllerRef = useRef<AbortController | null>(null);
  
  // Image validation state
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [isValidatingImage, setIsValidatingImage] = useState(false);
  const [showImageValidation, setShowImageValidation] = useState(false);
  const [documentType, setDocumentType] = useState<string>('invoice');
  const [useDemoMode, setUseDemoMode] = useState(false);
  const imageInputRef = useRef<HTMLInputElement>(null);

  // Handle OAuth callback with token in URL
  useEffect(() => {
    const urlToken = searchParams.get('token');
    const urlEmail = searchParams.get('email');
    const urlUsername = searchParams.get('username');
    
    if (urlToken && urlEmail && urlUsername) {
      setIsProcessingOAuth(true);
      // Save token to localStorage via AuthContext
      loginWithToken(urlToken, { email: urlEmail, username: urlUsername })
        .then(() => {
          // Clean up URL after successful login
          window.history.replaceState({}, document.title, '/');
        })
        .finally(() => {
          setIsProcessingOAuth(false);
        });
    }
  }, [searchParams, loginWithToken]);

  // Load Excel context from localStorage on mount
  useEffect(() => {
    const savedExcelId = localStorage.getItem('uploadedExcelId');
    const savedExcelName = localStorage.getItem('excelFileName');
    if (savedExcelId && savedExcelName) {
      setUploadedExcelId(parseInt(savedExcelId));
      setExcelFileName(savedExcelName);
      console.log('Restored Excel context:', savedExcelId, savedExcelName);
    }
  }, []);

  useEffect(() => {
    // Don't redirect to login if we're processing OAuth or still loading
    if (!authLoading && !user && !isProcessingOAuth) {
      router.push('/login');
    }
  }, [user, authLoading, isProcessingOAuth, router]);

  const scrollToBottom = () => {
    if (messagesContainerRef.current) {
      messagesContainerRef.current.scrollTop = messagesContainerRef.current.scrollHeight;
    }
  };

  useEffect(() => {
    // Only auto-scroll for new messages, not when loading history
    if (!isLoadingHistory) {
      scrollToBottom();
    }
  }, [messages, isLoadingHistory]);

  // Additional scroll trigger for loading state changes
  useEffect(() => {
    if (isLoading) {
      scrollToBottom();
    }
  }, [isLoading]);

  // Load messages when thread is selected
  const loadThreadMessages = async (threadId: number) => {
    setIsLoadingHistory(true);
    try {
      const response = await fetch(`http://localhost:8001/api/threads/${threadId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to load thread messages');
      }

      const data = await response.json();
      
      console.log('Loaded thread data:', data); // Debug log
      
      // Convert thread messages to chat format
      const threadMessages: Message[] = [];
      data.messages.forEach((msg: any) => {
        threadMessages.push({
          role: 'user',
          content: msg.message,
          timestamp: msg.created_at,
        });
        threadMessages.push({
          role: 'assistant',
          content: msg.response,
          timestamp: msg.created_at,
        });
      });

      console.log('Converted messages:', threadMessages); // Debug log
      setMessages(threadMessages);
      setCurrentThreadId(threadId);
    } catch (error) {
      console.error('Error loading thread:', error);
      alert('Failed to load thread messages');
    } finally {
      // Reset flag after a brief delay to allow render
      setTimeout(() => setIsLoadingHistory(false), 100);
    }
  };

  const handleSelectThread = (threadId: number | null) => {
    if (threadId === null) {
      // New chat
      setMessages([]);
      setCurrentThreadId(null);
      setMessageHistory([]);
      setHistoryIndex(-1);
    } else {
      // Load existing thread
      loadThreadMessages(threadId);
      setMessageHistory([]);
      setHistoryIndex(-1);
    }
  };

  // Handle up/down arrow navigation
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'ArrowUp' || e.key === 'ArrowDown') {
      console.log('Arrow key pressed:', e.key, 'History length:', messageHistory.length, 'Current index:', historyIndex);
    }
    
    if (messageHistory.length === 0) return;

    if (e.key === 'ArrowUp') {
      e.preventDefault();
      const newIndex = historyIndex + 1;
      if (newIndex < messageHistory.length) {
        setHistoryIndex(newIndex);
        const msg = messageHistory[messageHistory.length - 1 - newIndex];
        console.log('Setting input to:', msg);
        setInput(msg);
      }
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      const newIndex = historyIndex - 1;
      if (newIndex >= 0) {
        setHistoryIndex(newIndex);
        const msg = messageHistory[messageHistory.length - 1 - newIndex];
        console.log('Setting input to:', msg);
        setInput(msg);
      } else if (newIndex === -1) {
        setHistoryIndex(-1);
        console.log('Clearing input');
        setInput('');
      }
    }
  };

  const sendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      role: 'user',
      content: input.trim(),
      timestamp: new Date().toISOString(),
    };

    // Add to message history for up/down arrow navigation
    setMessageHistory(prev => {
      const newHistory = [...prev, input.trim()];
      console.log('Message history updated:', newHistory);
      return newHistory;
    });
    setHistoryIndex(-1);

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    // Create new AbortController for this request
    abortControllerRef.current = new AbortController();

    try {
      // If Excel file is uploaded, route to Excel API
      if (uploadedExcelId) {
        const response = await fetch(`http://localhost:8001/api/excel/${uploadedExcelId}/ask`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({
            question: userMessage.content
          }),
          signal: abortControllerRef.current.signal,
        });

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          if (response.status === 401) {
            logout();
            throw new Error('Session expired');
          }
          throw new Error(errorData.detail || 'Failed to get response');
        }

        const data = await response.json();
        
        const assistantMessage: Message = {
          role: 'assistant',
          content: data.answer,
          timestamp: new Date().toISOString(),
        };

        setMessages(prev => [...prev, assistantMessage]);
        return;
      }
      
      // Regular chat
      const response = await fetch('http://localhost:8001/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          message: userMessage.content,
          thread_id: currentThreadId,
        }),
        signal: abortControllerRef.current.signal,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        if (response.status === 401) {
            logout();
            throw new Error('Session expired');
        }
        throw new Error(errorData.detail || 'Failed to get response');
      }

      const data = await response.json();
      
      const assistantMessage: Message = {
        role: 'assistant',
        content: data.message,
        timestamp: data.timestamp,
        image_url: data.image_url,
        is_image: data.is_image,
      };

      setMessages(prev => [...prev, assistantMessage]);
      
      // Always update thread ID from response (backend always returns it)
      if (data.thread_id) {
        if (currentThreadId !== data.thread_id) {
          console.log(`Setting thread ID to ${data.thread_id}`);
          setCurrentThreadId(data.thread_id);
          setRefreshThreads(prev => prev + 1);
        }
      }
    } catch (error) {
      console.error('Error:', error);
      // Don't show error message if request was aborted by user
      if (error instanceof Error && error.name === 'AbortError') {
        console.log('Request cancelled by user');
      } else {
        const errorMessage: Message = {
          role: 'assistant',
          content: `Error: ${error instanceof Error ? error.message : 'Unknown error occurred'}`,
          timestamp: new Date().toISOString(),
        };
        setMessages(prev => [...prev, errorMessage]);
      }
    } finally {
      setIsLoading(false);
      abortControllerRef.current = null;
    }
  };

  const stopGeneration = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
      setIsLoading(false);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const allowedTypes = [
        'application/pdf', 
        'text/plain', 
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', // .xlsx
        'application/vnd.ms-excel', // .xls
        'text/csv' // .csv
      ];
      const fileExt = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
      const allowedExts = ['.pdf', '.txt', '.docx', '.xlsx', '.xls', '.xlsm', '.csv'];
      
      if (!allowedTypes.includes(file.type) && !allowedExts.includes(fileExt)) {
        alert('Supported files: PDF, TXT, DOCX, XLSX, XLS, CSV (max 50MB)');
        return;
      }
      if (file.size > 50 * 1024 * 1024) {
        alert('File size must be less than 50MB');
        return;
      }
      setSelectedFile(file);
    }
  };

  const uploadFile = async () => {
    if (!selectedFile) return;
    
    setIsUploadingFile(true);
    
    try {
      // Check if it's an Excel file
      const fileExt = selectedFile.name.toLowerCase().substring(selectedFile.name.lastIndexOf('.'));
      const isExcelFile = ['.xlsx', '.xls', '.xlsm', '.csv'].includes(fileExt);
      
      if (isExcelFile) {
        // Upload Excel file
        const formData = new FormData();
        formData.append('file', selectedFile);

        const response = await fetch('http://localhost:8001/api/excel/upload', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`
          },
          body: formData,
        });

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(errorData.detail || 'Failed to upload Excel file');
        }

        const data = await response.json();
        setUploadedExcelId(data.id);
        setExcelFileName(selectedFile.name);
        // Persist to localStorage
        localStorage.setItem('uploadedExcelId', data.id.toString());
        localStorage.setItem('excelFileName', selectedFile.name);
        console.log('Excel file uploaded, ID:', data.id);

        const uploadMessage: Message = {
          role: 'assistant',
          content: `✅ **Document uploaded successfully!**\n\n**${selectedFile.name}** is being processed and will be available shortly.\n\nYou can now ask questions about this document. The AI will automatically use the document content to answer your questions.`,
          timestamp: new Date().toISOString(),
        };
        
        setMessages(prev => [...prev, uploadMessage]);
        setSelectedFile(null);
        if (fileInputRef.current) {
          fileInputRef.current.value = '';
        }
        return;
      }
      
      // Regular document upload
      // If no thread exists, create one first
      let threadId = currentThreadId;
      if (!threadId) {
        const createThreadResponse = await fetch('http://localhost:8001/api/threads/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({
            title: `Document: ${selectedFile.name}`
          }),
        });
        
        if (!createThreadResponse.ok) {
          throw new Error('Failed to create thread for document');
        }
        
        const threadData = await createThreadResponse.json();
        threadId = threadData.id;
        setCurrentThreadId(threadId);
        setRefreshThreads(prev => prev + 1);
        console.log(`Created new thread ${threadId} for document upload`);
      }
      
      const formData = new FormData();
      formData.append('file', selectedFile);
      
      // Add thread_id as a query parameter
      const url = new URL('http://localhost:8001/api/documents/upload');
      url.searchParams.append('thread_id', threadId.toString());

      const response = await fetch(url.toString(), {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to upload file');
      }

      const data = await response.json();

      const uploadMessage: Message = {
        role: 'assistant',
        content: `✅ **Document uploaded successfully!**\n\n**${selectedFile.name}** is being processed and will be available shortly.\n\nYou can now ask questions about this document. The AI will automatically use the document content to answer your questions.`,
        timestamp: new Date().toISOString(),
      };
      
      setMessages(prev => [...prev, uploadMessage]);
      setSelectedFile(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (error) {
      console.error('Upload error:', error);
      const errorMessage: Message = {
        role: 'assistant',
        content: `❌ Failed to upload file: ${error instanceof Error ? error.message : 'Unknown error'}`,
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsUploadingFile(false);
    }
  };

  const removeSelectedFile = () => {
    setSelectedFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  // Image validation functions
  const handleImageSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      // Check if it's an image
      if (file.type.startsWith('image/')) {
        setSelectedImage(file);
      } else {
        alert('Please select an image file (JPG, PNG, JPEG)');
      }
    }
  };

  const validateImage = async () => {
    if (!token) return;
    
    // Check if demo mode and no image selected
    if (useDemoMode) {
      return validateDemoMode();
    }
    
    if (!selectedImage) return;

    setIsValidatingImage(true);
    
    // Add user message showing the image
    const userMessage: Message = {
      role: 'user',
      content: `🖼️ Validating image: **${selectedImage.name}** (Type: ${documentType})`,
      timestamp: new Date().toISOString(),
    };
    setMessages(prev => [...prev, userMessage]);

    try {
      const formData = new FormData();
      formData.append('file', selectedImage);
      formData.append('document_type', documentType);

      const response = await fetch('http://localhost:8001/api/image-validation/validate', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to validate image');
      }

      const result = await response.json();
      
      // Format the validation result as a nice message
      let resultMessage = `## 📋 Image Validation Results\n\n`;
      resultMessage += `**Document Type:** ${documentType}\n`;
      resultMessage += `**Overall Status:** ${result.overall_status === 'VALID' ? '✅ VALID' : '❌ INVALID'}\n`;
      resultMessage += `**Confidence Score:** ${(result.confidence_score * 100).toFixed(1)}%\n\n`;
      
      resultMessage += `### Extracted Data:\n\`\`\`json\n${JSON.stringify(result.extracted_data, null, 2)}\n\`\`\`\n\n`;
      
      resultMessage += `### Validation Results:\n\n`;
      result.validation_results.forEach((vr: any) => {
        const icon = vr.status === 'PASS' ? '✅' : '❌';
        resultMessage += `${icon} **${vr.field}** (${vr.rule_type}): ${vr.status}`;
        if (vr.reason) {
          resultMessage += `\n   - _${vr.reason}_`;
        }
        resultMessage += '\n\n';
      });

      const assistantMessage: Message = {
        role: 'assistant',
        content: resultMessage,
        timestamp: new Date().toISOString(),
      };
      
      setMessages(prev => [...prev, assistantMessage]);
      setSelectedImage(null);
      setShowImageValidation(false);
      if (imageInputRef.current) {
        imageInputRef.current.value = '';
      }
    } catch (error) {
      console.error('Image validation error:', error);
      const errorMessage: Message = {
        role: 'assistant',
        content: `❌ Failed to validate image: ${error instanceof Error ? error.message : 'Unknown error'}`,
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsValidatingImage(false);
    }
  };

  const removeSelectedImage = () => {
    setSelectedImage(null);
    if (imageInputRef.current) {
      imageInputRef.current.value = '';
    }
  };

  const validateDemoMode = async () => {
    if (!token) return;

    setIsValidatingImage(true);
    
    // Add user message
    const userMessage: Message = {
      role: 'user',
      content: `🎭 Running demo validation (Type: ${documentType})`,
      timestamp: new Date().toISOString(),
    };
    setMessages(prev => [...prev, userMessage]);

    try {
      const formData = new FormData();
      formData.append('document_type', documentType);

      const response = await fetch('http://localhost:8001/api/image-validation/validate-demo', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to run demo validation');
      }

      const result = await response.json();
      
      // Format the validation result
      let resultMessage = `## 📋 Demo Validation Results\n\n`;
      resultMessage += `**Document Type:** ${documentType}\n`;
      resultMessage += `**Overall Status:** ${result.overall_status === 'VALID' ? '✅ VALID' : '❌ INVALID'}\n`;
      resultMessage += `**Confidence Score:** ${(result.confidence_score * 100).toFixed(1)}% (Demo)\n\n`;
      
      resultMessage += `### Extracted Data:\n\`\`\`json\n${JSON.stringify(result.extracted_data, null, 2)}\n\`\`\`\n\n`;
      
      resultMessage += `### Validation Results:\n\n`;
      result.validation_results.forEach((vr: any) => {
        const icon = vr.status === 'PASS' ? '✅' : '❌';
        resultMessage += `${icon} **${vr.field}** (${vr.rule_type}): ${vr.status}`;
        if (vr.reason) {
          resultMessage += `\n   - _${vr.reason}_`;
        }
        resultMessage += '\n\n';
      });

      const assistantMessage: Message = {
        role: 'assistant',
        content: resultMessage,
        timestamp: new Date().toISOString(),
      };
      
      setMessages(prev => [...prev, assistantMessage]);
      setShowImageValidation(false);
    } catch (error) {
      console.error('Demo validation error:', error);
      const errorMessage: Message = {
        role: 'assistant',
        content: `❌ Failed to run demo: ${error instanceof Error ? error.message : 'Unknown error'}`,
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsValidatingImage(false);
    }
  };

  if (authLoading || !user) {
    return (
      <div className="flex h-screen items-center justify-center bg-gray-900">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-gray-900 overflow-hidden">
      {/* Thread Sidebar */}
      <ThreadSidebar 
        onSelectThread={handleSelectThread}
        currentThreadId={currentThreadId}
        refreshTrigger={refreshThreads}
      />

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col min-h-0 overflow-hidden">
        {/* Header */}
        <header className="bg-gray-800 border-b border-gray-700 px-6 py-4 shadow-sm flex justify-between items-center flex-shrink-0">
          <div>
            <h1 className="text-xl font-bold text-white">AI Chat Assistant</h1>
            <p className="text-sm text-gray-400">Powered by Google Gemini</p>
          </div>
          <div className="flex items-center space-x-4">
            <button
              onClick={() => router.push('/sql')}
              className="flex items-center space-x-2 text-sm bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" />
              </svg>
              <span>SQL Query</span>
            </button>
            <button
              onClick={() => router.push('/excel')}
              className="flex items-center space-x-2 text-sm bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <span>Excel Analysis</span>
            </button>
            <span className="text-sm text-gray-300">
              {user.full_name || user.username}
            </span>
            <button 
              onClick={logout}
              className="text-sm text-red-400 hover:text-red-300 font-medium transition-colors"
            >
              Logout
            </button>
          </div>
        </header>

        {/* Messages Container */}
        <div ref={messagesContainerRef} className="flex-1 overflow-y-auto overflow-x-hidden px-4 py-4 scroll-smooth">
          <div className="max-w-4xl mx-auto space-y-4">
            {messages.length === 0 ? (
              <div className="text-center text-gray-400 mt-20">
                <h2 className="text-xl font-semibold mb-2 text-white">
                  Welcome {user.username}!
                </h2>
                <p>Start a conversation by typing a message below.</p>
                <div className="mt-8 text-sm text-gray-500">
                  <p className="mb-2">✨ Supports rich content:</p>
                  <ul className="space-y-1">
                    <li>📝 Markdown formatting</li>
                    <li>💻 Code with syntax highlighting</li>
                    <li>📊 Tables & Excel/CSV files</li>
                    <li>🔢 Mathematical formulas (LaTeX)</li>
                    <li>🖼️ Images and videos</li>
                    <li>📈 Google Sheets (paste URL)</li>
                  </ul>
                </div>
              </div>
            ) : (
              messages.map((message, index) => (
                <div
                  key={index}
                  className={`flex ${
                    message.role === 'user' ? 'justify-end' : 'justify-start'
                  }`}
                >
                  <div
                    className={`max-w-[85%] rounded-2xl px-5 py-3 overflow-hidden break-words ${
                      message.role === 'user'
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-800 text-gray-100 shadow-md border border-gray-700'
                    }`}
                  >
                    <div className="flex items-start space-x-2">
                      <div className="flex-1 min-w-0 overflow-hidden">
                        {message.role === 'assistant' ? (
                          <>
                            <MarkdownRenderer content={message.content} />
                            {message.is_image && message.image_url && (
                              <div className="mt-3">
                                <img 
                                  src={`http://localhost:8001${message.image_url}`}
                                  alt="Generated image"
                                  className="rounded-lg max-w-full h-auto shadow-lg"
                                  style={{ maxHeight: '512px' }}
                                />
                              </div>
                            )}
                          </>
                        ) : (
                          <p className="whitespace-pre-wrap break-words">
                            {message.content}
                          </p>
                        )}
                      </div>
                    </div>
                    {message.timestamp && (
                      <p
                        className={`text-xs mt-2 ${
                          message.role === 'user'
                            ? 'text-blue-200'
                            : 'text-gray-500'
                        }`}
                      >
                        {new Date(message.timestamp).toLocaleTimeString()}
                      </p>
                    )}
                  </div>
                </div>
              ))
            )}
            
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-gray-800 rounded-2xl px-5 py-3 shadow-md border border-gray-700">
                  <div className="flex items-center space-x-2">
                    <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
                    <span className="text-gray-300">Thinking...</span>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input Area */}
        <div className="border-t border-gray-700 bg-gray-800 px-4 py-4 shadow-lg flex-shrink-0">
          <form onSubmit={sendMessage} className="max-w-4xl mx-auto">
            {/* Excel file active indicator */}
            {uploadedExcelId && excelFileName && (
              <div className="mb-3 flex items-center justify-between bg-green-900 bg-opacity-30 border border-green-700 rounded-lg px-4 py-2">
                <div className="flex items-center space-x-2">
                  <svg className="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <span className="text-sm text-green-300">📊 Excel: {excelFileName}</span>
                  <span className="text-xs text-green-500">(Active - Ask questions about this data)</span>
                </div>
                <button
                  type="button"
                  onClick={() => {
                    setUploadedExcelId(null);
                    setExcelFileName('');
                    localStorage.removeItem('uploadedExcelId');
                    localStorage.removeItem('excelFileName');
                  }}
                  className="text-sm text-green-400 hover:text-white"
                  title="Clear Excel context"
                >
                  ✕
                </button>
              </div>
            )}
            
            {/* Selected file display */}
            {selectedFile && (
              <div className="mb-3 flex items-center justify-between bg-gray-700 rounded-lg px-4 py-2">
                <div className="flex items-center space-x-2">
                  <svg className="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                  </svg>
                  <span className="text-sm text-gray-300">{selectedFile.name}</span>
                  <span className="text-xs text-gray-500">({(selectedFile.size / 1024).toFixed(1)} KB)</span>
                </div>
                <div className="flex space-x-2">
                  <button
                    type="button"
                    onClick={uploadFile}
                    disabled={isUploadingFile}
                    className="text-sm bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded disabled:opacity-50"
                  >
                    {isUploadingFile ? 'Uploading...' : 'Upload'}
                  </button>
                  <button
                    type="button"
                    onClick={removeSelectedFile}
                    className="text-sm text-gray-400 hover:text-white"
                  >
                    ✕
                  </button>
                </div>
              </div>
            )}

            {/* Image validation section */}
            {showImageValidation && (
              <div className="mb-3 bg-purple-900 bg-opacity-30 border border-purple-700 rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-lg font-semibold text-purple-300">🖼️ Image Validation</h3>
                  <button
                    type="button"
                    onClick={() => {
                      setShowImageValidation(false);
                      setSelectedImage(null);
                      if (imageInputRef.current) imageInputRef.current.value = '';
                    }}
                    className="text-gray-400 hover:text-white"
                  >
                    ✕
                  </button>
                </div>
                
                <div className="space-y-3">
                  {/* Demo mode toggle */}
                  <div className="flex items-center justify-between bg-gray-700 rounded-lg px-4 py-2">
                    <div className="flex items-center space-x-2">
                      <span className="text-sm text-gray-300">🎭 Demo Mode</span>
                      <span className="text-xs text-gray-500">(No API required)</span>
                    </div>
                    <button
                      type="button"
                      onClick={() => setUseDemoMode(!useDemoMode)}
                      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                        useDemoMode ? 'bg-purple-600' : 'bg-gray-600'
                      }`}
                    >
                      <span
                        className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                          useDemoMode ? 'translate-x-6' : 'translate-x-1'
                        }`}
                      />
                    </button>
                  </div>

                  {/* Document type selector */}
                  <div>
                    <label className="block text-sm text-gray-300 mb-2">Document Type:</label>
                    <select
                      value={documentType}
                      onChange={(e) => setDocumentType(e.target.value)}
                      className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                    >
                      <option value="invoice">Invoice</option>
                      <option value="receipt">Receipt</option>
                      <option value="id_card">ID Card</option>
                    </select>
                  </div>

                  {/* Image file input - only show if not in demo mode */}
                  {!useDemoMode && (
                    <>
                      <input
                        ref={imageInputRef}
                        type="file"
                        accept="image/*"
                        onChange={handleImageSelect}
                        className="hidden"
                          />

                      {/* Selected image display or demo button */}
                      {selectedImage ? (
                        <div className="flex items-center justify-between bg-gray-700 rounded-lg px-4 py-2">
                          <div className="flex items-center space-x-2">
                            <svg className="w-5 h-5 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                            </svg>
                            <span className="text-sm text-gray-300">{selectedImage.name}</span>
                            <span className="text-xs text-gray-500">({(selectedImage.size / 1024).toFixed(1)} KB)</span>
                          </div>
                          <div className="flex space-x-2">
                            <button
                              type="button"
                              onClick={validateImage}
                              disabled={isValidatingImage}
                              className="text-sm bg-purple-600 hover:bg-purple-700 text-white px-3 py-1 rounded disabled:opacity-50"
                            >
                              {isValidatingImage ? 'Validating...' : 'Validate'}
                            </button>
                            <button
                              type="button"
                              onClick={removeSelectedImage}
                              className="text-sm text-gray-400 hover:text-white"
                            >
                              ✕
                            </button>
                          </div>
                        </div>
                      ) : (
                        <button
                          type="button"
                          onClick={() => imageInputRef.current?.click()}
                          className="w-full bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded transition-colors"
                        >
                          Choose Image File
                        </button>
                      )}
                    </>
                  )}

                  {/* Demo mode button */}
                  {useDemoMode && (
                    <button
                      type="button"
                      onClick={validateImage}
                      disabled={isValidatingImage}
                      className="w-full bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded transition-colors disabled:opacity-50"
                    >
                      {isValidatingImage ? 'Running Demo...' : '🎭 Run Demo Validation'}
                    </button>
                  )}
                </div>
              </div>
            )}
            
            <div className="flex space-x-3">
              {/* Hidden file input */}
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.txt,.docx"
                onChange={handleFileSelect}
                className="hidden"
              />
              
              {/* File upload button */}
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                disabled={isLoading || isUploadingFile}
                className="bg-gray-700 hover:bg-gray-600 text-white p-3 rounded-full transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                title="Upload PDF, TXT, or DOCX"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
                </svg>
              </button>

              {/* Image validation button */}
              <button
                type="button"
                onClick={() => setShowImageValidation(!showImageValidation)}
                disabled={isLoading || isValidatingImage}
                className={`${showImageValidation ? 'bg-purple-600' : 'bg-gray-700'} hover:bg-purple-600 text-white p-3 rounded-full transition-colors disabled:opacity-50 disabled:cursor-not-allowed`}
                title="Validate Image (Invoice, Receipt, ID)"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </button>
              
              <input
                ref={inputRef}
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Type your message... (Supports Markdown, ↑↓ for history)"
                disabled={isLoading}
                className="flex-1 rounded-full border border-gray-600 bg-gray-700 text-white px-6 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed placeholder-gray-400"
              />
              
              {/* Stop button - shown when loading, next to send button */}
              {isLoading && (
                <button
                  type="button"
                  onClick={stopGeneration}
                  className="bg-gray-700 hover:bg-gray-600 text-white p-3 rounded-full transition-colors"
                  title="Stop generation"
                >
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                    <rect x="6" y="6" width="12" height="12" rx="1" />
                  </svg>
                </button>
              )}
              
              {/* Send button - always visible but disabled when loading */}
              <button
                type="submit"
                disabled={isLoading || !input.trim()}
                className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-full font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-blue-600"
                title="Send message"
              >
                Send
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
