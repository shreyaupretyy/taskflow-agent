"use client"

import { useEffect, useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

interface AgentMetric {
  agent_type: string
  total_executions: number
  success_rate: number
  avg_response_time_ms: number
  avg_rating: number
}

interface UserStats {
  total_executions: number
  successful_executions: number
  failed_executions: number
  success_rate: number
  avg_response_time_ms: number
  agents_used: string[]
  executions_per_agent: { [key: string]: number }
  period_days: number
}

export default function MetricsDashboard() {
  const [metrics, setMetrics] = useState<AgentMetric[]>([])
  const [userStats, setUserStats] = useState<UserStats | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchMetrics()
  }, [])

  const fetchMetrics = async () => {
    try {
      const token = localStorage.getItem('token')
      
      // Fetch agent metrics
      const metricsResponse = await fetch('http://localhost:8000/api/v1/agents/metrics', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (metricsResponse.ok) {
        const metricsData = await metricsResponse.json()
        setMetrics(Array.isArray(metricsData.metrics) ? metricsData.metrics : [])
      }
      
      // Fetch user stats
      const statsResponse = await fetch('http://localhost:8000/api/v1/agents/my-stats?days=30', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (statsResponse.ok) {
        const statsData = await statsResponse.json()
        setUserStats(statsData.stats)
      }
    } catch (error) {
      console.error('Error fetching metrics:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* User Statistics */}
      {userStats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium">Total Executions</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{userStats.total_executions}</div>
              <p className="text-xs text-muted-foreground">Last {userStats.period_days} days</p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{userStats.success_rate.toFixed(1)}%</div>
              <p className="text-xs text-muted-foreground">
                {userStats.successful_executions} / {userStats.total_executions}
              </p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium">Avg Response Time</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{(userStats.avg_response_time_ms / 1000).toFixed(2)}s</div>
              <p className="text-xs text-muted-foreground">Average processing time</p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium">Agents Used</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{userStats.agents_used.length}</div>
              <p className="text-xs text-muted-foreground">Different agent types</p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Agent Performance Metrics */}
      <Card>
        <CardHeader>
          <CardTitle>Agent Performance Metrics</CardTitle>
          <CardDescription>
            Performance statistics for each agent type
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {metrics.length === 0 ? (
              <p className="text-sm text-muted-foreground">No metrics available yet. Start using agents to see statistics.</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left py-2 px-4">Agent Type</th>
                      <th className="text-right py-2 px-4">Executions</th>
                      <th className="text-right py-2 px-4">Success Rate</th>
                      <th className="text-right py-2 px-4">Avg Response Time</th>
                      <th className="text-right py-2 px-4">Avg Rating</th>
                    </tr>
                  </thead>
                  <tbody>
                    {metrics.map((metric) => (
                      <tr key={metric.agent_type} className="border-b hover:bg-muted/50">
                        <td className="py-2 px-4 font-medium capitalize">{metric.agent_type}</td>
                        <td className="text-right py-2 px-4">{metric.total_executions}</td>
                        <td className="text-right py-2 px-4">
                          <span className={metric.success_rate >= 90 ? 'text-green-600' : metric.success_rate >= 70 ? 'text-yellow-600' : 'text-red-600'}>
                            {metric.success_rate.toFixed(1)}%
                          </span>
                        </td>
                        <td className="text-right py-2 px-4">{(metric.avg_response_time_ms / 1000).toFixed(2)}s</td>
                        <td className="text-right py-2 px-4">
                          {metric.avg_rating > 0 ? (
                            <span className="flex items-center justify-end gap-1">
                              {metric.avg_rating.toFixed(1)} ⭐
                            </span>
                          ) : (
                            <span className="text-muted-foreground">No ratings</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Usage by Agent */}
      {userStats && userStats.executions_per_agent && Object.keys(userStats.executions_per_agent).length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Your Agent Usage</CardTitle>
            <CardDescription>
              Breakdown of your executions by agent type
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {Object.entries(userStats.executions_per_agent).map(([agent, count]) => {
                const percentage = (count / userStats.total_executions) * 100
                return (
                  <div key={agent}>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm font-medium capitalize">{agent}</span>
                      <span className="text-sm text-muted-foreground">{count} ({percentage.toFixed(0)}%)</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-blue-600 h-2 rounded-full transition-all"
                        style={{ width: `${percentage}%` }}
                      ></div>
                    </div>
                  </div>
                )
              })}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
