'use client';

import AgentInterface from '@/components/AgentInterface';

export default function CodeReviewerPage() {
  return (
    <AgentInterface
      agentId="code-reviewer"
      agentName="Code Reviewer"
      agentIcon="👨‍💻"
      agentDescription="Analyze code for bugs, security vulnerabilities, performance issues, and suggest improvements with best practices"
      placeholder="Paste your code here for review...

Example:
def process_user_data(user_input):
    query = 'SELECT * FROM users WHERE username = ' + user_input
    result = database.execute(query)
    
    total = 0
    for item in result:
        for price in item.prices:
            total += price
    
    return total"
      exampleInput={`def process_user_data(user_input):
    query = 'SELECT * FROM users WHERE username = ' + user_input
    result = database.execute(query)
    
    total = 0
    for item in result:
        for price in item.prices:
            total += price
    
    return total`}
      color="#ef4444"
    />
  );
}
