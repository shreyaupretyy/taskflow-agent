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
            # Try to find JSON in markdown code blocks
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                json_str = response[start:end].strip()
            elif "```" in response:
                start = response.find("```") + 3
                end = response.find("```", start)
                json_str = response[start:end].strip()
            else:
                json_str = response.strip()
            
            return json.loads(json_str)
        except json.JSONDecodeError:
            # If parsing fails, return the raw response
            return {"result": response, "raw": True}


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
        self.system_prompt = """You are a data extraction agent specialized in extracting structured information from text.
Your task is to identify and extract relevant data points according to the schema provided.
Be precise and only extract information that is explicitly present in the text.
Respond in JSON format matching the requested schema."""
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract structured data from text."""
        text = input_data.get("text", "")
        schema = input_data.get("schema", {})
        fields = input_data.get("fields", [])
        
        schema_str = json.dumps(schema) if schema else f"Fields to extract: {', '.join(fields)}"
        
        prompt = f"""{self.system_prompt}

Text to extract from:
{text}

Extraction Schema:
{schema_str}

Extract the data and return it in JSON format matching the schema."""

        response = self.llm.invoke(prompt)
        result = self._parse_json_response(response)
        
        return {
            "agent": self.name,
            "status": "success",
            "data": result
        }


class WriterAgent(BaseAgent):
    """Agent that writes and generates content."""
    
    def __init__(self):
        super().__init__("Writer")
        self.system_prompt = """You are a professional writing agent specialized in creating high-quality content.
Your task is to write clear, engaging, and well-structured content based on the given requirements.
Adapt your writing style to match the specified tone and format.
Provide your output in the requested format."""
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate written content."""
        task = input_data.get("task", "")
        content_type = input_data.get("content_type", "article")
        tone = input_data.get("tone", "professional")
        length = input_data.get("length", "medium")
        context = input_data.get("context", "")
        
        prompt = f"""{self.system_prompt}

Writing Task: {task}
Content Type: {content_type}
Tone: {tone}
Length: {length}
Context: {context}

Write the content and return it in JSON format:
{{
    "title": "Content title",
    "content": "The written content",
    "word_count": number,
    "summary": "Brief summary"
}}"""

        response = self.llm.invoke(prompt)
        result = self._parse_json_response(response)
        
        return {
            "agent": self.name,
            "status": "success",
            "data": result
        }


class AnalyzerAgent(BaseAgent):
    """Agent that analyzes data and provides insights."""
    
    def __init__(self):
        super().__init__("Analyzer")
        self.system_prompt = """You are a data analysis agent specialized in analyzing information and providing insights.
Your task is to examine the provided data, identify patterns, trends, and anomalies.
Provide actionable insights and recommendations based on your analysis.
Respond in JSON format with structured analysis results."""
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze data and return insights."""
        data = input_data.get("data", "")
        analysis_type = input_data.get("analysis_type", "general")
        focus_areas = input_data.get("focus_areas", [])
        
        focus_str = ", ".join(focus_areas) if focus_areas else "all aspects"
        
        prompt = f"""{self.system_prompt}

Data to analyze:
{json.dumps(data) if isinstance(data, dict) else str(data)}

Analysis Type: {analysis_type}
Focus Areas: {focus_str}

Provide your analysis in JSON format:
{{
    "summary": "Overall analysis summary",
    "insights": ["insight 1", "insight 2", ...],
    "patterns": ["pattern 1", "pattern 2", ...],
    "recommendations": ["recommendation 1", "recommendation 2", ...],
    "confidence": 0.0-1.0
}}"""

        response = self.llm.invoke(prompt)
        result = self._parse_json_response(response)
        
        return {
            "agent": self.name,
            "status": "success",
            "data": result
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
