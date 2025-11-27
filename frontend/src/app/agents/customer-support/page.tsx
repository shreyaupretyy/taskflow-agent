'use client';

import AgentInterface from '@/components/AgentInterface';

export default function CustomerSupportPage() {
  return (
    <AgentInterface
      agentId="customer-support"
      agentName="Customer Support Assistant"
      agentIcon="💬"
      agentDescription="Analyze customer inquiries and generate professional, empathetic support responses with clear solutions"
      placeholder="Paste customer inquiry here...

Example:
Customer Name: Jane Smith
Issue: Unable to login to account
Priority: High

Message:
Hi, I've been trying to login to my account for the past hour but I keep getting an 'invalid credentials' error. I'm 100% sure my password is correct because I use a password manager. This is really frustrating because I need to access my dashboard for an important meeting in 30 minutes. Can someone please help me ASAP? My username is janesmith@email.com."
      exampleInput={`Customer Name: Jane Smith
Issue: Unable to login to account
Priority: High

Message:
Hi, I've been trying to login to my account for the past hour but I keep getting an 'invalid credentials' error. I'm 100% sure my password is correct because I use a password manager. This is really frustrating because I need to access my dashboard for an important meeting in 30 minutes. Can someone please help me ASAP? My username is janesmith@email.com.`}
      color="#f97316"
    />
  );
}
