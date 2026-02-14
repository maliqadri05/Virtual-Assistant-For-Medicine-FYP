'use client';

import React, { useState, useEffect, useMemo } from 'react';
import Link from 'next/link';
import { conversationAPI } from '@/services/api';
import { LoadingSkeleton } from '@/components/Common/Loading';
import { ErrorAlert } from '@/components/Common/Error';
import { ProtectedRoute } from '@/components/ProtectedRoute';

interface ConversationSummary {
  id: string;
  title: string;
  summary: string;
  messageCount: number;
  createdAt: Date;
  updatedAt: Date;
  category?: string;
  status?: 'completed' | 'in-progress' | 'pending';
  tags?: string[];
}

function DashboardContent() {
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState<'all' | 'completed' | 'in-progress'>('all');
  const [sortBy, setSortBy] = useState<'recent' | 'oldest' | 'messages'>('recent');
  const [itemsPerPage] = useState(12);
  const [currentPage, setCurrentPage] = useState(1);

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
            category: conv.category || 'General',
            status: conv.status || 'completed',
            tags: conv.tags || [],
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

  // Filter and search logic
  const filteredConversations = useMemo(() => {
    return conversations.filter((conv) => {
      const matchesSearch =
        conv.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        conv.summary.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (conv.tags?.some((tag) =>
          tag.toLowerCase().includes(searchTerm.toLowerCase())
        ) ?? false);

      const matchesFilter =
        filterStatus === 'all' || conv.status === filterStatus;

      return matchesSearch && matchesFilter;
    });
  }, [conversations, searchTerm, filterStatus]);

  // Sorting logic
  const sortedConversations = useMemo(() => {
    const sorted = [...filteredConversations];
    if (sortBy === 'recent') {
      sorted.sort((a, b) => b.updatedAt.getTime() - a.updatedAt.getTime());
    } else if (sortBy === 'oldest') {
      sorted.sort((a, b) => a.updatedAt.getTime() - b.updatedAt.getTime());
    } else if (sortBy === 'messages') {
      sorted.sort((a, b) => b.messageCount - a.messageCount);
    }
    return sorted;
  }, [filteredConversations, sortBy]);

  // Pagination logic
  const paginatedConversations = useMemo(() => {
    const startIdx = (currentPage - 1) * itemsPerPage;
    const endIdx = startIdx + itemsPerPage;
    return sortedConversations.slice(startIdx, endIdx);
  }, [sortedConversations, currentPage, itemsPerPage]);

  const totalPages = Math.ceil(sortedConversations.length / itemsPerPage);

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this conversation?')) return;

    try {
      setConversations((prev) => prev.filter((conv) => conv.id !== id));
    } catch (err) {
      setError('Failed to delete conversation');
      console.error('Failed to delete conversation:', err);
    }
  };

  const handleExport = (conv: ConversationSummary) => {
    const data = JSON.stringify(conv, null, 2);
    const element = document.createElement('a');
    element.setAttribute('href', 'data:text/json;charset=utf-8,' + encodeURIComponent(data));
    element.setAttribute('download', `consultation_${conv.id}.json`);
    element.style.display = 'none';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  const stats = {
    total: conversations.length,
    completed: conversations.filter((c) => c.status === 'completed').length,
    inProgress: conversations.filter((c) => c.status === 'in-progress').length,
    totalMessages: conversations.reduce((sum, c) => sum + c.messageCount, 0),
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Header */}
      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white">
        <div className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center mb-6">
            <div>
              <h1 className="text-4xl font-bold">Dashboard</h1>
              <p className="text-indigo-100 mt-2">
                Manage your medical consultations and reports
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <Link
                href="/profile"
                className="flex items-center space-x-2 px-4 py-2 bg-white/20 hover:bg-white/30 rounded-lg transition"
              >
                <span>👤</span>
                <span className="hidden sm:inline">Profile</span>
              </Link>
              <Link
                href="/settings"
                className="flex items-center space-x-2 px-4 py-2 bg-white/20 hover:bg-white/30 rounded-lg transition"
              >
                <span>⚙️</span>
                <span className="hidden sm:inline">Settings</span>
              </Link>
              <Link
                href="/chat/new"
                className="bg-white text-indigo-600 hover:bg-indigo-50 font-semibold py-2 px-6 rounded-lg transition-colors"
              >
                + New Consultation
              </Link>
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-white/10 backdrop-blur p-4 rounded-lg">
              <div className="text-2xl font-bold">{stats.total}</div>
              <div className="text-sm text-indigo-100">Total Consultations</div>
            </div>
            <div className="bg-white/10 backdrop-blur p-4 rounded-lg">
              <div className="text-2xl font-bold">{stats.completed}</div>
              <div className="text-sm text-indigo-100">Completed</div>
            </div>
            <div className="bg-white/10 backdrop-blur p-4 rounded-lg">
              <div className="text-2xl font-bold">{stats.inProgress}</div>
              <div className="text-sm text-indigo-100">In Progress</div>
            </div>
            <div className="bg-white/10 backdrop-blur p-4 rounded-lg">
              <div className="text-2xl font-bold">{stats.totalMessages}</div>
              <div className="text-sm text-indigo-100">Total Messages</div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
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

        {/* Search and Filters */}
        {!loading && conversations.length > 0 && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-8">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              {/* Search */}
              <div className="md:col-span-2">
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Search Consultations
                </label>
                <div className="relative">
                  <svg
                    className="absolute left-3 top-3 h-5 w-5 text-gray-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                    />
                  </svg>
                  <input
                    type="text"
                    placeholder="Search by title, summary, or tags..."
                    value={searchTerm}
                    onChange={(e) => {
                      setSearchTerm(e.target.value);
                      setCurrentPage(1);
                    }}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
                  />
                </div>
              </div>

              {/* Status Filter */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Status
                </label>
                <select
                  value={filterStatus}
                  onChange={(e) => {
                    setFilterStatus(e.target.value as any);
                    setCurrentPage(1);
                  }}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
                >
                  <option value="all">All</option>
                  <option value="completed">Completed</option>
                  <option value="in-progress">In Progress</option>
                </select>
              </div>

              {/* Sort */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Sort By
                </label>
                <select
                  value={sortBy}
                  onChange={(e) =>
                    setSortBy(e.target.value as 'recent' | 'oldest' | 'messages')
                  }
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
                >
                  <option value="recent">Most Recent</option>
                  <option value="oldest">Oldest First</option>
                  <option value="messages">Most Messages</option>
                </select>
              </div>
            </div>

            {/* Results info */}
            <div className="mt-4 text-sm text-gray-600">
              Showing <span className="font-semibold">{paginatedConversations.length}</span> of{' '}
              <span className="font-semibold">{sortedConversations.length}</span> consultations
            </div>
          </div>
        )}

        {/* Loading State */}
        {loading && <LoadingSkeleton />}

        {/* Empty State */}
        {!loading && conversations.length === 0 && !error && (
          <div className="text-center py-16 bg-white rounded-lg shadow">
            <div className="text-6xl mb-4">📋</div>
            <h2 className="text-2xl font-bold text-slate-900 mb-2">
              No Consultations Yet
            </h2>
            <p className="text-slate-600 max-w-md mx-auto mb-6">
              Start your first consultation to get AI-powered medical insights and detailed reports.
            </p>
            <Link
              href="/chat/new"
              className="inline-block bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold py-3 px-8 rounded-lg hover:shadow-lg transform hover:scale-105 transition"
            >
              Start First Consultation
            </Link>
          </div>
        )}

        {/* Conversations Grid */}
        {!loading && paginatedConversations.length > 0 && (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {paginatedConversations.map((conv) => (
                <div
                  key={conv.id}
                  className="bg-white rounded-lg shadow-md hover:shadow-xl transition-all border border-gray-100 overflow-hidden group"
                >
                  {/* Card Header */}
                  <div className="bg-gradient-to-r from-indigo-50 to-purple-50 p-4 border-b border-gray-100">
                    <div className="flex justify-between items-start mb-3">
                      <h3 className="text-lg font-semibold text-slate-900 flex-1 line-clamp-2 group-hover:text-indigo-600 transition">
                        {conv.title}
                      </h3>
                      <div className="flex items-center space-x-2 ml-2">
                        {conv.status === 'completed' && (
                          <span className="px-2 py-1 bg-green-100 text-green-700 text-xs font-semibold rounded-full">
                            ✓ Done
                          </span>
                        )}
                        {conv.status === 'in-progress' && (
                          <span className="px-2 py-1 bg-yellow-100 text-yellow-700 text-xs font-semibold rounded-full animate-pulse">
                            ⏳ Active
                          </span>
                        )}
                      </div>
                    </div>
                    <p className="text-xs text-gray-500 font-semibold">
                      Category: {conv.category}
                    </p>
                  </div>

                  {/* Card Body */}
                  <div className="p-4">
                    <p className="text-sm text-slate-600 mb-4 line-clamp-3">
                      {conv.summary}
                    </p>

                    {/* Tags */}
                    {conv.tags && conv.tags.length > 0 && (
                      <div className="flex flex-wrap gap-1 mb-4">
                        {conv.tags.slice(0, 3).map((tag) => (
                          <span
                            key={tag}
                            className="px-2 py-1 bg-indigo-100 text-indigo-700 text-xs rounded-full font-medium"
                          >
                            {tag}
                          </span>
                        ))}
                        {conv.tags.length > 3 && (
                          <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
                            +{conv.tags.length - 3}
                          </span>
                        )}
                      </div>
                    )}

                    {/* Stats */}
                    <div className="flex items-center justify-between text-xs text-slate-500 border-t border-slate-100 pt-3 mb-4">
                      <span>💬 {conv.messageCount} messages</span>
                      <span>{conv.updatedAt.toLocaleDateString()}</span>
                    </div>

                    {/* Actions */}
                    <div className="flex gap-2">
                      <Link
                        href={`/chat/${conv.id}`}
                        className="flex-1 text-center px-3 py-2 bg-gradient-to-r from-indigo-500 to-purple-500 hover:from-indigo-600 hover:to-purple-600 text-white text-sm font-semibold rounded transition-all"
                      >
                        View
                      </Link>
                      <button
                        onClick={() => handleExport(conv)}
                        className="px-3 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 text-sm font-semibold rounded transition"
                        title="Export"
                      >
                        📥
                      </button>
                      <button
                        onClick={() => handleDelete(conv.id)}
                        className="px-3 py-2 bg-red-50 hover:bg-red-100 text-red-600 text-sm font-semibold rounded transition"
                        title="Delete"
                      >
                        🗑️
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="mt-8 flex justify-center items-center space-x-2">
                <button
                  onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                  disabled={currentPage === 1}
                  className="px-4 py-2 bg-white border border-gray-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
                >
                  Previous
                </button>

                {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
                  <button
                    key={page}
                    onClick={() => setCurrentPage(page)}
                    className={`px-4 py-2 rounded-lg font-semibold transition ${
                      currentPage === page
                        ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white'
                        : 'bg-white border border-gray-300 hover:bg-gray-50'
                    }`}
                  >
                    {page}
                  </button>
                ))}

                <button
                  onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                  disabled={currentPage === totalPages}
                  className="px-4 py-2 bg-white border border-gray-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
                >
                  Next
                </button>
              </div>
            )}
          </>
        )}

        {/* No results */}
        {!loading && sortedConversations.length === 0 && conversations.length > 0 && (
          <div className="text-center py-12 bg-white rounded-lg shadow">
            <div className="text-4xl mb-3">🔍</div>
            <h2 className="text-xl font-bold text-slate-900 mb-2">
              No consultations found
            </h2>
            <p className="text-slate-600">
              Try adjusting your search or filter criteria
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

export default function DashboardPage() {
  return (
    <ProtectedRoute>
      <DashboardContent />
    </ProtectedRoute>
  );
}
