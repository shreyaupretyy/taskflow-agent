'use client';

import AgentInterface from '@/components/AgentInterface';

export default function MeetingNotesPage() {
  return (
    <AgentInterface
      agentId="meeting-notes"
      agentName="Meeting Notes Generator"
      agentIcon="📝"
      agentDescription="Convert meeting transcripts into structured notes with attendees, decisions, action items, and next steps"
      placeholder="Paste meeting transcript or notes here...

Example:
Meeting: Q4 Planning Session
Date: November 27, 2025
Attendees: John (CEO), Sarah (CFO), Mike (CTO), Emily (CMO)

John opened the meeting by reviewing Q3 performance, which exceeded targets by 12%. Sarah presented the Q4 budget proposal of $150K for new feature development.

Mike discussed technical roadmap and mentioned need for 2 additional engineers. Emily shared customer feedback indicating strong demand for mobile features.

After discussion, team agreed to:
- Approve the budget
- Post job listings next week
- Make Project Phoenix the top priority

Action items:
- John will finalize budget breakdown by Nov 30
- Sarah will post job listings by Dec 5
- Mike will create Phoenix kickoff presentation by Dec 1

Next meeting scheduled for Dec 15."
      exampleInput={`Meeting: Q4 Planning Session
Date: November 27, 2025
Attendees: John (CEO), Sarah (CFO), Mike (CTO), Emily (CMO)

John opened the meeting by reviewing Q3 performance, which exceeded targets by 12%. Sarah presented the Q4 budget proposal of $150K for new feature development.

Mike discussed technical roadmap and mentioned need for 2 additional engineers. Emily shared customer feedback indicating strong demand for mobile features.

After discussion, team agreed to:
- Approve the budget
- Post job listings next week
- Make Project Phoenix the top priority

Action items:
- John will finalize budget breakdown by Nov 30
- Sarah will post job listings by Dec 5
- Mike will create Phoenix kickoff presentation by Dec 1

Next meeting scheduled for Dec 15.`}
      color="#6366f1"
    />
  );
}
