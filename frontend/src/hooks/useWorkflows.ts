'use client';

import { useState, useEffect } from 'react';
import { workflowApi } from '@/lib/api';

export function useWorkflows() {
  const [workflows, setWorkflows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchWorkflows = async () => {
    try {
      setLoading(true);
      const data = await workflowApi.list();
      setWorkflows(data);
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
      const data = await workflowApi.create(workflow);
      setWorkflows([...workflows, data]);
      return data;
    } catch (err: any) {
      setError(err.message);
      throw err;
    }
  };

  const updateWorkflow = async (id: string, workflow: any) => {
    try {
      const data = await workflowApi.update(id, workflow);
      setWorkflows(workflows.map((w: any) => w.id === id ? data : w));
      return data;
    } catch (err: any) {
      setError(err.message);
      throw err;
    }
  };

  const deleteWorkflow = async (id: string) => {
    try {
      await workflowApi.delete(id);
      setWorkflows(workflows.filter((w: any) => w.id !== id));
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
  const [executions, setExecutions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchExecutions = async () => {
    try {
      setLoading(true);
      const data = await workflowApi.getExecutions(workflowId);
      setExecutions(data);
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
      const data = await workflowApi.execute(id, context);
      setExecutions([data, ...executions]);
      return data;
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
