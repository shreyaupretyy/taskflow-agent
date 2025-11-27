'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { workflowApi } from '@/lib/api';
import { useAuthStore } from '@/store/authStore';
import { Loader2, Plus, Play, Edit, Trash2, Calendar } from 'lucide-react';

interface Workflow {
  id: number;
  name: string;
  description: string;
  is_active: boolean;
  trigger_type: string;
  created_at: string;
  updated_at: string;
}

export default function WorkflowsPage() {
  const router = useRouter();
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated());
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [deletingId, setDeletingId] = useState<number | null>(null);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/auth/login');
      return;
    }
    fetchWorkflows();
  }, [isAuthenticated, router]);

  const fetchWorkflows = async () => {
    try {
      setLoading(true);
      const response = await workflowApi.list();
      setWorkflows(response.data);
      setError('');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load workflows');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this workflow?')) {
      return;
    }

    try {
      setDeletingId(id);
      await workflowApi.delete(id);
      setWorkflows(workflows.filter(w => w.id !== id));
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to delete workflow');
    } finally {
      setDeletingId(null);
    }
  };

  const handleExecute = async (id: number) => {
    try {
      await workflowApi.execute(id, {});
      alert('Workflow execution started successfully!');
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to execute workflow');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold">Workflows</h1>
          <p className="text-gray-600 mt-2">Manage your AI-powered automation workflows</p>
        </div>
        <Button onClick={() => router.push('/workflows/create')}>
          <Plus className="h-4 w-4 mr-2" />
          Create Workflow
        </Button>
      </div>

      {error && (
        <div className="p-4 mb-6 text-red-500 bg-red-50 border border-red-200 rounded-lg">
          {error}
        </div>
      )}

      {workflows.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <div className="text-center">
              <h3 className="text-lg font-semibold mb-2">No workflows yet</h3>
              <p className="text-gray-600 mb-4">Create your first workflow to get started</p>
              <Button onClick={() => router.push('/workflows/create')}>
                <Plus className="h-4 w-4 mr-2" />
                Create Workflow
              </Button>
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {workflows.map((workflow) => (
            <Card key={workflow.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <CardTitle className="text-xl">{workflow.name}</CardTitle>
                    <CardDescription className="mt-2">{workflow.description}</CardDescription>
                  </div>
                  <span
                    className={`px-2 py-1 text-xs rounded-full ${
                      workflow.is_active
                        ? 'bg-green-100 text-green-700'
                        : 'bg-gray-100 text-gray-700'
                    }`}
                  >
                    {workflow.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center text-sm text-gray-600">
                    <Calendar className="h-4 w-4 mr-2" />
                    Trigger: {workflow.trigger_type}
                  </div>
                  <div className="text-xs text-gray-500">
                    Created: {new Date(workflow.created_at).toLocaleDateString()}
                  </div>
                  <div className="flex gap-2 mt-4">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleExecute(workflow.id)}
                      className="flex-1"
                    >
                      <Play className="h-3 w-3 mr-1" />
                      Run
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => router.push(`/workflows/${workflow.id}/edit`)}
                    >
                      <Edit className="h-3 w-3" />
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleDelete(workflow.id)}
                      disabled={deletingId === workflow.id}
                    >
                      {deletingId === workflow.id ? (
                        <Loader2 className="h-3 w-3 animate-spin" />
                      ) : (
                        <Trash2 className="h-3 w-3" />
                      )}
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
