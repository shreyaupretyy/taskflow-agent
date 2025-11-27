'use client';

import AgentInterface from '@/components/AgentInterface';

export default function EmailSummarizerPage() {
  return (
    <AgentInterface
      agentId="email-summarizer"
      agentName="Email Summarizer"
      agentIcon=""
      agentDescription="Automatically analyze and summarize emails with priority detection, sentiment analysis, and action item extraction"
      placeholder="Paste your email content here...

Example:
From: john.doe@company.com
Subject: Q4 Budget Review - Action Required
Date: Nov 27, 2025

Hi Team,

I hope this email finds you well. I wanted to reach out regarding our Q4 budget review which is coming up next week. We need to finalize the numbers before our board meeting on Friday.

Could you please review the attached spreadsheet and provide your department's input by Wednesday EOD? This is critical for our planning cycle.

Also, please note that we've identified some cost-saving opportunities in the IT infrastructure budget that we should discuss.

Looking forward to your feedback.

Best regards,
John"
      exampleInput={`From: john.doe@company.com
Subject: Q4 Budget Review - Action Required
Date: Nov 27, 2025

Hi Team,

I hope this email finds you well. I wanted to reach out regarding our Q4 budget review which is coming up next week. We need to finalize the numbers before our board meeting on Friday.

Could you please review the attached spreadsheet and provide your department's input by Wednesday EOD? This is critical for our planning cycle.

Also, please note that we've identified some cost-saving opportunities in the IT infrastructure budget that we should discuss.

Looking forward to your feedback.

Best regards,
John`}
      color="#3b82f6"
    />
  );
}
