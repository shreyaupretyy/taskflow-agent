'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';

export default function DashboardPage() {
  const router = useRouter();
  const { user, isAuthenticated } = useAuthStore();

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/auth/login');
    }
  }, [isAuthenticated, router]);

  if (!user) {
    return <div>Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold">TaskFlow Agent</h1>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => router.push('/metrics')}
                className="text-sm text-gray-600 hover:text-gray-900 font-medium"
              >
                Metrics
              </button>
              <span className="text-sm text-gray-700">{user.username}</span>
              <button
                onClick={() => {
                  useAuthStore.getState().clearAuth();
                  router.push('/auth/login');
                }}
                className="text-sm text-gray-600 hover:text-gray-900"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900">AI Agents</h2>
          <p className="mt-2 text-gray-600">Select a pre-built AI agent to start automating your tasks</p>
        </div>

        <div className="bg-white rounded-lg shadow">
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {/* Email Summarizer Agent */}
              <button
                onClick={() => router.push('/agents/email-summarizer')}
                className="p-6 border-2 border-gray-200 rounded-xl hover:border-blue-500 hover:shadow-lg transition-all text-left group"
              >
                <h4 className="text-lg font-bold text-gray-900 group-hover:text-blue-600">Email Summarizer</h4>
                <p className="text-sm text-gray-600 mt-2">Automatically analyze and summarize emails with priority detection</p>
                <div className="mt-4 flex items-center text-xs text-blue-600 font-medium">
                  <span>Use Agent</span>
                  <svg className="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              </button>

              {/* Content Generator Agent */}
              <button
                onClick={() => router.push('/agents/content-generator')}
                className="p-6 border-2 border-gray-200 rounded-xl hover:border-purple-500 hover:shadow-lg transition-all text-left group"
              >
                <h4 className="text-lg font-bold text-gray-900 group-hover:text-purple-600">Content Generator</h4>
                <p className="text-sm text-gray-600 mt-2">Research topics and write comprehensive articles and blog posts</p>
                <div className="mt-4 flex items-center text-xs text-purple-600 font-medium">
                  <span>Use Agent</span>
                  <svg className="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              </button>

              {/* Data Analyzer Agent */}
              <button
                onClick={() => router.push('/agents/data-analyzer')}
                className="p-6 border-2 border-gray-200 rounded-xl hover:border-green-500 hover:shadow-lg transition-all text-left group"
              >
                <h4 className="text-lg font-bold text-gray-900 group-hover:text-green-600">Data Analyzer</h4>
                <p className="text-sm text-gray-600 mt-2">Extract insights, identify patterns, and generate reports from data</p>
                <div className="mt-4 flex items-center text-xs text-green-600 font-medium">
                  <span>Use Agent</span>
                  <svg className="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              </button>

              {/* Customer Support Agent */}
              <button
                onClick={() => router.push('/agents/customer-support')}
                className="p-6 border-2 border-gray-200 rounded-xl hover:border-yellow-500 hover:shadow-lg transition-all text-left group"
              >
                <h4 className="text-lg font-bold text-gray-900 group-hover:text-yellow-600">Customer Support</h4>
                <p className="text-sm text-gray-600 mt-2">Analyze inquiries and generate professional support responses</p>
                <div className="mt-4 flex items-center text-xs text-orange-600 font-medium">
                  <span>Use Agent</span>
                  <svg className="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              </button>

              {/* Code Reviewer Agent */}
              <button
                onClick={() => router.push('/agents/code-reviewer')}
                className="p-6 border-2 border-gray-200 rounded-xl hover:border-indigo-500 hover:shadow-lg transition-all text-left group"
              >
                <h4 className="text-lg font-bold text-gray-900 group-hover:text-indigo-600">Code Reviewer</h4>
                <p className="text-sm text-gray-600 mt-2">Analyze code for bugs, security issues, and improvements</p>
                <div className="mt-4 flex items-center text-xs text-red-600 font-medium">
                  <span>Use Agent</span>
                  <svg className="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              </button>

              {/* Meeting Notes Agent */}
              <button
                onClick={() => router.push('/agents/meeting-notes')}
                className="p-6 border-2 border-gray-200 rounded-xl hover:border-pink-500 hover:shadow-lg transition-all text-left group"
              >
                <h4 className="text-lg font-bold text-gray-900 group-hover:text-pink-600">Meeting Notes</h4>
                <p className="text-sm text-gray-600 mt-2">Convert meeting transcripts into structured notes with action items</p>
                <div className="mt-4 flex items-center text-xs text-indigo-600 font-medium">
                  <span>Use Agent</span>
                  <svg className="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              </button>

              {/* Document Q&A (RAG) Agent */}
              <button
                onClick={() => router.push('/agents/document-qa')}
                className="p-6 border-2 border-gray-200 rounded-xl hover:border-teal-500 hover:shadow-lg transition-all text-left group"
              >
                <h4 className="text-lg font-bold text-gray-900 group-hover:text-teal-600">Document Q&A (RAG)</h4>
                <p className="text-sm text-gray-600 mt-2">Upload documents and ask questions using semantic search</p>
                <div className="mt-4 flex items-center text-xs text-teal-600 font-medium">
                  <span>Use Agent</span>
                  <svg className="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              </button>
            </div>
          </div>
        </div>
        
        <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-start">
            <div className="text-2xl mr-3">💡</div>
            <div>
              <h4 className="font-semibold text-blue-900">How to Use Agents</h4>
              <p className="text-sm text-blue-800 mt-1">
                Click on any agent card above → Enter your input text → Get instant AI-powered results!
                All agents work in demo mode without requiring additional setup.
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
