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
          <h2 className="text-3xl font-bold text-gray-900">Dashboard</h2>
          <p className="mt-2 text-gray-600">Welcome to your workflow automation platform</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-2">Workflows</h3>
            <p className="text-3xl font-bold text-blue-600">0</p>
            <p className="text-sm text-gray-600 mt-2">Total workflows created</p>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-2">Executions</h3>
            <p className="text-3xl font-bold text-green-600">0</p>
            <p className="text-sm text-gray-600 mt-2">Total executions</p>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-2">Active Workflows</h3>
            <p className="text-3xl font-bold text-purple-600">0</p>
            <p className="text-sm text-gray-600 mt-2">Currently active</p>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow">
          <div className="p-6">
            <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <button
                onClick={() => router.push('/workflows/create')}
                className="p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors"
              >
                <div className="text-center">
                  <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                  </svg>
                  <h4 className="mt-2 text-sm font-medium text-gray-900">Create New Workflow</h4>
                  <p className="mt-1 text-xs text-gray-500">Build an AI-powered workflow</p>
                </div>
              </button>
              
              <button
                onClick={() => router.push('/workflows')}
                className="p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors"
              >
                <div className="text-center">
                  <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                  </svg>
                  <h4 className="mt-2 text-sm font-medium text-gray-900">View All Workflows</h4>
                  <p className="mt-1 text-xs text-gray-500">Manage existing workflows</p>
                </div>
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
