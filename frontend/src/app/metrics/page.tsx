"use client"

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/store/authStore'
import MetricsDashboard from '@/components/MetricsDashboard'

export default function MetricsPage() {
  const router = useRouter()
  const { user } = useAuthStore()

  useEffect(() => {
    if (!user) {
      router.push('/auth/login')
    }
  }, [user, router])

  if (!user) {
    return null
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Performance Metrics</h1>
          <p className="mt-2 text-gray-600">
            Track agent performance, response times, and usage statistics
          </p>
        </div>
        
        <MetricsDashboard />
      </div>
    </div>
  )
}
