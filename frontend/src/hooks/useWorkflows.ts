'use client';

import { useState, useEffect } from 'react';
import { workflowApi } from '@/lib/api';

export function useWorkflows() {
  const [workflows, setWorkflows] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchWorkflows = async () => {
    try {
      setLoading(true);
      const response = await workflowApi.list();
      setWorkflows(response.data);
      setError(null);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWorkflows();
  }, []);

  const createWorkflow = async (workflow: any) => {
    try {
      const response = await workflowApi.create(workflow);
      setWorkflows([...workflows, response.data]);
      return response.data;
    } catch (err: any) {
      setError(err.message);
      throw err;
    }
  };

  const updateWorkflow = async (id: string, workflow: any) => {
    try {
      const response = await workflowApi.update(parseInt(id), workflow);
      setWorkflows(workflows.map((w: any) => w.id === parseInt(id) ? response.data : w));
      return response.data;
    } catch (err: any) {
      setError(err.message);
      throw err;
    }
  };

  const deleteWorkflow = async (id: string) => {
    try {
      await workflowApi.delete(parseInt(id));
      setWorkflows(workflows.filter((w: any) => w.id !== parseInt(id)));
    } catch (err: any) {
      setError(err.message);
      throw err;
    }
  };

  return {
    workflows,
    loading,
    error,
    refetch: fetchWorkflows,
    createWorkflow,
    updateWorkflow,
    deleteWorkflow,
  };
}

export function useWorkflowExecutions(workflowId?: string) {
  const [executions, setExecutions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchExecutions = async () => {
    try {
      setLoading(true);
      const response = await workflowApi.listExecutions(parseInt(workflowId!));
      setExecutions(response.data);
      setError(null);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (workflowId) {
      fetchExecutions();
    }
  }, [workflowId]);

  const executeWorkflow = async (id: string, context?: any) => {
    try {
      const response = await workflowApi.execute(parseInt(id), context);
      setExecutions([response.data, ...executions]);
      return response.data;
    } catch (err: any) {
      setError(err.message);
      throw err;
    }
  };

  return {
    executions,
    loading,
    error,
    refetch: fetchExecutions,
    executeWorkflow,
  };
}
