"""
Agentic Orchestrator for MetaClaude

This module provides the orchestration layer that integrates the research-enhanced
agentic agent creation system with the existing MetaClaude infrastructure.
It manages the complete workflow from idea analysis to agent creation to 
Claude Code execution with dynamic agent coordination.

Features:
    - Seamless integration with existing orchestrator
    - Dynamic agent creation and configuration
    - Research-enhanced agent generation
    - Multi-agent coordination and execution
    - Real-time web research integration
"""

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

from .agentic_creator import (
    ResearchEnhancedAgentGenerator,
    DynamicAgent,
    AgentBlueprint,
    ProjectAnalysis,
    ComplexityLevel
)
from .parser import AgentConfig
from ..utils.logging import get_logger
from ..utils.errors import MetaClaudeAgentError, MetaClaudeExecutionError

logger = get_logger(__name__)


class AgenticOrchestrator:
    """
    Orchestrator for agentic agent creation and coordination.
    
    This class manages the complete agentic workflow:
    1. Analyzes project requirements using AI
    2. Designs optimal agent architecture 
    3. Creates research-enhanced specialized agents
    4. Generates Claude Code configuration
    5. Coordinates multi-agent execution
    """
    
    def __init__(self, templates_dir: Path, web_search_available: bool = True):
        """Initialize the agentic orchestrator.
        
        Args:
            templates_dir: Path to templates directory
            web_search_available: Whether WebSearch tool is available
        """
        self.templates_dir = templates_dir
        self.web_search_available = web_search_available
        
        # Initialize the research-enhanced agent generator
        self.agent_generator = ResearchEnhancedAgentGenerator()
        
        # Execution state
        self.current_agents: List[DynamicAgent] = []
        self.current_blueprint: Optional[AgentBlueprint] = None
        self.execution_context: Dict[str, Any] = {}
        
        logger.info("AgenticOrchestrator initialized with research enhancement")
    
    async def create_agentic_team(self, idea: str) -> Tuple[List[DynamicAgent], AgentBlueprint]:
        """Create a complete agentic team for the project.
        
        Args:
            idea: Project idea description
            
        Returns:
            Tuple of (dynamic agents, agent blueprint)
            
        Raises:
            VCCAgentError: If agent creation fails
        """
        logger.info(f"Creating agentic team for project: {idea[:50]}...")
        
        try:
            # Create research-enhanced agent team
            agents, blueprint = await self.agent_generator.create_agentic_project_team(idea)
            
            # Store current state
            self.current_agents = agents
            self.current_blueprint = blueprint
            
            # Create execution context
            self.execution_context = {
                "idea": idea,
                "creation_time": datetime.now().isoformat(),
                "agent_count": len(agents),
                "complexity": blueprint.coordination_strategy,
                "estimated_duration": blueprint.estimated_duration
            }
            
            logger.info(f"Agentic team created successfully: {len(agents)} agents")
            self._log_team_summary(agents, blueprint)
            
            return agents, blueprint
            
        except Exception as e:
            logger.error(f"Agentic team creation failed: {e}")
            raise MetaClaudeAgentError(f"Failed to create agentic team: {e}")
    
    def convert_to_claude_config(
        self, 
        agents: List[DynamicAgent], 
        blueprint: AgentBlueprint,
        model: str = "opus",
        project_name: str = "Generated Project"
    ) -> Dict[str, Any]:
        """Convert agentic team to Claude Code configuration.
        
        Args:
            agents: List of dynamic agents
            blueprint: Agent blueprint
            model: Claude model to use
            project_name: Name of the project
            
        Returns:
            Claude Code configuration dictionary
        """
        logger.info("Converting agentic team to Claude Code configuration")
        
        # Create CLAUDE.md content with agentic team
        claude_md_content = self._generate_claude_md_content(agents, blueprint, project_name)
        
        # Create agent configurations for Claude Code
        agent_configs = []
        for agent in agents:
            agent_config = {
                "name": agent.name,
                "description": agent.description,
                "system_prompt": agent.system_prompt,
                "tools": agent.tools,
                "expertise_level": agent.expertise_level.value,
                "specialization_areas": agent.specialization_areas,
                "research_enhanced": agent.research_enhanced,
                "creation_timestamp": agent.creation_timestamp.isoformat()
            }
            agent_configs.append(agent_config)
        
        # Create execution plan
        execution_plan = {
            "execution_order": blueprint.execution_order,
            "parallel_groups": blueprint.parallel_groups,
            "collaboration_matrix": blueprint.collaboration_matrix,
            "quality_gates": blueprint.quality_gates,
            "coordination_strategy": blueprint.coordination_strategy,
            "success_criteria": blueprint.success_criteria
        }
        
        config = {
            "model": model,
            "project_name": project_name,
            "claude_md_content": claude_md_content,
            "agentic_team": {
                "agents": agent_configs,
                "blueprint": execution_plan,
                "execution_context": self.execution_context
            },
            "settings": {
                "research_enhanced": True,
                "multi_agent_coordination": True,
                "agent_count": len(agents)
            }
        }
        
        logger.info(f"Claude Code configuration generated for {len(agents)} agents")
        return config
    
    def _generate_claude_md_content(
        self, 
        agents: List[DynamicAgent], 
        blueprint: AgentBlueprint,
        project_name: str
    ) -> str:
        """Generate CLAUDE.md content for agentic team execution.
        
        Args:
            agents: List of dynamic agents
            blueprint: Agent blueprint
            project_name: Name of the project
            
        Returns:
            CLAUDE.md content as string
        """
        sections = []
        
        # Header
        sections.append(f"# {project_name}")
        sections.append("*Generated by MetaClaude Agentic System with Research-Enhanced Agents*")
        sections.append(f"*Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
        
        # Project overview
        sections.append("## 🚀 Project Overview")
        sections.append(f"This project has been analyzed and will be implemented by a specialized team of {len(agents)} AI agents.")
        sections.append(f"Each agent has been research-enhanced with the latest 2025 industry knowledge and best practices.")
        sections.append(f"**Estimated Duration**: {blueprint.estimated_duration}")
        sections.append(f"**Coordination Strategy**: {blueprint.coordination_strategy}\n")
        
        # Agent team overview
        sections.append("## 🤖 Specialized Agent Team")
        sections.append("The following AI agents will collaborate to build your project:\n")
        
        for i, agent in enumerate(agents, 1):
            sections.append(f"### {i}. {agent.name}")
            sections.append(f"**Role**: {agent.description}")
            sections.append(f"**Expertise Level**: {agent.expertise_level.value.title()}")
            sections.append(f"**Specialization Areas**: {', '.join(agent.specialization_areas)}")
            sections.append(f"**Research Enhanced**: {'✅ Yes' if agent.research_enhanced else '❌ No'}")
            sections.append("")
        
        # Execution plan
        sections.append("## 📋 Execution Plan")
        sections.append("### Execution Order")
        for i, agent_name in enumerate(blueprint.execution_order, 1):
            sections.append(f"{i}. {agent_name}")
        sections.append("")
        
        # Parallel execution groups
        if blueprint.parallel_groups:
            sections.append("### Parallel Execution Groups")
            for i, group in enumerate(blueprint.parallel_groups, 1):
                sections.append(f"**Group {i}**: {', '.join(group)} (can work simultaneously)")
            sections.append("")
        
        # Quality gates
        sections.append("### Quality Gates")
        for gate in blueprint.quality_gates:
            sections.append(f"- {gate}")
        sections.append("")
        
        # Success criteria
        sections.append("### Success Criteria")
        for criterion in blueprint.success_criteria:
            sections.append(f"- {criterion}")
        sections.append("")
        
        # Agent coordination instructions
        sections.append("## 🔄 Agent Coordination Instructions")
        sections.append("You are part of a specialized AI agent team. Follow these coordination guidelines:")
        sections.append("")
        
        coordination_instructions = self._generate_coordination_instructions(blueprint)
        sections.append(coordination_instructions)
        
        # Main project prompt
        sections.append("## 🎯 Project Implementation")
        sections.append(f"**Primary Objective**: {self.execution_context.get('idea', 'Complete the assigned project')}")
        sections.append("")
        sections.append("### Implementation Guidelines")
        sections.append("1. **Follow your agent specialization** - Focus on your areas of expertise")
        sections.append("2. **Use latest knowledge** - Apply 2025 best practices from your research-enhanced knowledge base")
        sections.append("3. **Coordinate effectively** - Work with other agents according to the execution plan") 
        sections.append("4. **Maintain quality** - Ensure all quality gates are met")
        sections.append("5. **Document thoroughly** - Provide comprehensive documentation for your work")
        sections.append("")
        
        # Individual agent prompts
        sections.append("## 👥 Individual Agent Instructions")
        sections.append("Each agent should focus on their specialized role while coordinating with the team:\n")
        
        for agent in agents:
            sections.append(f"### Instructions for {agent.name}")
            sections.append(f"```")
            sections.append(agent.system_prompt)
            sections.append(f"```")
            sections.append("")
            
            # Collaboration instructions
            sections.append(f"**Collaboration Instructions for {agent.name}:**")
            sections.append(agent.collaboration_instructions)
            sections.append("")
            
            # Success metrics
            sections.append(f"**Success Metrics for {agent.name}:**")
            for metric in agent.success_metrics:
                sections.append(f"- {metric}")
            sections.append("")
        
        return "\n".join(sections)
    
    def _generate_coordination_instructions(self, blueprint: AgentBlueprint) -> str:
        """Generate coordination instructions based on blueprint.
        
        Args:
            blueprint: Agent blueprint
            
        Returns:
            Coordination instructions as string
        """
        instructions = []
        
        if blueprint.coordination_strategy == "hierarchical_with_architect_lead":
            instructions.extend([
                "### Hierarchical Coordination with Architect Leadership",
                "- **System Architect** leads overall technical decisions",
                "- Development agents report to architect for major decisions",
                "- Support agents coordinate with relevant development agents",
                "- Regular progress updates and architectural reviews",
                ""
            ])
        elif blueprint.coordination_strategy == "collaborative_with_priority_coordination":
            instructions.extend([
                "### Collaborative Coordination with Priority-Based Flow",
                "- Agents work according to priority levels and dependencies",
                "- High-priority agents (1-2) establish foundation",
                "- Medium-priority agents (3) build on established foundation", 
                "- Support agents (4+) provide quality assurance and optimization",
                ""
            ])
        elif blueprint.coordination_strategy == "peer_to_peer_collaboration":
            instructions.extend([
                "### Peer-to-Peer Collaboration",
                "- All agents work as equal peers",
                "- Coordinate directly with relevant agents",
                "- Share progress and coordinate feature development",
                "- Review each other's work for quality and consistency",
                ""
            ])
        else:
            instructions.extend([
                "### Single Agent Execution",
                "- Work independently to complete all project requirements",
                "- Apply expertise from all relevant domains",
                ""
            ])
        
        # Add general coordination principles
        instructions.extend([
            "### General Coordination Principles",
            "1. **Communication**: Share progress, issues, and decisions",
            "2. **Dependencies**: Respect execution order and dependencies",
            "3. **Quality**: Review and validate other agents' work when relevant",
            "4. **Consistency**: Maintain consistent standards across the project",
            "5. **Documentation**: Document decisions and implementation details",
            ""
        ])
        
        return "\n".join(instructions)
    
    def generate_claude_files(
        self,
        agents: List[DynamicAgent],
        blueprint: AgentBlueprint,
        output_dir: Path,
        model: str = "opus",
        project_name: str = "Generated Project"
    ) -> None:
        """Generate Claude Code configuration files.
        
        Args:
            agents: List of dynamic agents
            blueprint: Agent blueprint
            output_dir: Output directory for files
            model: Claude model to use
            project_name: Name of the project
        """
        logger.info(f"Generating Claude Code files in {output_dir}")
        
        # Create .claude directory
        claude_dir = output_dir / ".claude"
        claude_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate CLAUDE.md
        claude_md_content = self._generate_claude_md_content(agents, blueprint, project_name)
        claude_md_path = claude_dir / "CLAUDE.md"
        claude_md_path.write_text(claude_md_content, encoding="utf-8")
        
        # Generate settings.json
        settings = self._generate_settings_json(agents, model)
        settings_path = claude_dir / "settings.json"
        settings_path.write_text(json.dumps(settings, indent=2), encoding="utf-8")
        
        # Generate agent metadata file
        agent_metadata = self._generate_agent_metadata(agents, blueprint)
        metadata_path = claude_dir / "agent_metadata.json"
        metadata_path.write_text(json.dumps(agent_metadata, indent=2), encoding="utf-8")
        
        logger.info("Claude Code configuration files generated successfully")
    
    def _generate_settings_json(self, agents: List[DynamicAgent], model: str) -> Dict[str, Any]:
        """Generate settings.json for Claude Code.
        
        Args:
            agents: List of dynamic agents
            model: Claude model to use
            
        Returns:
            Settings configuration
        """
        # Collect all unique tools from agents
        all_tools = set()
        for agent in agents:
            all_tools.update(agent.tools)
        
        settings = {
            "model": model,
            "tools": {
                "enabled": list(all_tools),
                "permissions": {
                    "read_files": True,
                    "write_files": True,
                    "execute_commands": True,
                    "web_search": self.web_search_available
                }
            },
            "agentic_mode": {
                "enabled": True,
                "agent_count": len(agents),
                "research_enhanced": True,
                "coordination_enabled": True
            },
            "quality_settings": {
                "enforce_quality_gates": True,
                "require_documentation": True,
                "enable_cross_agent_review": len(agents) > 1
            }
        }
        
        return settings
    
    def _generate_agent_metadata(
        self, 
        agents: List[DynamicAgent], 
        blueprint: AgentBlueprint
    ) -> Dict[str, Any]:
        """Generate agent metadata for reference.
        
        Args:
            agents: List of dynamic agents
            blueprint: Agent blueprint
            
        Returns:
            Agent metadata
        """
        metadata = {
            "generation_info": {
                "created_at": datetime.now().isoformat(),
                "generator_version": "1.0.0",
                "research_enhanced": True
            },
            "team_composition": {
                "total_agents": len(agents),
                "coordination_strategy": blueprint.coordination_strategy,
                "estimated_duration": blueprint.estimated_duration
            },
            "agents": [],
            "execution_plan": {
                "execution_order": blueprint.execution_order,
                "parallel_groups": blueprint.parallel_groups,
                "quality_gates": blueprint.quality_gates,
                "success_criteria": blueprint.success_criteria
            }
        }
        
        for agent in agents:
            agent_info = {
                "name": agent.name,
                "description": agent.description,
                "expertise_level": agent.expertise_level.value,
                "specialization_areas": agent.specialization_areas,
                "tools": agent.tools,
                "research_enhanced": agent.research_enhanced,
                "knowledge_quality_score": agent.knowledge_base.quality_score,
                "success_metrics": agent.success_metrics,
                "creation_timestamp": agent.creation_timestamp.isoformat()
            }
            metadata["agents"].append(agent_info)
        
        return metadata
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """Get summary of current agentic execution.
        
        Returns:
            Execution summary
        """
        if not self.current_agents or not self.current_blueprint:
            return {"status": "no_active_execution"}
        
        return {
            "status": "active",
            "agent_count": len(self.current_agents),
            "coordination_strategy": self.current_blueprint.coordination_strategy,
            "estimated_duration": self.current_blueprint.estimated_duration,
            "execution_context": self.execution_context,
            "agents": [
                {
                    "name": agent.name,
                    "role": agent.description,
                    "research_enhanced": agent.research_enhanced,
                    "expertise_level": agent.expertise_level.value
                }
                for agent in self.current_agents
            ]
        }
    
    def _log_team_summary(self, agents: List[DynamicAgent], blueprint: AgentBlueprint) -> None:
        """Log summary of created agentic team.
        
        Args:
            agents: List of dynamic agents
            blueprint: Agent blueprint
        """
        logger.info("=== AGENTIC TEAM SUMMARY ===")
        logger.info(f"Team Size: {len(agents)} agents")
        logger.info(f"Coordination Strategy: {blueprint.coordination_strategy}")
        logger.info(f"Estimated Duration: {blueprint.estimated_duration}")
        
        logger.info("Agent Composition:")
        for agent in agents:
            research_status = "✅ Research-Enhanced" if agent.research_enhanced else "❌ Basic"
            logger.info(f"  - {agent.name}: {agent.expertise_level.value.title()} ({research_status})")
        
        logger.info(f"Execution Order: {' → '.join(blueprint.execution_order)}")
        
        if blueprint.parallel_groups:
            logger.info("Parallel Groups:")
            for i, group in enumerate(blueprint.parallel_groups, 1):
                logger.info(f"  Group {i}: {', '.join(group)}")
        
        logger.info("=== END TEAM SUMMARY ===")


class AgenticIntegration:
    """
    Integration layer between agentic system and existing MetaClaude orchestrator.
    
    This class provides a bridge between the new agentic agent creation system
    and the existing MetaClaude orchestrator, allowing seamless integration.
    """
    
    def __init__(self, templates_dir: Path):
        """Initialize the agentic integration.
        
        Args:
            templates_dir: Path to templates directory
        """
        self.templates_dir = templates_dir
        self.agentic_orchestrator = AgenticOrchestrator(templates_dir)
        
        logger.info("AgenticIntegration initialized")
    
    async def create_agentic_agents(
        self,
        idea: str,
        model: str = "opus",
        force_agents: Optional[List[str]] = None,
        custom_template_vars: Optional[Dict[str, Any]] = None
    ) -> Tuple[List[AgentConfig], Dict[str, Any]]:
        """Create agentic agents compatible with existing system.
        
        Args:
            idea: Project idea description
            model: Claude model to use
            force_agents: Ignored for agentic creation (agents determined by AI)
            custom_template_vars: Custom template variables
            
        Returns:
            Tuple of (agent configs, agentic metadata)
        """
        logger.info("Creating agentic agents for MetaClaude integration")
        
        try:
            # Create agentic team
            dynamic_agents, blueprint = await self.agentic_orchestrator.create_agentic_team(idea)
            
            # Convert to AgentConfig format for compatibility
            agent_configs = []
            for agent in dynamic_agents:
                # Create temporary file path for agent
                agent_file_path = self.templates_dir / ".claude" / "agents" / f"{agent.name.lower()}.md"
                
                agent_config = AgentConfig(
                    name=agent.name,
                    description=agent.description,
                    tools=agent.tools,
                    parallelism=min(len(agent.specialization_areas), 4),  # Reasonable parallelism
                    patterns=["agentic", "research-enhanced"],
                    content=agent.system_prompt,
                    file_path=str(agent_file_path)
                )
                agent_configs.append(agent_config)
            
            # Create agentic metadata for orchestrator
            agentic_metadata = {
                "agentic_mode": True,
                "blueprint": blueprint,
                "dynamic_agents": dynamic_agents,
                "execution_context": self.agentic_orchestrator.execution_context,
                "coordination_strategy": blueprint.coordination_strategy
            }
            
            logger.info(f"Agentic agents created: {len(agent_configs)} agents")
            return agent_configs, agentic_metadata
            
        except Exception as e:
            logger.error(f"Agentic agent creation failed: {e}")
            # Fall back to single general agent
            fallback_config = self._create_fallback_agent_config(idea)
            return [fallback_config], {"agentic_mode": False, "fallback": True}
    
    def _create_fallback_agent_config(self, idea: str) -> AgentConfig:
        """Create fallback agent config if agentic creation fails.
        
        Args:
            idea: Project idea
            
        Returns:
            Fallback agent configuration
        """
        fallback_content = f"""# General Development Agent

You are a versatile software developer tasked with implementing this project:

## Project Idea
{idea}

## Your Role
Analyze the requirements and implement a complete solution following best practices.
Use your expertise across multiple domains to create a high-quality project.

## Guidelines
- Follow current industry best practices
- Implement proper error handling and testing
- Create comprehensive documentation
- Ensure code quality and maintainability
"""
        
        agent_file_path = self.templates_dir / ".claude" / "agents" / "fallback_general.md"
        
        return AgentConfig(
            name="GeneralDeveloper",
            description="General-purpose developer for complete project implementation",
            tools=["Read", "Write", "Edit", "MultiEdit", "Glob", "Grep", "Bash", "WebFetch", "TodoWrite"],
            parallelism=2,
            patterns=["general", "fallback"],
            content=fallback_content,
            file_path=str(agent_file_path)
        )
    
    def generate_claude_configuration(
        self,
        workspace_path: Path,
        idea: str,
        model: str,
        dynamic_agents: List[DynamicAgent],
        blueprint: AgentBlueprint,
        custom_template_vars: Optional[Dict[str, Any]] = None
    ) -> None:
        """Generate Claude Code configuration for agentic execution.
        
        Args:
            workspace_path: Workspace directory path
            idea: Project idea
            model: Claude model
            dynamic_agents: List of dynamic agents
            blueprint: Agent blueprint
            custom_template_vars: Custom template variables
        """
        logger.info("Generating Claude Code configuration for agentic execution")
        
        # Generate project name
        project_name = self._generate_project_name(idea)
        
        # Generate Claude configuration files
        self.agentic_orchestrator.generate_claude_files(
            agents=dynamic_agents,
            blueprint=blueprint,
            output_dir=workspace_path,
            model=model,
            project_name=project_name
        )
        
        logger.info("Agentic Claude Code configuration generated successfully")
    
    def _generate_project_name(self, idea: str) -> str:
        """Generate project name from idea.
        
        Args:
            idea: Project idea
            
        Returns:
            Generated project name
        """
        # Extract key words and create project name
        words = idea.split()[:5]  # First 5 words
        safe_words = []
        
        for word in words:
            # Clean word
            clean_word = "".join(c for c in word if c.isalnum())
            if clean_word and len(clean_word) > 2:
                safe_words.append(clean_word.title())
        
        if safe_words:
            return "".join(safe_words)[:50]  # Limit length
        else:
            return "AgenticProject"


# Export main classes
__all__ = [
    'AgenticOrchestrator',
    'AgenticIntegration'
]