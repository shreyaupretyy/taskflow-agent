'use client';

import AgentInterface from '@/components/AgentInterface';

export default function ContentGeneratorPage() {
  return (
    <AgentInterface
      agentId="content-generator"
      agentName="Content Generator"
      agentIcon="✍️"
      agentDescription="Research topics and write comprehensive articles, blog posts, and marketing content with proper structure and engaging style"
      placeholder="Enter your content topic or brief...

Example:
Topic: The Impact of Remote Work on Employee Productivity
Target Audience: Business managers and HR professionals
Tone: Professional and informative
Length: 500-700 words
Key Points to Cover:
- Benefits of remote work
- Challenges and solutions
- Best practices for remote teams
- Future trends"
      exampleInput={`Topic: The Impact of Remote Work on Employee Productivity
Target Audience: Business managers and HR professionals
Tone: Professional and informative
Length: 500-700 words
Key Points to Cover:
- Benefits of remote work
- Challenges and solutions
- Best practices for remote teams
- Future trends`}
      color="#a855f7"
    />
  );
}
