'use client';

import { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { workflowApi } from '@/lib/api';
import { ArrowLeft, Save, Loader2, Play } from 'lucide-react';

export default function EditWorkflowPage() {
  const router = useRouter();
  const params = useParams();
  const workflowId = Number(params.id);
  
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [workflow, setWorkflow] = useState<any>(null);
  const [workflowNodes, setWorkflowNodes] = useState<any[]>([]);
  const [executing, setExecuting] = useState(false);
  const [testInput, setTestInput] = useState('');
  const [executionResult, setExecutionResult] = useState<any>(null);

  useEffect(() => {
    fetchWorkflow();
  }, [workflowId]);

  const fetchWorkflow = async () => {
    try {
      setLoading(true);
      const response = await workflowApi.get(workflowId);
      setWorkflow(response.data);
      
      // Load existing nodes
      if (response.data.workflow_data?.nodes) {
        setWorkflowNodes(response.data.workflow_data.nodes);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load workflow');
    } finally {
      setLoading(false);
    }
  };

  const addNode = (type: string) => {
    const newNode = {
      id: `node_${workflowNodes.length + 1}`,
      type: type,
      data: {
        config: {
          prompt: '',
          input: workflowNodes.length > 0 ? `{{node_${workflowNodes.length}.output}}` : ''
        }
      }
    };
    setWorkflowNodes([...workflowNodes, newNode]);
  };

  const removeNode = (nodeId: string) => {
    setWorkflowNodes(workflowNodes.filter(n => n.id !== nodeId));
  };

  const updateNodeConfig = (nodeId: string, field: string, value: string) => {
    setWorkflowNodes(workflowNodes.map(node => {
      if (node.id === nodeId) {
        return {
          ...node,
          data: {
            ...node.data,
            config: {
              ...node.data.config,
              [field]: value
            }
          }
        };
      }
      return node;
    }));
  };

  const getNodePlaceholder = (type: string) => {
    const placeholders: Record<string, string> = {
      extractor: 'Extract key information from the email: sender, subject, main points...',
      analyzer: 'Analyze the email sentiment and categorize it (urgent, info, request, etc.)',
      writer: 'Generate a concise 2-3 sentence summary of the email',
      researcher: 'Research additional context or information needed'
    };
    return placeholders[type] || 'Enter task instructions for this node';
  };

  const setupEmailSummarizer = () => {
    const nodes = [
      {
        id: 'node_1',
        type: 'extractor',
        data: {
          config: {
            prompt: 'Extract the following from the email: sender, subject, date, main topic, key points, and any action items or requests.',
            input: ''
          }
        }
      },
      {
        id: 'node_2',
        type: 'analyzer',
        data: {
          config: {
            prompt: 'Analyze the extracted email information and determine: 1) Priority level (High/Medium/Low), 2) Category (Question, Request, Information, Complaint, etc.), 3) Sentiment (Positive/Neutral/Negative)',
            input: '{{node_1.output}}'
          }
        }
      },
      {
        id: 'node_3',
        type: 'writer',
        data: {
          config: {
            prompt: 'Generate a professional 2-3 sentence summary of the email that includes the main point, any action required, and the priority level.',
            input: '{{node_2.output}}'
          }
        }
      }
    ];
    setWorkflowNodes(nodes);
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      
      // Build edges connecting nodes sequentially
      const edges = workflowNodes.slice(0, -1).map((node, index) => ({
        id: `edge_${index + 1}`,
        source: node.id,
        target: workflowNodes[index + 1].id
      }));

      const updatedWorkflow = {
        ...workflow,
        workflow_data: {
          nodes: workflowNodes,
          edges: edges
        }
      };

      await workflowApi.update(workflowId, updatedWorkflow);
      setWorkflow(updatedWorkflow);
      alert('Workflow saved successfully! You can now run it from the workflows list.');
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to save workflow');
    } finally {
      setSaving(false);
    }
  };

  const handleTestRun = async () => {
    if (!testInput.trim()) {
      alert('Please enter test input (e.g., an email to summarize)');
      return;
    }

    try {
      setExecuting(true);
      setExecutionResult(null);
      
      // Save workflow first
      const edges = workflowNodes.slice(0, -1).map((node, index) => ({
        id: `edge_${index + 1}`,
        source: node.id,
        target: workflowNodes[index + 1].id
      }));

      await workflowApi.update(workflowId, {
        ...workflow,
        workflow_data: {
          nodes: workflowNodes,
          edges: edges
        }
      });

      // Execute workflow
      const result = await workflowApi.execute(workflowId, {
        input_data: { text: testInput }
      });

      setExecutionResult(result.data);
      
      if (result.data.status === 'completed') {
        alert('✓ Workflow completed successfully! Check results below.');
      } else if (result.data.status === 'failed') {
        alert('✗ Workflow failed. Check error details below.');
      } else {
        alert('Workflow execution started! Status: ' + result.data.status);
      }
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to execute workflow');
    } finally {
      setExecuting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (error || !workflow) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="p-4 text-red-500 bg-red-50 border border-red-200 rounded-lg">
          {error || 'Workflow not found'}
        </div>
        <Button onClick={() => router.push('/workflows')} className="mt-4">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Workflows
        </Button>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <Button variant="ghost" onClick={() => router.push('/workflows')}>
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back
        </Button>
        <Button onClick={handleSave} disabled={saving}>
          {saving ? (
            <>
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              Saving...
            </>
          ) : (
            <>
              <Save className="h-4 w-4 mr-2" />
              Save
            </>
          )}
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-2xl">Edit Workflow: {workflow.name}</CardTitle>
          <p className="text-sm text-gray-600 mt-2">
            Build your AI workflow by adding nodes that process data sequentially
          </p>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            <div className="space-y-2">
              <label className="text-sm font-medium">Name</label>
              <input
                type="text"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                value={workflow.name}
                onChange={(e) => setWorkflow({ ...workflow, name: e.target.value })}
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Description</label>
              <textarea
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                rows={4}
                value={workflow.description}
                onChange={(e) => setWorkflow({ ...workflow, description: e.target.value })}
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Trigger Type</label>
              <select
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                value={workflow.trigger_type}
                onChange={(e) => setWorkflow({ ...workflow, trigger_type: e.target.value })}
              >
                <option value="manual">Manual</option>
                <option value="scheduled">Scheduled</option>
                <option value="webhook">Webhook</option>
                <option value="event">Event</option>
              </select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Status</label>
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="is_active"
                  checked={workflow.is_active}
                  onChange={(e) => setWorkflow({ ...workflow, is_active: e.target.checked })}
                  className="h-4 w-4"
                />
                <label htmlFor="is_active" className="text-sm">
                  Active
                </label>
              </div>
            </div>

            <div className="border-t pt-6">
              <h3 className="text-lg font-semibold mb-4">Workflow Configuration</h3>
              
              {/* Node Templates */}
              <div className="mb-6">
                <h4 className="text-sm font-medium mb-3">Add Nodes</h4>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  <button
                    type="button"
                    onClick={() => addNode('extractor')}
                    className="p-3 border-2 border-blue-300 bg-blue-50 rounded-lg hover:bg-blue-100 text-left"
                  >
                    <div className="font-medium text-blue-900">📧 Extractor</div>
                    <div className="text-xs text-blue-700 mt-1">Extract data from text</div>
                  </button>
                  <button
                    type="button"
                    onClick={() => addNode('analyzer')}
                    className="p-3 border-2 border-purple-300 bg-purple-50 rounded-lg hover:bg-purple-100 text-left"
                  >
                    <div className="font-medium text-purple-900">🔍 Analyzer</div>
                    <div className="text-xs text-purple-700 mt-1">Analyze and classify</div>
                  </button>
                  <button
                    type="button"
                    onClick={() => addNode('writer')}
                    className="p-3 border-2 border-green-300 bg-green-50 rounded-lg hover:bg-green-100 text-left"
                  >
                    <div className="font-medium text-green-900">✍️ Writer</div>
                    <div className="text-xs text-green-700 mt-1">Generate summaries</div>
                  </button>
                  <button
                    type="button"
                    onClick={() => addNode('researcher')}
                    className="p-3 border-2 border-orange-300 bg-orange-50 rounded-lg hover:bg-orange-100 text-left"
                  >
                    <div className="font-medium text-orange-900">🔬 Researcher</div>
                    <div className="text-xs text-orange-700 mt-1">Research information</div>
                  </button>
                </div>
              </div>

              {/* Current Nodes */}
              <div className="space-y-3">
                <h4 className="text-sm font-medium">Workflow Nodes ({workflowNodes.length})</h4>
                {workflowNodes.length === 0 ? (
                  <div className="bg-gray-50 border border-gray-200 rounded-lg p-6 text-center">
                    <p className="text-gray-600">No nodes added yet</p>
                    <p className="text-sm text-gray-500 mt-1">Click a node type above to add it to your workflow</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {workflowNodes.map((node, index) => (
                      <div key={node.id} className="border border-gray-300 rounded-lg p-4 bg-white">
                        <div className="flex justify-between items-start mb-3">
                          <div className="flex-1">
                            <h5 className="font-medium">
                              {index + 1}. {node.type.charAt(0).toUpperCase() + node.type.slice(1)} Node
                            </h5>
                            <p className="text-xs text-gray-500 mt-1">ID: {node.id}</p>
                          </div>
                          <button
                            type="button"
                            onClick={() => removeNode(node.id)}
                            className="text-red-500 hover:text-red-700"
                          >
                            Remove
                          </button>
                        </div>
                        
                        <div className="space-y-3">
                          <div>
                            <label className="text-xs font-medium text-gray-700">Task/Prompt</label>
                            <textarea
                              className="w-full px-2 py-1 text-sm border border-gray-300 rounded mt-1"
                              rows={3}
                              placeholder={getNodePlaceholder(node.type)}
                              value={node.data.config?.prompt || ''}
                              onChange={(e) => updateNodeConfig(node.id, 'prompt', e.target.value)}
                            />
                          </div>
                          
                          {index > 0 && (
                            <div>
                              <label className="text-xs font-medium text-gray-700">Input from previous node</label>
                              <input
                                type="text"
                                className="w-full px-2 py-1 text-sm border border-gray-300 rounded mt-1"
                                placeholder="{{node_1.output}}"
                                value={node.data.config?.input || ''}
                                onChange={(e) => updateNodeConfig(node.id, 'input', e.target.value)}
                              />
                              <p className="text-xs text-gray-500 mt-1">
                                Use {`{{node_${index}.output}}`} to reference previous node output
                              </p>
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Quick Setup for Email Summarizer */}
              {workflowNodes.length === 0 && workflow.name.toLowerCase().includes('email') && (
                <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                  <h5 className="font-medium text-blue-900 mb-2">💡 Quick Setup: Email Summarizer</h5>
                  <p className="text-sm text-blue-700 mb-3">
                    Add pre-configured nodes for email summarization workflow
                  </p>
                  <button
                    type="button"
                    onClick={setupEmailSummarizer}
                    className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm"
                  >
                    Set Up Email Summarizer
                  </button>
                </div>
              )}
            </div>

            {/* Test & Run Section */}
            {workflowNodes.length > 0 && (
              <div className="border-t pt-6">
                <h3 className="text-lg font-semibold mb-4">Test Workflow</h3>
                <div className="space-y-4">
                  <div>
                    <label className="text-sm font-medium">Test Input</label>
                    <textarea
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary mt-2"
                      rows={6}
                      placeholder="Paste an email or text to summarize here..."
                      value={testInput}
                      onChange={(e) => setTestInput(e.target.value)}
                      disabled={executing}
                    />
                  </div>
                  
                  <Button
                    type="button"
                    onClick={handleTestRun}
                    disabled={executing || !testInput.trim()}
                    className="w-full"
                  >
                    {executing ? (
                      <>
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        Executing Workflow...
                      </>
                    ) : (
                      <>
                        <Play className="h-4 w-4 mr-2" />
                        Run Test
                      </>
                    )}
                  </Button>

                  {executionResult && (
                    <div className="mt-4 space-y-3">
                      <div className={`p-4 border rounded-lg ${
                        executionResult.status === 'completed' ? 'bg-green-50 border-green-200' :
                        executionResult.status === 'failed' ? 'bg-red-50 border-red-200' :
                        executionResult.status === 'running' ? 'bg-blue-50 border-blue-200' :
                        'bg-yellow-50 border-yellow-200'
                      }`}>
                        <h4 className={`font-medium mb-2 ${
                          executionResult.status === 'completed' ? 'text-green-900' :
                          executionResult.status === 'failed' ? 'text-red-900' :
                          executionResult.status === 'running' ? 'text-blue-900' :
                          'text-yellow-900'
                        }`}>
                          {executionResult.status === 'completed' ? '✓ Execution Completed' :
                           executionResult.status === 'failed' ? '✗ Execution Failed' :
                           executionResult.status === 'running' ? '⟳ Execution Running' :
                           '⏱ Execution Pending'}
                        </h4>
                        <div className="text-sm space-y-1">
                          <p><strong>Execution ID:</strong> {executionResult.id}</p>
                          <p><strong>Status:</strong> {executionResult.status}</p>
                          {executionResult.started_at && (
                            <p><strong>Started:</strong> {new Date(executionResult.started_at).toLocaleString()}</p>
                          )}
                          {executionResult.completed_at && (
                            <p><strong>Completed:</strong> {new Date(executionResult.completed_at).toLocaleString()}</p>
                          )}
                        </div>
                      </div>

                      {executionResult.output_data && (
                        <div className="p-4 bg-gray-50 border border-gray-200 rounded-lg">
                          <h5 className="font-medium mb-2">Results:</h5>
                          <pre className="text-xs bg-white p-3 rounded border overflow-auto max-h-96">
                            {JSON.stringify(executionResult.output_data, null, 2)}
                          </pre>
                        </div>
                      )}

                      {executionResult.error_message && (
                        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                          <h5 className="font-medium text-red-900 mb-2">Error:</h5>
                          <p className="text-sm text-red-700">{executionResult.error_message}</p>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
