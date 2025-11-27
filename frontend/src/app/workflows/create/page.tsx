'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { workflowApi } from '@/lib/api';
import { ArrowLeft, Loader2 } from 'lucide-react';

export default function CreateWorkflowPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    trigger_type: 'manual',
    template: '',
  });

  const getTemplateNodes = (template: string) => {
    const templates: Record<string, any> = {
      email_summarizer: [
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
      ],
      content_generator: [
        {
          id: 'node_1',
          type: 'researcher',
          data: {
            config: {
              prompt: 'Research the given topic and gather key information, facts, and relevant details.',
              input: ''
            }
          }
        },
        {
          id: 'node_2',
          type: 'writer',
          data: {
            config: {
              prompt: 'Write a comprehensive, engaging article or blog post based on the research. Include an introduction, main points, and conclusion.',
              input: '{{node_1.output}}'
            }
          }
        }
      ],
      data_analyzer: [
        {
          id: 'node_1',
          type: 'extractor',
          data: {
            config: {
              prompt: 'Extract and structure the data from the provided text or document.',
              input: ''
            }
          }
        },
        {
          id: 'node_2',
          type: 'analyzer',
          data: {
            config: {
              prompt: 'Analyze the extracted data to identify patterns, trends, anomalies, and key insights.',
              input: '{{node_1.output}}'
            }
          }
        },
        {
          id: 'node_3',
          type: 'writer',
          data: {
            config: {
              prompt: 'Create a clear, actionable report summarizing the analysis findings with recommendations.',
              input: '{{node_2.output}}'
            }
          }
        }
      ],
      customer_support: [
        {
          id: 'node_1',
          type: 'analyzer',
          data: {
            config: {
              prompt: 'Analyze the customer inquiry to understand: 1) Issue type, 2) Urgency level, 3) Customer sentiment, 4) Required department/expertise.',
              input: ''
            }
          }
        },
        {
          id: 'node_2',
          type: 'writer',
          data: {
            config: {
              prompt: 'Generate a professional, empathetic response addressing the customer\'s concern with clear next steps or solutions.',
              input: '{{node_1.output}}'
            }
          }
        }
      ],
      meeting_notes: [
        {
          id: 'node_1',
          type: 'extractor',
          data: {
            config: {
              prompt: 'Extract from meeting transcript: attendees, main topics discussed, decisions made, action items with owners, and deadlines.',
              input: ''
            }
          }
        },
        {
          id: 'node_2',
          type: 'writer',
          data: {
            config: {
              prompt: 'Create structured meeting notes with: summary, key decisions, action items table (task, owner, deadline), and next steps.',
              input: '{{node_1.output}}'
            }
          }
        }
      ],
      code_reviewer: [
        {
          id: 'node_1',
          type: 'analyzer',
          data: {
            config: {
              prompt: 'Analyze the code for: 1) Potential bugs, 2) Security issues, 3) Performance problems, 4) Code quality and best practices violations.',
              input: ''
            }
          }
        },
        {
          id: 'node_2',
          type: 'writer',
          data: {
            config: {
              prompt: 'Generate a detailed code review with specific suggestions, improvement recommendations, and code examples where applicable.',
              input: '{{node_1.output}}'
            }
          }
        }
      ]
    };
    return templates[template] || [];
  };

  const getTemplateName = (template: string) => {
    const names: Record<string, string> = {
      email_summarizer: 'Email Summarizer - Extracts, analyzes, and summarizes emails',
      content_generator: 'Content Generator - Researches and writes articles',
      data_analyzer: 'Data Analyzer - Extracts data, analyzes patterns, creates reports',
      customer_support: 'Customer Support - Analyzes inquiries and generates responses',
      meeting_notes: 'Meeting Notes - Extracts action items and creates structured notes',
      code_reviewer: 'Code Reviewer - Analyzes code and provides improvement suggestions'
    };
    return names[template] || template;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const nodes = formData.template ? getTemplateNodes(formData.template) : [];
      const edges = nodes.slice(0, -1).map((node: any, index: number) => ({
        id: `edge_${index + 1}`,
        source: node.id,
        target: nodes[index + 1].id
      }));

      const response = await workflowApi.create({
        name: formData.name,
        description: formData.description,
        trigger_type: formData.trigger_type,
        workflow_data: {
          nodes: nodes,
          edges: edges,
        },
      });
      
      router.push(`/workflows/${response.data.id}/edit`);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create workflow');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-2xl">
      <Button
        variant="ghost"
        onClick={() => router.back()}
        className="mb-6"
      >
        <ArrowLeft className="h-4 w-4 mr-2" />
        Back
      </Button>

      <Card>
        <CardHeader>
          <CardTitle className="text-2xl">Create New Workflow</CardTitle>
          <CardDescription>
            Set up a new AI-powered automation workflow
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            {error && (
              <div className="p-3 text-sm text-red-500 bg-red-50 border border-red-200 rounded-md">
                {error}
              </div>
            )}

            <div className="space-y-2">
              <label htmlFor="template" className="text-sm font-medium">
                Workflow Template
              </label>
              <select
                id="template"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                value={formData.template}
                onChange={(e) => setFormData({ ...formData, template: e.target.value })}
                disabled={loading}
              >
                <option value="">Blank Workflow</option>
                <option value="email_summarizer">Email Summarizer</option>
                <option value="content_generator">✍️ Content Generator</option>
                <option value="data_analyzer">Data Analyzer</option>
                <option value="customer_support">Customer Support Assistant</option>
                <option value="meeting_notes">Meeting Notes Generator</option>
                <option value="code_reviewer">👨‍💻 Code Reviewer</option>
              </select>
              <p className="text-xs text-gray-500">
                Choose a template to start with pre-configured AI nodes, or select blank to build from scratch
              </p>
              {formData.template && (
                <div className="mt-2 p-3 bg-blue-50 border border-blue-200 rounded-md text-sm text-blue-900">
                  ✓ Template selected: {getTemplateName(formData.template)}
                </div>
              )}
            </div>

            <div className="space-y-2">
              <label htmlFor="name" className="text-sm font-medium">
                Workflow Name *
              </label>
              <Input
                id="name"
                type="text"
                placeholder="My Automation Workflow"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
                disabled={loading}
              />
            </div>

            <div className="space-y-2">
              <label htmlFor="description" className="text-sm font-medium">
                Description
              </label>
              <textarea
                id="description"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                placeholder="Describe what this workflow does..."
                rows={4}
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                disabled={loading}
              />
            </div>

            <div className="space-y-2">
              <label htmlFor="trigger_type" className="text-sm font-medium">
                Trigger Type *
              </label>
              <select
                id="trigger_type"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                value={formData.trigger_type}
                onChange={(e) => setFormData({ ...formData, trigger_type: e.target.value })}
                disabled={loading}
              >
                <option value="manual">Manual</option>
                <option value="scheduled">Scheduled</option>
                <option value="webhook">Webhook</option>
                <option value="event">Event</option>
              </select>
              <p className="text-xs text-gray-500">
                Manual: Run on demand | Scheduled: Run on a schedule | Webhook: Trigger via API | Event: Trigger on system events
              </p>
            </div>

            <div className="flex gap-3 pt-4">
              <Button
                type="submit"
                disabled={loading}
                className="flex-1"
              >
                {loading ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Creating...
                  </>
                ) : (
                  'Create Workflow'
                )}
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => router.back()}
                disabled={loading}
              >
                Cancel
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
