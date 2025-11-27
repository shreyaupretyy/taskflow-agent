export const NODE_TYPES = {
  trigger: {
    label: 'Trigger',
    category: 'inputs',
    description: 'Start the workflow',
    color: '#10b981',
  },
  researcher: {
    label: 'Researcher Agent',
    category: 'agents',
    description: 'Research and gather information',
    color: '#3b82f6',
  },
  extractor: {
    label: 'Extractor Agent',
    category: 'agents',
    description: 'Extract structured data',
    color: '#8b5cf6',
  },
  writer: {
    label: 'Writer Agent',
    category: 'agents',
    description: 'Generate written content',
    color: '#ec4899',
  },
  analyzer: {
    label: 'Analyzer Agent',
    category: 'agents',
    description: 'Analyze data and provide insights',
    color: '#f59e0b',
  },
  http_request: {
    label: 'HTTP Request',
    category: 'actions',
    description: 'Make HTTP API calls',
    color: '#06b6d4',
  },
  email: {
    label: 'Send Email',
    category: 'actions',
    description: 'Send email notifications',
    color: '#14b8a6',
  },
  database: {
    label: 'Database',
    category: 'actions',
    description: 'Query or update database',
    color: '#6366f1',
  },
  condition: {
    label: 'Condition',
    category: 'logic',
    description: 'Conditional branching',
    color: '#84cc16',
  },
  transform: {
    label: 'Transform',
    category: 'logic',
    description: 'Transform data',
    color: '#a855f7',
  },
};

export const NODE_CATEGORIES = [
  { id: 'inputs', label: 'Inputs', icon: 'play' },
  { id: 'agents', label: 'AI Agents', icon: 'brain' },
  { id: 'actions', label: 'Actions', icon: 'zap' },
  { id: 'logic', label: 'Logic', icon: 'git-branch' },
];
