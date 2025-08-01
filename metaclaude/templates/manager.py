"""Template management system for VCC."""

import json
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from jinja2 import Environment, FileSystemLoader, Template

from ..utils.errors import MetaClaudeTemplateError
from ..utils.logging import get_logger

logger = get_logger(__name__)


class TemplateManager:
    """Manages template loading, rendering, and configuration generation."""
    
    def __init__(self, templates_dir: Path):
        """Initialize template manager.
        
        Args:
            templates_dir: Path to templates directory
        """
        self.templates_dir = templates_dir
        self.claude_dir = templates_dir / ".claude"
        self.agents_dir = self.claude_dir / "agents"
        
        # Initialize Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(templates_dir)),
            autoescape=False,
            trim_blocks=True,
            lstrip_blocks=True,
        )
        
        logger.info(f"TemplateManager initialized with templates dir: {templates_dir}")
    
    def load_agent_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load all agent templates with their metadata.
        
        Returns:
            Dictionary mapping agent names to their configuration
            
        Raises:
            MetaClaudeTemplateError: If agent template loading fails
        """
        agents = {}
        
        try:
            if not self.agents_dir.exists():
                logger.warning(f"Agents directory not found: {self.agents_dir}")
                return agents
            
            for agent_file in self.agents_dir.glob("*.md"):
                agent_config = self._parse_agent_template(agent_file)
                agents[agent_config["name"]] = agent_config
                logger.debug(f"Loaded agent template: {agent_config['name']}")
            
            logger.info(f"Loaded {len(agents)} agent templates")
            return agents
            
        except Exception as e:
            logger.error(f"Failed to load agent templates: {e}")
            raise MetaClaudeTemplateError(f"Agent template loading failed: {e}")
    
    def _parse_agent_template(self, agent_file: Path) -> Dict[str, Any]:
        """Parse individual agent template file.
        
        Args:
            agent_file: Path to agent template file
            
        Returns:
            Agent configuration dictionary
            
        Raises:
            MetaClaudeTemplateError: If parsing fails
        """
        try:
            content = agent_file.read_text(encoding="utf-8")
            
            # Split YAML front-matter from content
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    front_matter = parts[1].strip()
                    agent_content = parts[2].strip()
                else:
                    raise MetaClaudeTemplateError(f"Invalid front-matter format in {agent_file}")
            else:
                raise MetaClaudeTemplateError(f"Missing front-matter in {agent_file}")
            
            # Parse YAML front-matter
            try:
                metadata = yaml.safe_load(front_matter)
            except yaml.YAMLError as e:
                raise MetaClaudeTemplateError(f"Invalid YAML in {agent_file}: {e}")
            
            # Add content to metadata
            metadata["content"] = agent_content
            metadata["file_path"] = str(agent_file)
            
            # Validate required fields
            required_fields = ["name", "description", "tools"]
            for field in required_fields:
                if field not in metadata:
                    raise MetaClaudeTemplateError(f"Missing required field '{field}' in {agent_file}")
            
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to parse agent template {agent_file}: {e}")
            raise MetaClaudeTemplateError(f"Agent template parsing failed: {e}")
    
    def select_agents_for_idea(self, idea: str, force_agents: Optional[List[str]] = None) -> List[str]:
        """Select appropriate agents based on project idea.
        
        Args:
            idea: Project idea/description
            force_agents: List of agent names to force include
            
        Returns:
            List of selected agent names
        """
        idea_lower = idea.lower()
        selected_agents = set()
        
        # Force agents if specified
        if force_agents:
            selected_agents.update(force_agents)
        
        # Keyword-based agent selection
        agent_keywords = {
            "fullstack-engineer": [
                "web", "frontend", "backend", "react", "node", "api", "database",
                "typescript", "javascript", "express", "next.js", "electron"
            ],
            "ml-dl-engineer": [
                "machine learning", "ml", "ai", "deep learning", "neural", "model",
                "pytorch", "tensorflow", "data science", "prediction", "classification"
            ],
            "devops-engineer": [
                "deploy", "infrastructure", "docker", "kubernetes", "aws", "cloud",
                "ci/cd", "pipeline", "terraform", "ansible", "monitoring"
            ],
            "qa-engineer": [
                "test", "testing", "quality", "qa", "automation", "cypress", "jest",
                "validation", "bug", "coverage"
            ],
        }
        
        # Select agents based on keywords
        for agent_name, keywords in agent_keywords.items():
            if any(keyword in idea_lower for keyword in keywords):
                selected_agents.add(agent_name)
        
        # Default to fullstack if no specific match
        if not selected_agents:
            selected_agents.add("fullstack-engineer")
        
        result = list(selected_agents)
        logger.info(f"Selected agents for idea: {result}")
        return result
    
    def render_claude_config(
        self,
        output_dir: Path,
        model: str = "opus",
        project_name: str = "Generated Project",
        project_description: str = "AI-generated software project",
        selected_agents: Optional[List[str]] = None,
        template_vars: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Render complete Claude configuration to output directory.
        
        Args:
            output_dir: Directory to render configuration
            model: Claude model to use
            project_name: Name of the project
            project_description: Description of the project
            selected_agents: List of agent names to include
            template_vars: Additional template variables
            
        Raises:
            MetaClaudeTemplateError: If rendering fails
        """
        try:
            claude_output_dir = output_dir / ".claude"
            claude_output_dir.mkdir(parents=True, exist_ok=True)
            
            # Default template variables
            default_vars = {
                "model": model,
                "project_name": project_name,
                "project_description": project_description,
                "generation_timestamp": datetime.now().isoformat(),
                "tech_stack": "To be determined based on requirements",
                "architecture_description": "Architecture will be designed based on project needs",
                "development_commands": "# Commands will be added during implementation",
                "implementation_details": "Implementation details will be provided during development",
                "extension_points": "Extension points will be identified during implementation",
                "custom_instructions": "Follow best practices and maintain code quality",
            }
            
            # Merge with provided variables
            if template_vars:
                default_vars.update(template_vars)
            
            # Render settings.json
            self._render_settings(claude_output_dir, default_vars)
            
            # Render MCP configuration
            self._render_mcp_config(claude_output_dir, default_vars)
            
            # Render CLAUDE.md
            self._render_claude_md(claude_output_dir, default_vars)
            
            # Copy selected agents
            if selected_agents:
                self._copy_selected_agents(claude_output_dir, selected_agents)
            
            logger.info(f"Claude configuration rendered to {claude_output_dir}")
            
        except Exception as e:
            logger.error(f"Failed to render Claude configuration: {e}")
            raise MetaClaudeTemplateError(f"Configuration rendering failed: {e}")
    
    def _render_settings(self, output_dir: Path, template_vars: Dict[str, Any]) -> None:
        """Render settings.json template."""
        template_path = self.claude_dir / "settings.json"
        output_path = output_dir / "settings.json"
        
        if template_path.exists():
            template = self.jinja_env.get_template(".claude/settings.json")
            rendered = template.render(**template_vars)
            output_path.write_text(rendered, encoding="utf-8")
            logger.debug("Rendered settings.json")
    
    def _render_mcp_config(self, output_dir: Path, template_vars: Dict[str, Any]) -> None:
        """Render MCP configuration template."""
        template_path = self.claude_dir / "mcp.json"
        output_path = output_dir / "mcp.json"
        
        if template_path.exists():
            template = self.jinja_env.get_template(".claude/mcp.json")
            rendered = template.render(**template_vars)
            output_path.write_text(rendered, encoding="utf-8")
            logger.debug("Rendered mcp.json")
    
    def _render_claude_md(self, output_dir: Path, template_vars: Dict[str, Any]) -> None:
        """Render CLAUDE.md template."""
        template_path = self.claude_dir / "CLAUDE.md"
        output_path = output_dir / "CLAUDE.md"
        
        if template_path.exists():
            template = self.jinja_env.get_template(".claude/CLAUDE.md")
            rendered = template.render(**template_vars)
            output_path.write_text(rendered, encoding="utf-8")
            logger.debug("Rendered CLAUDE.md")
    
    def _copy_selected_agents(self, output_dir: Path, selected_agents: List[str]) -> None:
        """Copy selected agent templates to output directory."""
        agents_output_dir = output_dir / "agents"
        agents_output_dir.mkdir(exist_ok=True)
        
        agents_config = self.load_agent_templates()
        
        for agent_name in selected_agents:
            if agent_name in agents_config:
                agent_config = agents_config[agent_name]
                source_file = Path(agent_config["file_path"])
                dest_file = agents_output_dir / source_file.name
                
                # Copy agent file
                dest_file.write_text(source_file.read_text(encoding="utf-8"), encoding="utf-8")
                logger.debug(f"Copied agent template: {agent_name}")
            else:
                logger.warning(f"Agent template not found: {agent_name}")
    
    def validate_templates(self) -> List[str]:
        """Validate all templates for syntax and required fields.
        
        Returns:
            List of validation errors (empty if all valid)
        """
        errors = []
        
        try:
            # Validate agent templates
            agents = self.load_agent_templates()
            for agent_name, config in agents.items():
                # Check required fields
                required_fields = ["name", "description", "tools", "content"]
                for field in required_fields:
                    if field not in config:
                        errors.append(f"Agent {agent_name}: missing field '{field}'")
                
                # Validate tools list
                if not isinstance(config.get("tools"), list):
                    errors.append(f"Agent {agent_name}: 'tools' must be a list")
            
            # Validate JSON templates
            json_templates = ["settings.json", "mcp.json"]
            for template_name in json_templates:
                template_path = self.claude_dir / template_name
                if template_path.exists():
                    try:
                        # Test template rendering with dummy variables
                        template = self.jinja_env.get_template(f".claude/{template_name}")
                        dummy_vars = {
                            "model": "test",
                            "github_token": "test",
                        }
                        rendered = template.render(**dummy_vars)
                        json.loads(rendered)  # Validate JSON syntax
                    except Exception as e:
                        errors.append(f"Template {template_name}: {e}")
            
        except Exception as e:
            errors.append(f"Template validation error: {e}")
        
        if errors:
            logger.warning(f"Template validation found {len(errors)} errors")
        else:
            logger.info("All templates validated successfully")
        
        return errors