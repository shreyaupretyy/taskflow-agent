"""
Tests for AI agents
"""
import pytest
from app.agents.base_agent import create_agent, ExtractorAgent, WriterAgent, AnalyzerAgent


class TestAgentCreation:
    """Test agent factory and initialization."""
    
    def test_create_extractor_agent(self):
        """Test creating an extractor agent."""
        agent = create_agent("extractor")
        assert isinstance(agent, ExtractorAgent)
        assert agent.name == "Extractor"
    
    def test_create_writer_agent(self):
        """Test creating a writer agent."""
        agent = create_agent("writer")
        assert isinstance(agent, WriterAgent)
        assert agent.name == "Writer"
    
    def test_create_analyzer_agent(self):
        """Test creating an analyzer agent."""
        agent = create_agent("analyzer")
        assert isinstance(agent, AnalyzerAgent)
        assert agent.name == "Analyzer"
    
    def test_invalid_agent_type(self):
        """Test creating an invalid agent type raises error."""
        with pytest.raises(ValueError):
            create_agent("invalid_agent")


class TestAgentExecution:
    """Test agent execution logic."""
    
    @pytest.mark.asyncio
    async def test_extractor_agent_execution(self):
        """Test extractor agent executes without errors."""
        agent = create_agent("extractor")
        result = await agent.execute({
            "text": "Test email content for analysis"
        })
        
        assert result is not None
        assert "agent" in result
        assert result["agent"] == "Extractor"
        assert "status" in result
        assert result["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_writer_agent_execution(self):
        """Test writer agent executes without errors."""
        agent = create_agent("writer")
        result = await agent.execute({
            "task": "Write a short paragraph about AI"
        })
        
        assert result is not None
        assert "agent" in result
        assert result["agent"] == "Writer"
        assert "status" in result
    
    @pytest.mark.asyncio
    async def test_analyzer_agent_execution(self):
        """Test analyzer agent executes without errors."""
        agent = create_agent("analyzer")
        result = await agent.execute({
            "data": "Sample data for analysis"
        })
        
        assert result is not None
        assert "agent" in result
        assert result["agent"] == "Analyzer"


class TestAgentPrompts:
    """Test agent system prompts are properly configured."""
    
    def test_extractor_has_system_prompt(self):
        """Test extractor agent has a system prompt."""
        agent = create_agent("extractor")
        assert hasattr(agent, 'system_prompt')
        assert len(agent.system_prompt) > 0
        assert "email" in agent.system_prompt.lower() or "extract" in agent.system_prompt.lower()
    
    def test_writer_has_system_prompt(self):
        """Test writer agent has a system prompt."""
        agent = create_agent("writer")
        assert hasattr(agent, 'system_prompt')
        assert len(agent.system_prompt) > 0
        assert "content" in agent.system_prompt.lower() or "write" in agent.system_prompt.lower()
    
    def test_analyzer_has_system_prompt(self):
        """Test analyzer agent has a system prompt."""
        agent = create_agent("analyzer")
        assert hasattr(agent, 'system_prompt')
        assert len(agent.system_prompt) > 0
        assert "code" in agent.system_prompt.lower() or "review" in agent.system_prompt.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
