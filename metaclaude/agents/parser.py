"""Agent configuration parser for MetaClaude."""

import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, validator

from ..utils.errors import MetaClaudeAgentError
from ..utils.logging import get_logger

logger = get_logger(__name__)


class AgentConfig(BaseModel):
    """Pydantic model for agent configuration."""
    
    name: str = Field(..., description="Agent name")
    description: str = Field(..., description="Agent description")
    tools: List[str] = Field(..., description="List of available tools")
    parallelism: Optional[int] = Field(default=1, description="Number of parallel operations")
    patterns: Optional[List[str]] = Field(default_factory=list, description="Agent patterns")
    content: str = Field(..., description="Agent system prompt content")
    file_path: str = Field(..., description="Path to agent template file")
    
    @validator("parallelism")
    def validate_parallelism(cls, v: Optional[int]) -> int:
        """Validate parallelism value."""
        if v is None:
            return 1
        if v < 1 or v > 10:
            raise ValueError("Parallelism must be between 1 and 10")
        return v
    
    @validator("tools")
    def validate_tools(cls, v: List[str]) -> List[str]:
        """Validate tools list."""
        if not v:
            raise ValueError("At least one tool must be specified")
        
        valid_tools = {
            "Bash", "Read", "Write", "Edit", "MultiEdit", "Glob", "Grep", "LS",
            "WebFetch", "WebSearch", "TodoWrite", "Task", "NotebookRead", "NotebookEdit"
        }
        
        for tool in v:
            if tool not in valid_tools:
                logger.warning(f"Unknown tool specified: {tool}")
        
        return v
    
    @validator("patterns")
    def validate_patterns(cls, v: Optional[List[str]]) -> List[str]:
        """Validate agent patterns."""
        if v is None:
            return []
        
        valid_patterns = {"planner", "coder", "tester", "researcher"}
        
        for pattern in v:
            if pattern not in valid_patterns:
                logger.warning(f"Unknown pattern specified: {pattern}")
        
        return v


class AgentParser:
    """Parser for agent configuration files."""
    
    def __init__(self):
        """Initialize agent parser."""
        logger.info("AgentParser initialized")
    
    def parse_agent_file(self, agent_file: Path) -> AgentConfig:
        """Parse individual agent template file.
        
        Args:
            agent_file: Path to agent template file
            
        Returns:
            Parsed agent configuration
            
        Raises:
            MetaClaudeAgentError: If parsing fails
        """
        try:
            logger.debug(f"Parsing agent file: {agent_file}")
            
            if not agent_file.exists():
                raise MetaClaudeAgentError(f"Agent file does not exist: {agent_file}")
            
            content = agent_file.read_text(encoding="utf-8")
            
            # Split YAML front-matter from content
            if not content.startswith("---"):
                raise MetaClaudeAgentError(f"Missing YAML front-matter in {agent_file}")
            
            parts = content.split("---", 2)
            if len(parts) < 3:
                raise MetaClaudeAgentError(f"Invalid front-matter format in {agent_file}")
            
            front_matter = parts[1].strip()
            agent_content = parts[2].strip()
            
            # Parse YAML front-matter
            try:
                metadata = yaml.safe_load(front_matter)
                if not isinstance(metadata, dict):
                    raise MetaClaudeAgentError(f"Front-matter must be a dictionary in {agent_file}")
            except yaml.YAMLError as e:
                raise MetaClaudeAgentError(f"Invalid YAML in {agent_file}: {e}")
            
            # Add content and file path
            metadata["content"] = agent_content
            metadata["file_path"] = str(agent_file)
            
            # Create and validate agent configuration
            agent_config = AgentConfig(**metadata)
            
            logger.debug(f"Successfully parsed agent: {agent_config.name}")
            return agent_config
            
        except Exception as e:
            logger.error(f"Failed to parse agent file {agent_file}: {e}")
            if isinstance(e, MetaClaudeAgentError):
                raise
            raise MetaClaudeAgentError(f"Agent file parsing failed: {e}")
    
    def parse_agents_directory(self, agents_dir: Path) -> Dict[str, AgentConfig]:
        """Parse all agent files in a directory.
        
        Args:
            agents_dir: Directory containing agent template files
            
        Returns:
            Dictionary mapping agent names to configurations
            
        Raises:
            MetaClaudeAgentError: If parsing fails
        """
        try:
            logger.info(f"Parsing agents directory: {agents_dir}")
            
            if not agents_dir.exists():
                logger.warning(f"Agents directory does not exist: {agents_dir}")
                return {}
            
            agents = {}
            
            for agent_file in agents_dir.glob("*.md"):
                try:
                    agent_config = self.parse_agent_file(agent_file)
                    
                    # Check for duplicate names
                    if agent_config.name in agents:
                        logger.warning(f"Duplicate agent name found: {agent_config.name}")
                    
                    agents[agent_config.name] = agent_config
                    
                except MetaClaudeAgentError as e:
                    logger.error(f"Failed to parse agent file {agent_file}: {e}")
                    # Continue parsing other files
                    continue
            
            logger.info(f"Successfully parsed {len(agents)} agents")
            return agents
            
        except Exception as e:
            logger.error(f"Failed to parse agents directory: {e}")
            raise MetaClaudeAgentError(f"Agents directory parsing failed: {e}")
    
    def validate_agent_config(self, config: Dict[str, Any]) -> List[str]:
        """Validate agent configuration dictionary.
        
        Args:
            config: Agent configuration dictionary
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        try:
            # Try to create AgentConfig instance for validation
            AgentConfig(**config)
        except Exception as e:
            errors.append(str(e))
        
        # Additional custom validations
        if "name" in config:
            name = config["name"]
            if not isinstance(name, str) or not name.strip():
                errors.append("Agent name must be a non-empty string")
            elif not name.replace("-", "").replace("_", "").isalnum():
                errors.append("Agent name must be alphanumeric with hyphens/underscores")
        
        if "description" in config:
            description = config["description"]
            if not isinstance(description, str) or len(description.strip()) < 10:
                errors.append("Agent description must be at least 10 characters")
        
        if "content" in config:
            content = config["content"]
            if not isinstance(content, str) or len(content.strip()) < 50:
                errors.append("Agent content must be at least 50 characters")
        
        return errors
    
    def get_agent_capabilities(self, agent_config: AgentConfig) -> Dict[str, Any]:
        """Extract agent capabilities from configuration.
        
        Args:
            agent_config: Agent configuration
            
        Returns:
            Dictionary of agent capabilities
        """
        capabilities = {
            "name": agent_config.name,
            "description": agent_config.description,
            "tools": agent_config.tools,
            "parallelism": agent_config.parallelism,
            "patterns": agent_config.patterns,
            "can_execute_bash": "Bash" in agent_config.tools,
            "can_read_files": "Read" in agent_config.tools,
            "can_write_files": "Write" in agent_config.tools or "Edit" in agent_config.tools,
            "can_search_web": "WebSearch" in agent_config.tools or "WebFetch" in agent_config.tools,
            "can_manage_tasks": "TodoWrite" in agent_config.tools,
            "supports_planning": "planner" in agent_config.patterns,
            "supports_coding": "coder" in agent_config.patterns,
            "supports_testing": "tester" in agent_config.patterns,
            "supports_research": "researcher" in agent_config.patterns,
        }
        
        logger.debug(f"Extracted capabilities for agent {agent_config.name}")
        return capabilities