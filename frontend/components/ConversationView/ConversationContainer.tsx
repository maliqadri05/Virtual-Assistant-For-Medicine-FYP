'use client';

import React, { useState, useEffect, useRef } from 'react';
import { MessageBubble, Message } from './MessageBubble';
import { InputField } from './InputField';
import { ConversationHistory, ConversationItem } from './ConversationHistory';
import { conversationAPI } from '@/services/api';

interface ConversationContainerProps {
  initialConversationId?: string;
  showSidebar?: boolean;
}

export function ConversationContainer({
  initialConversationId,
  showSidebar = true,
}: ConversationContainerProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [conversations, setConversations] = useState<ConversationItem[]>([]);
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(
    initialConversationId || null
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom on new messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Load conversation history
  useEffect(() => {
    const loadConversations = async () => {
      try {
        const data: any = await conversationAPI.list();
        setConversations(
          Array.isArray(data)
            ? data.map((conv: any) => ({
                id: conv.id || '',
                title: conv.title || 'Untitled Chat',
                lastMessage: conv.lastMessage || 'No messages',
                timestamp: new Date(conv.timestamp || Date.now()),
                messageCount: conv.messageCount || 0,
              }))
            : []
        );
      } catch (err) {
        console.error('Failed to load conversations:', err);
      }
    };

    loadConversations();
  }, []);

  // Load current conversation messages
  useEffect(() => {
    if (!currentConversationId) return;

    const loadConversation = async () => {
      try {
        setLoading(true);
        const data: any = await conversationAPI.get(currentConversationId);
        const loadedMessages: Message[] = Array.isArray(data?.messages)
          ? data.messages.map((msg: any) => ({
              id: msg.id || '',
              role: msg.role || 'assistant',
              content: msg.content || '',
              timestamp: new Date(msg.timestamp || Date.now()),
            }))
          : [];
        setMessages(loadedMessages);
        setError(null);
      } catch (err) {
        setError('Failed to load conversation');
        console.error('Failed to load conversation:', err);
      } finally {
        setLoading(false);
      }
    };

    loadConversation();
  }, [currentConversationId]);

  // Handle send message
  const handleSendMessage = async (content: string) => {
    if (!content.trim()) return;

    try {
      setError(null);

      // Add user message to UI immediately
      const userMessage: Message = {
        id: Date.now().toString(),
        role: 'user',
        content,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, userMessage]);

      // Add loading assistant message
      const loadingMessage: Message = {
        id: 'loading',
        role: 'assistant',
        content: '',
        timestamp: new Date(),
        loading: true,
      };
      setMessages((prev) => [...prev, loadingMessage]);
      setLoading(true);

      // Send to API
      let convId = currentConversationId;
      if (!convId) {
        // Create new conversation if needed
        const conv: any = await conversationAPI.create({});
        convId = conv?.id || '';
        setCurrentConversationId(convId);
      }

      const response: any = await conversationAPI.addMessage(convId || '', content);

      // Replace loading message with actual response
      setMessages((prev) => {
        const updatedMessages = [...prev];
        const lastIdx = updatedMessages.length - 1;
        if (lastIdx >= 0 && updatedMessages[lastIdx].id === 'loading') {
          updatedMessages[lastIdx] = {
            id: response?.id || 'msg-' + Date.now(),
            role: 'assistant',
            content: response?.content || 'No response',
            timestamp: new Date(response?.timestamp || Date.now()),
          };
        }
        return updatedMessages;
      });
    } catch (err) {
      setError('Failed to send message. Please try again.');
      console.error('Failed to send message:', err);
      // Remove loading message on error
      setMessages((prev) => prev.filter((msg) => msg.id !== 'loading'));
    } finally {
      setLoading(false);
    }
  };

  // Handle conversation selection
  const handleSelectConversation = (id: string) => {
    setCurrentConversationId(id);
  };

  // Handle delete conversation
  const handleDeleteConversation = async (id: string) => {
    try {
      // Call delete API if available
      // await conversationAPI.delete(id);
      setConversations((prev) => prev.filter((conv) => conv.id !== id));
      if (currentConversationId === id) {
        setCurrentConversationId(null);
        setMessages([]);
      }
    } catch (err) {
      console.error('Failed to delete conversation:', err);
    }
  };

  return (
    <div className="flex h-screen bg-white">
      {/* Sidebar */}
     
{showSidebar && (
        <ConversationHistory
          conversations={conversations}
          currentId={currentConversationId || undefined}
          onSelect={handleSelectConversation}
          onDelete={handleDeleteConversation}
        />
      )}

      {/* Main conversation area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="bg-medical-primary text-white p-4 shadow-sm">
          <div className="max-w-6xl mx-auto">
            <h1 className="text-2xl font-bold">Medical Consultation</h1>
            <p className="text-sm text-blue-100">Powered by MedGemma AI</p>
          </div>
        </div>

        {/* Messages area */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 && !loading && (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <div className="text-6xl mb-4">🏥</div>
              <h2 className="text-2xl font-bold text-slate-700 mb-2">
                Welcome to MedAI Assistant
              </h2>
              <p className="text-slate-500 max-w-md">
                Describe your symptoms or ask medical questions. I'll provide
                professional assessments and generate detailed reports for you to
                share with your doctor.
              </p>
              <div className="mt-8 p-4 bg-yellow-50 border-l-4 border-yellow-400 rounded max-w-md">
                <p className="text-sm text-yellow-800">
                  <strong>⚠️ Disclaimer:</strong> This is an AI assistant and not
                  a substitute for professional medical advice.
                </p>
              </div>
            </div>
          )}

          {/* Display messages */}
          {messages.map((msg) => (
            <MessageBubble key={msg.id} message={msg} />
          ))}

          {/* Error message */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
              <strong>Error:</strong> {error}
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input area */}
        <InputField
          onSubmit={handleSendMessage}
          disabled={loading}
          placeholder="Describe your symptoms or ask a medical question..."
        />
      </div>
    </div>
  );
}
