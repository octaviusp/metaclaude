"""
Claude Code Integration for Agent Creation

This module provides integration with Claude Code to let Claude itself
suggest and create specialized agents based on project analysis.
Instead of using deterministic rules, Claude analyzes the project
and creates custom agents with its own reasoning and knowledge.
"""

import json
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

from ..utils.logging import get_logger
from ..utils.errors import MetaClaudeAgentError
from .parser import AgentConfig

logger = get_logger(__name__)


@dataclass
class ClaudeAgentSuggestion:
    """Agent suggestion from Claude Code."""
    name: str
    role: str
    description: str
    expertise_areas: List[str]
    tools: List[str]
    system_prompt: str
    reasoning: str
    priority: int = 1


@dataclass
class ClaudeAgentResponse:
    """Response from Claude Code agent creation."""
    suggested_agents: List[ClaudeAgentSuggestion]
    coordination_strategy: str
    execution_order: List[str]
    reasoning: str
    estimated_duration: str
    success_criteria: List[str]


class ClaudeCodeAgentCreator:
    """
    Agent creator that leverages Claude Code's intelligence to suggest
    and create specialized agents for projects.
    """
    
    def __init__(self, docker_manager=None):
        """Initialize Claude Code agent creator.
        
        Args:
            docker_manager: Docker manager for running Claude Code
        """
        self.docker_manager = docker_manager
        self.agent_creation_prompt = self._create_agent_creation_prompt()
        
    def _create_agent_creation_prompt(self) -> str:
        """Create the prompt for Claude Code to suggest agents."""
        return """
You are Claude Code, an AI assistant specialized in software development. You have been asked to analyze a project idea and suggest specialized sub-agents that would be optimal for completing this project.

Your task is to:
1. Analyze the project requirements deeply
2. Suggest 1-4 specialized sub-agents that would work together optimally
3. Design each agent with specific expertise, tools, and system prompts
4. Create a coordination strategy for how these agents should work together

For each suggested agent, provide:
- **name**: A descriptive name (e.g., "FrontendArchitect", "DatabaseDesigner")
- **role**: Their primary role in the project
- **description**: What they specialize in (2-3 sentences)
- **expertise_areas**: List of their main expertise areas
- **tools**: List of tools they should have access to from: [Bash, Read, Write, Edit, MultiEdit, Glob, Grep, WebFetch, TodoWrite, WebSearch]
- **system_prompt**: A detailed system prompt that defines their personality, expertise, and approach
- **reasoning**: Why this agent is needed for this specific project
- **priority**: Execution priority (1=highest, 4=lowest)

Also provide:
- **coordination_strategy**: How the agents should work together (parallel, sequential, hybrid)
- **execution_order**: The order in which agents should execute
- **reasoning**: Your overall reasoning for this agent architecture
- **estimated_duration**: Realistic time estimate for completion
- **success_criteria**: How to measure if the agents succeeded

Project Details:
IDEA: {idea}

Please respond with a JSON object in this exact format:
{{
  "suggested_agents": [
    {{
      "name": "AgentName",
      "role": "Primary role",
      "description": "What this agent does",
      "expertise_areas": ["area1", "area2"],
      "tools": ["Bash", "Read", "Write"],
      "system_prompt": "Detailed system prompt for this agent...",
      "reasoning": "Why this agent is needed",
      "priority": 1
    }}
  ],
  "coordination_strategy": "sequential|parallel|hybrid",
  "execution_order": ["Agent1", "Agent2"],
  "reasoning": "Overall reasoning for this architecture",
  "estimated_duration": "2-4 hours",
  "success_criteria": ["criteria1", "criteria2"]
}}

Be creative and leverage your knowledge to suggest agents that would actually be optimal for this specific project. Consider the project's complexity, technology stack, and requirements.
"""

    async def create_agents_with_claude(
        self, 
        idea: str, 
        container_id: str,
        workspace_path: Path
    ) -> ClaudeAgentResponse:
        """
        Use Claude Code to suggest and create specialized agents.
        
        Args:
            idea: Project idea description
            container_id: Docker container ID where Claude Code is running
            workspace_path: Path to workspace directory
            
        Returns:
            Claude's agent suggestions and coordination strategy
            
        Raises:
            MetaClaudeAgentError: If agent creation fails
        """
        logger.info(f"Asking Claude Code to suggest agents for: {idea[:50]}...")
        
        try:
            # Create the prompt with the specific idea
            prompt = self.agent_creation_prompt.format(idea=idea)
            
            # Create a temporary file with the prompt
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
                f.write(f"# Agent Creation Task\n\n{prompt}")
                prompt_file = f.name
            
            try:
                # Copy prompt file to container
                prompt_container_path = "/workspace/agent_creation_prompt.md"
                # Get the actual container object from Docker manager
                container = self.docker_manager.client.containers.get(container_id)
                self.docker_manager.copy_to_container(
                    container, 
                    Path(prompt_file), 
                    "/workspace"
                )
                
                # Execute Claude Code to analyze and suggest agents
                claude_command = "claude-code --dangerously-skip-permissions " + prompt_container_path
                
                logger.info("Executing Claude Code for agent creation...")
                exit_code, output = self.docker_manager.execute_command(
                    container, 
                    claude_command,
                    workdir="/workspace"
                )
                
                if exit_code != 0:
                    raise MetaClaudeAgentError(
                        f"Claude Code agent creation failed with exit code {exit_code}: {output}",
                        recovery_hint="Check if Claude Code is properly installed in container"
                    )
                
                # Parse Claude's response
                response = self._parse_claude_response(output)
                
                logger.info(f"Claude suggested {len(response.suggested_agents)} agents: "
                          f"{[a.name for a in response.suggested_agents]}")
                
                return response
                
            finally:
                # Cleanup temp file
                Path(prompt_file).unlink(missing_ok=True)
                
        except Exception as e:
            logger.error(f"Claude Code agent creation failed: {e}")
            # Return fallback single agent
            return self._create_fallback_response(idea)
    
    def _parse_claude_response(self, claude_output: str) -> ClaudeAgentResponse:
        """Parse Claude Code's JSON response into structured data.
        
        Args:
            claude_output: Raw output from Claude Code
            
        Returns:
            Parsed agent response
            
        Raises:
            MetaClaudeAgentError: If parsing fails
        """
        try:
            # Extract JSON from Claude's output (it might have other text)
            json_start = claude_output.find('{')
            json_end = claude_output.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in Claude's response")
            
            json_str = claude_output[json_start:json_end]
            data = json.loads(json_str)
            
            # Convert to structured objects
            agents = [
                ClaudeAgentSuggestion(**agent_data) 
                for agent_data in data["suggested_agents"]
            ]
            
            return ClaudeAgentResponse(
                suggested_agents=agents,
                coordination_strategy=data["coordination_strategy"],
                execution_order=data["execution_order"],
                reasoning=data["reasoning"],
                estimated_duration=data["estimated_duration"],
                success_criteria=data["success_criteria"]
            )
            
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            logger.error(f"Failed to parse Claude response: {e}")
            logger.debug(f"Claude output was: {claude_output}")
            raise MetaClaudeAgentError(
                f"Failed to parse Claude's agent suggestions: {e}",
                recovery_hint="Claude may not have responded in the expected JSON format"
            )
    
    def _create_fallback_response(self, idea: str) -> ClaudeAgentResponse:
        """Create a fallback response if Claude Code fails.
        
        Args:
            idea: Project idea
            
        Returns:
            Simple fallback agent response
        """
        logger.warning("Creating fallback agent due to Claude Code failure")
        
        fallback_agent = ClaudeAgentSuggestion(
            name="GeneralDeveloper",
            role="Full-stack developer",
            description="A versatile developer capable of handling various aspects of software development",
            expertise_areas=["general development", "problem solving"],
            tools=["Bash", "Read", "Write", "Edit", "MultiEdit", "Glob", "Grep", "TodoWrite"],
            system_prompt=f"""You are a skilled software developer working on: {idea}

Your approach:
1. Analyze the requirements carefully
2. Break down the task into manageable steps
3. Implement clean, well-documented code
4. Test your implementation
5. Provide clear documentation

Focus on delivering a working solution that meets the user's needs.""",
            reasoning="Fallback general-purpose agent when specialized agent creation fails",
            priority=1
        )
        
        return ClaudeAgentResponse(
            suggested_agents=[fallback_agent],
            coordination_strategy="single_agent",
            execution_order=["GeneralDeveloper"],
            reasoning="Fallback to single general-purpose agent due to specialized agent creation failure",
            estimated_duration="2-4 hours",
            success_criteria=["Working implementation", "Clear documentation"]
        )
    
    def convert_to_agent_configs(self, response: ClaudeAgentResponse) -> List[AgentConfig]:
        """Convert Claude's suggestions to AgentConfig objects.
        
        Args:
            response: Claude's agent response
            
        Returns:
            List of AgentConfig objects
        """
        configs = []
        
        for agent in response.suggested_agents:
            # Create agent configuration
            config = AgentConfig(
                name=agent.name,
                description=agent.description,
                tools=agent.tools,
                parallelism=4,  # Default parallelism
                patterns=["agentic", "claude-created"],  # Mark as Claude-created
                system_prompt=agent.system_prompt,
                expertise_areas=agent.expertise_areas,
                priority=agent.priority,
                role=agent.role
            )
            configs.append(config)
        
        return configs