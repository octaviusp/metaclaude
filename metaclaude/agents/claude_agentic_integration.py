"""
Claude Code Agentic Integration - Natural Approach

This module provides integration between MetaClaude and Claude Code for
intelligent agent creation. It uses Claude Code's natural file creation
abilities to let Claude suggest and create optimal agents.
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

from .natural_claude_creator import NaturalClaudeAgentCreator, ClaudeCreatedAgent
from .parser import AgentConfig
from ..utils.logging import get_logger
from ..utils.errors import MetaClaudeAgentError

logger = get_logger(__name__)


class ClaudeAgenticIntegration:
    """
    Integration layer that uses Claude Code to create agents naturally.
    
    This approach lets Claude Code work naturally by:
    1. Giving Claude a natural prompt to analyze the project
    2. Asking Claude to create individual .md files for specialized agents
    3. Parsing the created files to extract agent information
    4. Converting to internal agent format
    """
    
    def __init__(self, templates_dir: Path, docker_manager=None):
        """Initialize Claude agentic integration.
        
        Args:
            templates_dir: Path to templates directory
            docker_manager: Docker manager for running Claude Code
        """
        self.templates_dir = templates_dir
        self.docker_manager = docker_manager
        self.claude_creator = NaturalClaudeAgentCreator(docker_manager)
        
        # State tracking
        self.last_created_agents: List[ClaudeCreatedAgent] = []
        self.execution_context: Dict[str, Any] = {}
        
        logger.info("ClaudeAgenticIntegration initialized")
    
    async def create_agentic_agents(
        self,
        idea: str,
        model: str = "opus",
        force_agents: Optional[List[str]] = None,
        custom_template_vars: Optional[Dict[str, Any]] = None,
        container_id: Optional[str] = None,
        workspace_path: Optional[Path] = None
    ) -> Tuple[List[AgentConfig], Dict[str, Any]]:
        """
        Create agents using Claude Code's natural intelligence.
        
        Args:
            idea: Project idea description
            model: Claude model to use
            force_agents: Ignored - Claude decides the agents
            custom_template_vars: Custom template variables
            container_id: Docker container ID where Claude Code runs
            workspace_path: Path to workspace directory
            
        Returns:
            Tuple of (agent configs, agentic metadata)
            
        Raises:
            MetaClaudeAgentError: If agent creation fails
        """
        logger.info("Creating agentic agents using Claude Code's natural intelligence")
        
        if not container_id or not workspace_path:
            raise MetaClaudeAgentError(
                "Container ID and workspace path required for Claude agent creation",
                recovery_hint="Ensure Docker container is running before agent creation"
            )
        
        try:
            # Let Claude Code naturally create agents
            logger.info("Asking Claude Code to naturally analyze project and create agents...")
            claude_agents = await self.claude_creator.create_agents_with_claude(
                idea=idea,
                container_id=container_id,
                workspace_path=workspace_path
            )
            
            if not claude_agents:
                logger.warning("No agents were created by Claude Code")
                return self._create_fallback_response(idea, model)
            
            # Store the agents for later use
            self.last_created_agents = claude_agents
            
            # Convert Claude's created agents to AgentConfig objects
            agent_configs = self.claude_creator.convert_to_agent_configs(claude_agents)
            
            # Create metadata for orchestrator
            agentic_metadata = self._create_agentic_metadata(claude_agents, idea, model)
            
            logger.info(f"Claude naturally created {len(agent_configs)} agents: "
                       f"{[config.name for config in agent_configs]}")
            
            # Log details about created agents
            for agent in claude_agents:
                logger.info(f"  - {agent.name}: {agent.description}")
                if agent.reasoning:
                    logger.info(f"    Reasoning: {agent.reasoning}")
            
            return agent_configs, agentic_metadata
            
        except Exception as e:
            logger.error(f"Claude agent creation failed: {e}")
            # Fall back to simple agent
            return self._create_fallback_response(idea, model)
    
    def _create_agentic_metadata(
        self,
        claude_agents: List[ClaudeCreatedAgent],
        idea: str,
        model: str
    ) -> Dict[str, Any]:
        """Create metadata about the agentic execution.
        
        Args:
            claude_agents: List of Claude-created agents
            idea: Original project idea
            model: Claude model used
            
        Returns:
            Agentic metadata dictionary
        """
        return {
            "agentic_mode": True,
            "creation_method": "claude_code_natural",
            "claude_model": model,
            "agent_count": len(claude_agents),
            "coordination_strategy": "natural_claude_creation",
            "execution_order": [agent.name for agent in claude_agents],
            "estimated_duration": "2-6 hours",  # Reasonable estimate
            "success_criteria": [
                "Working implementation",
                "Clean code structure",
                "Proper documentation",
                "Meets user requirements"
            ],
            "claude_reasoning": "Agents created through Claude Code's natural analysis",
            "creation_timestamp": datetime.now().isoformat(),
            "original_idea": idea,
            "agent_names": [agent.name for agent in claude_agents],
            "intelligent_creation": True,
            "natural_creation": True,
            "fallback": False
        }
    
    def _create_fallback_response(
        self, 
        idea: str, 
        model: str
    ) -> Tuple[List[AgentConfig], Dict[str, Any]]:
        """Create fallback response if Claude creation fails.
        
        Args:
            idea: Project idea
            model: Claude model being used
            
        Returns:
            Tuple of (agent configs, metadata)
        """
        fallback_config = self._create_fallback_agent_config(idea, model)
        fallback_metadata = {
            "agentic_mode": False,
            "fallback": True,
            "error": "Claude Code agent creation failed",
            "fallback_reason": "Natural Claude Code agent creation failed"
        }
        
        return [fallback_config], fallback_metadata
    
    def _create_fallback_agent_config(self, idea: str, model: str) -> AgentConfig:
        """Create fallback agent config if Claude creation fails.
        
        Args:
            idea: Project idea
            model: Claude model being used
            
        Returns:
            Fallback agent configuration
        """
        fallback_prompt = f"""---
name: GeneralDeveloper
description: General-purpose developer (fallback)
tools: ["Read", "Write", "Edit", "MultiEdit", "Glob", "Grep", "Bash", "TodoWrite"]
parallelism: 2
patterns: ["fallback", "general"]
---

# General Developer (Fallback)

You are a versatile software developer working on: {idea}

## Your Mission
Since specialized agent creation failed, you need to handle this project comprehensively:

1. **Analyze** the project requirements thoroughly
2. **Plan** the implementation approach step by step
3. **Implement** clean, well-documented code
4. **Test** your implementation works correctly
5. **Document** the solution clearly

## Approach
- Break down complex tasks into manageable steps
- Follow best practices for the technology stack
- Write clean, maintainable code
- Include proper error handling
- Create useful documentation

## Focus Areas
- Understand the core requirements
- Choose appropriate technologies
- Implement a working solution
- Ensure code quality and reliability

Work systematically and deliver a complete, functional project that meets the user's needs.
"""
        
        agent_file_path = self.templates_dir / ".claude" / "agents" / "fallback_general.md"
        
        return AgentConfig(
            name="GeneralDeveloper",
            description="General-purpose developer (fallback when Claude agent creation fails)",
            tools=["Read", "Write", "Edit", "MultiEdit", "Glob", "Grep", "Bash", "TodoWrite"],
            parallelism=2,
            patterns=["fallback", "general"],
            content=fallback_prompt,
            file_path=str(agent_file_path)
        )
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """Get summary of the agent creation process.
        
        Returns:
            Execution summary
        """
        if not self.last_created_agents:
            return {"status": "no_agents_created"}
        
        return {
            "status": "success",
            "agents_created": len(self.last_created_agents),
            "agent_names": [a.name for a in self.last_created_agents],
            "creation_method": "natural_claude_code",
            "agent_details": [
                {
                    "name": agent.name,
                    "description": agent.description,
                    "file_path": agent.file_path,
                    "reasoning": agent.reasoning
                }
                for agent in self.last_created_agents
            ]
        }