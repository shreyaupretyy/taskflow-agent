'use client';

import AgentInterface from '@/components/AgentInterface';

export default function DataAnalyzerPage() {
  return (
    <AgentInterface
      agentId="data-analyzer"
      agentName="Data Analyzer"
      agentIcon="📊"
      agentDescription="Extract insights, identify patterns, and generate actionable reports from your data with confidence scores"
      placeholder="Paste your data for analysis...

Example:
Q3 2025 Sales Data:
Product A: $150,000 (up 15% from Q2)
Product B: $89,000 (down 5% from Q2)
Product C: $210,000 (up 23% from Q2)

Customer Acquisition: 1,245 new customers
Churn Rate: 3.2%
Average Order Value: $185
Customer Satisfaction: 4.2/5.0

Regional Performance:
North America: $280,000
Europe: $120,000
Asia Pacific: $49,000

Marketing ROI: 3.8x"
      exampleInput={`Q3 2025 Sales Data:
Product A: $150,000 (up 15% from Q2)
Product B: $89,000 (down 5% from Q2)
Product C: $210,000 (up 23% from Q2)

Customer Acquisition: 1,245 new customers
Churn Rate: 3.2%
Average Order Value: $185
Customer Satisfaction: 4.2/5.0

Regional Performance:
North America: $280,000
Europe: $120,000
Asia Pacific: $49,000

Marketing ROI: 3.8x`}
      color="#22c55e"
    />
  );
}
