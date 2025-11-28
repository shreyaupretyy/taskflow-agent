"""Workflow examples."""

RESEARCH_WORKFLOW = {
    "name": "Research and Summarize",
    "description": "Research a topic and generate a summary",
    "nodes": [
        {
            "id": "trigger",
            "type": "trigger",
            "data": {"name": "Manual Trigger", "config": {}},
            "position": {"x": 100, "y": 100},
        },
        {
            "id": "research",
            "type": "ai_agent",
            "data": {
                "name": "Research Agent",
                "config": {"agent_type": "researcher", "query": "{{topic}}", "max_results": 5},
            },
            "position": {"x": 300, "y": 100},
        },
        {
            "id": "summarize",
            "type": "ai_agent",
            "data": {
                "name": "Writer Agent",
                "config": {
                    "agent_type": "writer",
                    "content": "{{research.result}}",
                    "task": "summarize",
                },
            },
            "position": {"x": 500, "y": 100},
        },
    ],
    "edges": [
        {"id": "e1", "source": "trigger", "target": "research"},
        {"id": "e2", "source": "research", "target": "summarize"},
    ],
}

WEB_SCRAPING_WORKFLOW = {
    "name": "Web Scraping and Analysis",
    "description": "Scrape website data and analyze it",
    "nodes": [
        {
            "id": "trigger",
            "type": "trigger",
            "data": {"name": "Manual Trigger", "config": {}},
            "position": {"x": 100, "y": 100},
        },
        {
            "id": "scrape",
            "type": "http_request",
            "data": {"name": "Scrape Website", "config": {"method": "GET", "url": "{{url}}"}},
            "position": {"x": 300, "y": 100},
        },
        {
            "id": "extract",
            "type": "ai_agent",
            "data": {
                "name": "Extractor Agent",
                "config": {
                    "agent_type": "extractor",
                    "content": "{{scrape.body}}",
                    "fields": ["title", "description", "author"],
                },
            },
            "position": {"x": 500, "y": 100},
        },
        {
            "id": "analyze",
            "type": "ai_agent",
            "data": {
                "name": "Analyzer Agent",
                "config": {
                    "agent_type": "analyzer",
                    "data": "{{extract.result}}",
                    "analysis_type": "sentiment",
                },
            },
            "position": {"x": 700, "y": 100},
        },
    ],
    "edges": [
        {"id": "e1", "source": "trigger", "target": "scrape"},
        {"id": "e2", "source": "scrape", "target": "extract"},
        {"id": "e3", "source": "extract", "target": "analyze"},
    ],
}

CONDITIONAL_WORKFLOW = {
    "name": "Conditional Processing",
    "description": "Process data based on conditions",
    "nodes": [
        {
            "id": "trigger",
            "type": "trigger",
            "data": {"name": "Manual Trigger", "config": {}},
            "position": {"x": 100, "y": 100},
        },
        {
            "id": "condition",
            "type": "condition",
            "data": {
                "name": "Check Value",
                "config": {"left": "{{value}}", "operator": ">", "right": 100},
            },
            "position": {"x": 300, "y": 100},
        },
        {
            "id": "high_value",
            "type": "ai_agent",
            "data": {
                "name": "High Value Handler",
                "config": {"agent_type": "writer", "content": "High value detected: {{value}}"},
            },
            "position": {"x": 500, "y": 50},
        },
        {
            "id": "low_value",
            "type": "ai_agent",
            "data": {
                "name": "Low Value Handler",
                "config": {"agent_type": "writer", "content": "Low value detected: {{value}}"},
            },
            "position": {"x": 500, "y": 150},
        },
    ],
    "edges": [
        {"id": "e1", "source": "trigger", "target": "condition"},
        {"id": "e2", "source": "condition", "target": "high_value", "sourceHandle": "true"},
        {"id": "e3", "source": "condition", "target": "low_value", "sourceHandle": "false"},
    ],
}
