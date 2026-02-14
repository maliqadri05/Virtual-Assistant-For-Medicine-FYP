'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { conversationAPI } from '@/services/api';
import { LoadingSkeleton } from '@/components/Common/Loading';
import { ErrorAlert } from '@/components/Common/Error';

interface ConversationSummary {
  id: string;
  title: string;
  summary: string;
  messageCount: number;
  createdAt: Date;
  updatedAt: Date;
}

export default function DashboardPage() {
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadConversations();
  }, []);

  const loadConversations = async () => {
    try {
      setLoading(true);
      setError(null);
      const data: any = await conversationAPI.list();
      const conversations = Array.isArray(data)
        ? data.map((conv: any) => ({
            id: conv.id || '',
            title: conv.title || 'Untitled Conversation',
            summary: conv.summary || 'No summary available',
            messageCount: conv.messageCount || 0,
            createdAt: new Date(conv.createdAt || Date.now()),
            updatedAt: new Date(conv.updatedAt || Date.now()),
          }))
        : [];
      setConversations(conversations);
    } catch (err) {
      setError('Failed to load conversations. Please try again.');
      console.error('Failed to load conversations:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this conversation?')) return;

    try {
      // await conversationAPI.delete(id);
      setConversations((prev) => prev.filter((conv) => conv.id !== id));
    } catch (err) {
      setError('Failed to delete conversation');
      console.error('Failed to delete conversation:', err);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <div className="bg-medical-primary text-white">
        <div className="max-w-6xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold">Medical Consultation History</h1>
              <p className="text-blue-100 mt-2">
                View and manage your previous medical consultations
              </p>
            </div>
            <Link
              href="/chat/new"
              className="bg-white text-medical-primary hover:bg-blue-50 font-bold py-2 px-6 rounded-lg transition-colors"
            >
              + New Consultation
            </Link>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Error State */}
        {error && (
          <div className="mb-6">
            <ErrorAlert
              title="Error Loading Conversations"
              message={error}
              onRetry={loadConversations}
            />
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div>
            <LoadingSkeleton />
          </div>
        )}

        {/* Empty State */}
        {!loading && conversations.length === 0 && !error && (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">📋</div>
            <h2 className="text-2xl font-bold text-slate-900 mb-2">
              No Consultations Yet
            </h2>
            <p className="text-slate-600 max-w-md mx-auto">
              Start your first consultation to get AI-powered medical insights.
            </p>
            <Link
              href="/chat/new"
              className="inline-block mt-6 bg-medical-primary text-white font-medium py-2 px-6 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Start First Consultation
            </Link>
          </div>
        )}

        {/* Conversations Grid */}
        {!loading && conversations.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {conversations.map((conv) => (
              <div
                key={conv.id}
                className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow overflow-hidden border border-slate-100"
              >
                <div className="p-6">
                  <div className="flex justify-between items-start mb-3">
                    <h3 className="text-lg font-semibold text-slate-900 flex-1 line-clamp-2">
                      {conv.title}
                    </h3>
                    <button
                      onClick={() => handleDelete(conv.id)}
                      className="text-slate-400 hover:text-red-600 transition-colors ml-2"
                      title="Delete conversation"
                    >
                      ✕
                    </button>
                  </div>

                  <p className="text-sm text-slate-600 mb-4 line-clamp-3">
                    {conv.summary}
                  </p>

                  <div className="flex items-center justify-between text-xs text-slate-500 border-t border-slate-100 pt-3">
                    <span>💬 {conv.messageCount} messages</span>
                    <span>{conv.updatedAt.toLocaleDateString()}</span>
                  </div>

                  <Link
                    href={`/chat/${conv.id}`}
                    className="block mt-4 w-full text-center bg-medical-primary hover:bg-blue-700 text-white font-medium py-2 rounded transition-colors"
                  >
                    View Consultation
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
