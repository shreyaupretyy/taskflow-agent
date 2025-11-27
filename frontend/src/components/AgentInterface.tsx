'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { ArrowLeft, Loader2, Play } from 'lucide-react';
import { useRouter } from 'next/navigation';

interface AgentInterfaceProps {
  agentId: string;
  agentName: string;
  agentIcon: string;
  agentDescription: string;
  placeholder: string;
  exampleInput: string;
  color: string;
}

export default function AgentInterface({
  agentId,
  agentName,
  agentIcon,
  agentDescription,
  placeholder,
  exampleInput,
  color
}: AgentInterfaceProps) {
  const router = useRouter();
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleExecute = async () => {
    if (!input.trim()) {
      alert('Please enter some input text');
      return;
    }

    setLoading(true);
    setResult(null);

    try {
      // Call backend API
      const token = localStorage.getItem('token');
      
      if (!token) {
        alert('Not logged in. Please login again.');
        router.push('/auth/login');
        return;
      }
      
      const response = await fetch('http://localhost:8000/api/v1/agents/execute', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          agent_id: agentId,
          input_text: input
        })
      });

      if (response.status === 401) {
        alert('Session expired. Please login again.');
        localStorage.removeItem('token');
        router.push('/auth/login');
        return;
      }
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(`API Error: ${response.status} - ${JSON.stringify(errorData)}`);
      }

      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error('Error executing agent:', error);
      // Fallback to demo mode if API fails
      const demoResult = generateDemoResult(agentId, input);
      setResult({
        ...demoResult,
        message: 'API connection failed - showing demo results'
      });
    } finally {
      setLoading(false);
    }
  };

  const loadExample = () => {
    setInput(exampleInput);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <Button variant="ghost" onClick={() => router.push('/dashboard')}>
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Dashboard
              </Button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-6">
          <div className="flex items-center gap-3 mb-2">
            {agentIcon && <span className="text-4xl">{agentIcon}</span>}
            <h1 className="text-3xl font-bold">{agentName}</h1>
          </div>
          <p className="text-gray-600">{agentDescription}</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Input Section */}
          <Card>
            <CardHeader>
              <CardTitle>Input</CardTitle>
              <CardDescription>Enter your content for the agent to process</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <textarea
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                rows={12}
                placeholder={placeholder}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                disabled={loading}
              />
              
              <div className="flex gap-2">
                <Button
                  onClick={handleExecute}
                  disabled={loading || !input.trim()}
                  className="flex-1"
                  style={{ backgroundColor: loading ? undefined : color }}
                >
                  {loading ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Processing...
                    </>
                  ) : (
                    <>
                      <Play className="h-4 w-4 mr-2" />
                      Run Agent
                    </>
                  )}
                </Button>
                <Button
                  onClick={loadExample}
                  variant="outline"
                  disabled={loading}
                >
                  Load Example
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Output Section */}
          <Card>
            <CardHeader>
              <CardTitle>Output</CardTitle>
              <CardDescription>Agent processing results</CardDescription>
            </CardHeader>
            <CardContent>
              {!result && !loading && (
                <div className="flex items-center justify-center h-64 text-gray-400">
                  <div className="text-center">
                    <p className="text-lg font-medium">Run the agent to see results</p>
                  </div>
                </div>
              )}

              {loading && (
                <div className="flex items-center justify-center h-64">
                  <Loader2 className="h-8 w-8 animate-spin text-primary" />
                </div>
              )}

              {result && (
                <div className="space-y-4">
                  {(result.demo_mode || result.message) && (
                    <div className="p-3 bg-yellow-50 border border-yellow-300 rounded text-sm text-yellow-900">
                      {result.message || 'DEMO MODE: These are simulated results. Install Ollama for real AI processing.'}
                    </div>
                  )}
                  
                  <div className="bg-white rounded-lg p-6 border border-gray-200">
                    <div className="prose prose-sm max-w-none">
                      <pre className="whitespace-pre-wrap font-sans text-sm leading-relaxed text-gray-800">
                        {result.output?.report || result.output?.data || JSON.stringify(result.output, null, 2)}
                      </pre>
                    </div>
                  </div>

                  <Button
                    onClick={() => {
                      const text = result.output?.report || result.output?.data || JSON.stringify(result.output, null, 2);
                      navigator.clipboard.writeText(text);
                      alert('Copied to clipboard!');
                    }}
                    variant="outline"
                    className="w-full"
                  >
                    Copy Result
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}

function generateDemoResult(agentId: string, input: string): any {
  const results: Record<string, any> = {
    'email-summarizer': {
      demo_mode: true,
      output: {
        summary: "This email discusses project updates and requires action by end of week. Priority: High. The sender requests review of the attached documents and approval for next phase.",
        extracted_data: {
          sender: "demo@example.com",
          subject: "Project Update - Action Required",
          priority: "High",
          category: "Action Required",
          sentiment: "Positive",
          action_items: [
            "Review attached documents",
            "Approve next phase",
            "Respond by end of week"
          ],
          key_points: [
            "Project is on track",
            "Next phase ready to begin",
            "Requires management approval"
          ]
        }
      }
    },
    'content-generator': {
      demo_mode: true,
      output: {
        title: "The Future of AI in Modern Business",
        content: `In today's rapidly evolving business landscape, Artificial Intelligence has emerged as a transformative force that is reshaping how companies operate, compete, and deliver value to their customers.

The integration of AI technologies into business processes has demonstrated remarkable benefits across various sectors. From automated customer service chatbots to predictive analytics systems that forecast market trends, AI is enabling businesses to operate more efficiently and make data-driven decisions with unprecedented accuracy.

Key areas where AI is making significant impact include process automation, customer experience enhancement, and strategic decision-making. Organizations that successfully adopt AI technologies are seeing improved operational efficiency, reduced costs, and enhanced competitive advantages.

As we look toward the future, the role of AI in business will only continue to grow, making it essential for organizations to develop AI strategies and capabilities to remain competitive in the digital age.`,
        word_count: 142,
        summary: "An overview of AI's transformative impact on modern business operations and strategy"
      }
    },
    'data-analyzer': {
      demo_mode: true,
      output: {
        summary: "Analysis reveals positive trends with moderate growth indicators and stable performance metrics.",
        insights: [
          "Overall performance shows 15% improvement compared to previous period",
          "Key metrics indicate sustainable growth trajectory",
          "Customer satisfaction scores remain consistently high at 87%",
          "Operational efficiency improved by 12% this quarter"
        ],
        patterns: [
          "Peak activity occurs during mid-week periods",
          "Seasonal variations show 20% increase in Q4",
          "User engagement correlates strongly with feature adoption"
        ],
        recommendations: [
          "Focus resources on high-performing segments",
          "Implement optimization strategies in identified areas",
          "Monitor emerging trends for early intervention",
          "Scale successful initiatives to maximize ROI"
        ],
        confidence: 0.87
      }
    },
    'customer-support': {
      demo_mode: true,
      output: {
        response: `Thank you for reaching out to us. I understand you're experiencing difficulties with your account access, and I sincerely apologize for any inconvenience this has caused.

I've reviewed your account and identified that your login credentials may need to be reset. Here's what I recommend:

1. **Immediate Action**: Please use our password reset feature at [yourcompany.com/reset]
2. **Verification**: Check your registered email for the verification code
3. **Alternative**: If the above doesn't work, our technical team can manually verify your account

Our priority is to get you back to accessing your account as quickly as possible. The typical resolution time for this issue is under 15 minutes.

Please let me know if you continue to experience any issues after trying these steps, and I'll personally ensure this gets resolved for you.

Best regards,
Customer Support Team`,
        analysis: {
          issue_type: "Account Access",
          priority: "High",
          sentiment: "Frustrated but polite",
          estimated_resolution: "15 minutes"
        }
      }
    },
    'code-reviewer': {
      demo_mode: true,
      output: {
        overall_assessment: "Code quality: Good | Security: Needs attention | Performance: Acceptable",
        findings: [
          {
            severity: "High",
            category: "Security",
            issue: "SQL injection vulnerability detected",
            line: "User input not sanitized before database query",
            recommendation: "Use parameterized queries or ORM to prevent SQL injection"
          },
          {
            severity: "Medium",
            category: "Performance",
            issue: "Inefficient loop structure",
            line: "Nested loops could be optimized",
            recommendation: "Consider using hash map for O(1) lookup instead of nested iteration"
          },
          {
            severity: "Low",
            category: "Best Practices",
            issue: "Missing error handling",
            line: "No try-catch blocks for async operations",
            recommendation: "Add proper error handling and logging for production reliability"
          }
        ],
        positive_aspects: [
          "Well-structured and modular code organization",
          "Clear variable naming and good readability",
          "Comprehensive inline comments"
        ],
        suggestions: [
          "Add input validation for all user-provided data",
          "Implement unit tests for critical functions",
          "Consider adding type hints for better code maintainability"
        ]
      }
    },
    'meeting-notes': {
      demo_mode: true,
      output: {
        summary: "Q4 planning meeting covering budget allocation, resource planning, and project priorities for next quarter",
        attendees: ["John Smith", "Sarah Johnson", "Mike Chen", "Emily Davis"],
        date: new Date().toLocaleDateString(),
        decisions_made: [
          "Approved $150K budget for new feature development",
          "Decided to hire 2 additional engineers in Q1",
          "Selected Project Phoenix as top priority for Q4"
        ],
        action_items: [
          {
            task: "Finalize Q4 budget breakdown",
            owner: "John Smith",
            deadline: "Nov 30, 2025",
            status: "Pending"
          },
          {
            task: "Post job listings for engineering positions",
            owner: "Sarah Johnson",
            deadline: "Dec 5, 2025",
            status: "Pending"
          },
          {
            task: "Create Project Phoenix kickoff presentation",
            owner: "Mike Chen",
            deadline: "Dec 1, 2025",
            status: "Pending"
          }
        ],
        key_discussion_points: [
          "Q3 performance exceeded targets by 12%",
          "Customer feedback indicates strong demand for mobile features",
          "Team capacity analysis shows need for additional resources",
          "Competitive landscape analysis presented"
        ],
        next_meeting: "December 15, 2025"
      }
    }
  };

  return results[agentId] || {
    demo_mode: true,
    output: { result: "Agent executed successfully in demo mode" }
  };
}
