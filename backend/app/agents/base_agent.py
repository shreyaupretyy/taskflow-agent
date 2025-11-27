from typing import Dict, Any, List, Optional
from langchain.schema import HumanMessage, SystemMessage
from langchain_community.llms import Ollama
from langchain.memory import ConversationBufferMemory
from app.core.config import settings
import json


class BaseAgent:
    """Base class for all AI agents."""
    
    def __init__(self, name: str, model: str = None):
        self.name = name
        self.model = model or settings.DEFAULT_MODEL
        print(f"🔍 Initializing {name} agent with model: {self.model}")
        print(f"🔍 Ollama base URL: {settings.OLLAMA_BASE_URL}")
        self.llm = Ollama(
            model=self.model,
            base_url=settings.OLLAMA_BASE_URL,
            temperature=settings.TEMPERATURE,
        )
        self.memory = ConversationBufferMemory()
        
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent with given input."""
        raise NotImplementedError("Subclasses must implement execute method")
    
    def _format_prompt(self, template: str, **kwargs) -> str:
        """Format a prompt template with variables."""
        return template.format(**kwargs)
    
    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON from LLM response."""
        try:
            # Remove any leading/trailing text before JSON
            response = response.strip()
            
            # Try to find JSON in the response
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                json_str = response[start:end].strip()
            elif "```" in response:
                start = response.find("```") + 3
                end = response.find("```", start)
                json_str = response[start:end].strip()
            elif "{" in response and "}" in response:
                # Find the first { and last }
                start = response.find("{")
                end = response.rfind("}") + 1
                json_str = response[start:end].strip()
            else:
                json_str = response.strip()
            
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            # If parsing fails, try to extract JSON from text
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except:
                    pass
            # Last resort: return structured error
            return {"error": "Failed to parse response", "raw_response": response}


class ResearcherAgent(BaseAgent):
    """Agent that researches and gathers information."""
    
    def __init__(self):
        super().__init__("Researcher")
        self.system_prompt = """You are a research agent specialized in gathering and analyzing information.
Your task is to research the given topic thoroughly and provide comprehensive, factual information.
Always cite sources when possible and organize information logically.
Respond in JSON format with the following structure:
{
    "summary": "Brief summary of findings",
    "key_points": ["point 1", "point 2", ...],
    "detailed_findings": "Detailed research findings",
    "sources": ["source 1", "source 2", ...],
    "confidence": 0.0-1.0
}"""
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Research a topic and return findings."""
        query = input_data.get("query", "")
        context = input_data.get("context", "")
        
        prompt = f"""{self.system_prompt}

Research Query: {query}
Additional Context: {context}

Provide your research findings in the JSON format specified above."""

        response = self.llm.invoke(prompt)
        result = self._parse_json_response(response)
        
        return {
            "agent": self.name,
            "status": "success",
            "data": result
        }


class ExtractorAgent(BaseAgent):
    """Agent that extracts structured data from unstructured text."""
    
    def __init__(self):
        super().__init__("Extractor")
        self.system_prompt = """You are an email analysis agent. Analyze the email and provide a comprehensive, well-formatted summary.

Format your response as follows:

EMAIL ANALYSIS REPORT

SUMMARY
[Provide 2-3 sentence summary of the email's main points]

SENDER: [sender email or name]
SUBJECT: [email subject if mentioned]
PRIORITY: [High/Medium/Low]
CATEGORY: [Action Required/Information/Request/Update]
SENTIMENT: [Positive/Neutral/Negative]
DEADLINE: [any mentioned deadline or Not specified]

ACTION ITEMS
[List each action item with a bullet point]

KEY POINTS
[List each key point with a bullet point]

Be clear, concise, and professional."""
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract structured data from text."""
        text = input_data.get("text", "")
        
        prompt = f"""{self.system_prompt}

Email text to analyze:
{text}"""

        response = self.llm.invoke(prompt)
        
        return {
            "agent": self.name,
            "status": "success",
            "report": response
        }


class WriterAgent(BaseAgent):
    """Agent that writes and generates content."""
    
    def __init__(self):
        super().__init__("Writer")
        self.system_prompt = """You are a professional content writer. Create engaging, well-structured content based on the given task.

Format your response as follows:

CONTENT GENERATION REPORT

TITLE
[Create an engaging title]

CONTENT
[Write the full content with proper paragraphs, structure, and formatting]

METADATA
Word Count: [approximate word count]
Tone: Professional
Format: [article/blog/email/etc]

KEY TAKEAWAYS
• [Key point 1]
• [Key point 2]
• [Key point 3]

Write in a clear, engaging, and professional style."""
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate written content."""
        task = input_data.get("task", "")
        
        prompt = f"""{self.system_prompt}

Writing Task: {task}"""

        response = self.llm.invoke(prompt)
        
        return {
            "agent": self.name,
            "status": "success",
            "report": response
        }


class AnalyzerAgent(BaseAgent):
    """Agent that analyzes data and provides insights."""
    
    def __init__(self):
        super().__init__("Analyzer")
        self.system_prompt = """You are an expert code reviewer. Review the code and provide the corrected version with a brief summary.

Format your response as follows:

CODE REVIEW

SUMMARY
[1-2 sentence summary of main issues fixed]

CORRECTED CODE
[Provide the complete corrected code with all fixes applied]

CHANGES MADE
• [Brief description of fix 1]
• [Brief description of fix 2]
• [Brief description of fix 3]

Be concise and focus on providing working, corrected code."""
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze data and return insights."""
        data = input_data.get("data", "")
        
        prompt = f"""{self.system_prompt}

Content to analyze:
{data}"""

        response = self.llm.invoke(prompt)
        
        return {
            "agent": self.name,
            "status": "success",
            "report": response
        }


# Agent factory
def create_agent(agent_type: str) -> BaseAgent:
    """Create an agent instance based on type."""
    agents = {
        "researcher": ResearcherAgent,
        "extractor": ExtractorAgent,
        "writer": WriterAgent,
        "analyzer": AnalyzerAgent,
    }
    
    agent_class = agents.get(agent_type.lower())
    if not agent_class:
        raise ValueError(f"Unknown agent type: {agent_type}")
    
    return agent_class()
