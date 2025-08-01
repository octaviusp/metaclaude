"""Agent selector and augmenter for MetaClaude."""

import re
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from collections import defaultdict

from .parser import AgentConfig, AgentParser
from ..utils.errors import MetaClaudeAgentError
from ..utils.logging import get_logger

logger = get_logger(__name__)


class AgentSelector:
    """Selects and augments agents based on project requirements."""
    
    def __init__(self, agents_dir: Path):
        """Initialize agent selector.
        
        Args:
            agents_dir: Directory containing agent templates
        """
        self.agents_dir = agents_dir
        self.parser = AgentParser()
        self.available_agents: Dict[str, AgentConfig] = {}
        self._load_agents()
        
        # Domain keyword mappings
        self.domain_keywords = {
            "web": [
                "web", "website", "frontend", "backend", "fullstack", "react", "vue", "angular",
                "html", "css", "javascript", "typescript", "node", "express", "api", "rest",
                "graphql", "next.js", "nuxt", "svelte", "electron"
            ],
            "mobile": [
                "mobile", "app", "ios", "android", "react native", "flutter", "swift", "kotlin",
                "xamarin", "cordova", "ionic", "phone", "tablet"
            ],
            "ml": [
                "machine learning", "ml", "ai", "artificial intelligence", "deep learning",
                "neural network", "model", "pytorch", "tensorflow", "scikit", "pandas",
                "numpy", "data science", "prediction", "classification", "regression",
                "nlp", "computer vision", "cv", "transformers", "bert", "gpt"
            ],
            "data": [
                "data", "analytics", "database", "sql", "nosql", "mongodb", "postgresql",
                "mysql", "redis", "elasticsearch", "etl", "pipeline", "warehouse",
                "bigquery", "spark", "hadoop", "kafka", "airflow"
            ],
            "devops": [
                "devops", "infrastructure", "deployment", "ci/cd", "docker", "kubernetes",
                "aws", "azure", "gcp", "cloud", "terraform", "ansible", "jenkins",
                "github actions", "monitoring", "prometheus", "grafana", "helm"
            ],
            "desktop": [
                "desktop", "gui", "tkinter", "qt", "gtk", "wpf", "winforms", "electron",
                "tauri", "native", "cross-platform"
            ],
            "game": [
                "game", "gaming", "unity", "unreal", "godot", "pygame", "three.js",
                "webgl", "opengl", "vulkan", "directx", "2d", "3d"
            ],
            "blockchain": [
                "blockchain", "crypto", "web3", "ethereum", "bitcoin", "solidity",
                "smart contract", "defi", "nft", "dapp", "metamask"
            ],
            "testing": [
                "test", "testing", "qa", "quality assurance", "automation", "unit test",
                "integration test", "e2e", "cypress", "jest", "pytest", "selenium"
            ]
        }
        
        # Technology stack mappings
        self.tech_stack_agents = {
            "python": ["ml-dl-engineer", "fullstack-engineer", "qa-engineer"],
            "javascript": ["fullstack-engineer", "qa-engineer"],
            "typescript": ["fullstack-engineer", "qa-engineer"],
            "react": ["fullstack-engineer"],
            "node": ["fullstack-engineer"],
            "docker": ["devops-engineer", "fullstack-engineer"],
            "kubernetes": ["devops-engineer"],
            "aws": ["devops-engineer"],
            "terraform": ["devops-engineer"],
            "pytorch": ["ml-dl-engineer"],
            "tensorflow": ["ml-dl-engineer"],
        }
        
        logger.info(f"AgentSelector initialized with {len(self.available_agents)} agents")
    
    def _load_agents(self) -> None:
        """Load available agents from directory."""
        try:
            self.available_agents = self.parser.parse_agents_directory(self.agents_dir)
            logger.info(f"Loaded {len(self.available_agents)} agents")
        except Exception as e:
            logger.error(f"Failed to load agents: {e}")
            self.available_agents = {}
    
    def analyze_idea(self, idea: str) -> Dict[str, any]:
        """Analyze project idea to extract requirements and keywords.
        
        Args:
            idea: Project idea/description
            
        Returns:
            Analysis results including domains, technologies, complexity
        """
        idea_lower = idea.lower()
        
        # Extract domains
        detected_domains = set()
        for domain, keywords in self.domain_keywords.items():
            if any(keyword in idea_lower for keyword in keywords):
                detected_domains.add(domain)
        
        # Extract technologies
        detected_technologies = set()
        for tech, _ in self.tech_stack_agents.items():
            if tech in idea_lower:
                detected_technologies.add(tech)
        
        # Estimate complexity based on keywords
        complexity_indicators = [
            "enterprise", "scalable", "distributed", "microservices", "real-time",
            "high-performance", "machine learning", "ai", "blockchain", "advanced"
        ]
        complexity_score = sum(1 for indicator in complexity_indicators if indicator in idea_lower)
        
        if complexity_score >= 3:
            complexity = "high"
        elif complexity_score >= 1:
            complexity = "medium"
        else:
            complexity = "low"
        
        # Extract project type
        project_types = {
            "api": ["api", "rest", "graphql", "backend", "service"],
            "webapp": ["web app", "website", "frontend", "dashboard"],
            "mobile_app": ["mobile app", "ios app", "android app"],
            "desktop_app": ["desktop app", "gui", "application"],
            "cli": ["cli", "command line", "terminal", "script"],
            "library": ["library", "package", "module", "sdk"],
            "data_pipeline": ["pipeline", "etl", "data processing"],
            "ml_model": ["model", "prediction", "classification", "ml"],
        }
        
        detected_project_type = "general"
        for ptype, keywords in project_types.items():
            if any(keyword in idea_lower for keyword in keywords):
                detected_project_type = ptype
                break
        
        analysis = {
            "domains": list(detected_domains),
            "technologies": list(detected_technologies),
            "complexity": complexity,
            "project_type": detected_project_type,
            "word_count": len(idea.split()),
            "has_specific_requirements": len(detected_domains) > 0 or len(detected_technologies) > 0,
        }
        
        logger.info(f"Idea analysis: {analysis}")
        return analysis
    
    def select_agents(
        self,
        idea: str,
        force_agents: Optional[List[str]] = None,
        max_agents: int = 4,
    ) -> List[str]:
        """Select appropriate agents based on project idea.
        
        Args:
            idea: Project idea/description
            force_agents: List of agent names to force include
            max_agents: Maximum number of agents to select
            
        Returns:
            List of selected agent names
        """
        analysis = self.analyze_idea(idea)
        selected_agents = set()
        
        # Add forced agents
        if force_agents:
            for agent in force_agents:
                if agent in self.available_agents:
                    selected_agents.add(agent)
                else:
                    logger.warning(f"Forced agent not available: {agent}")
        
        # Domain-based selection
        domain_agent_map = {
            "web": ["fullstack-engineer"],
            "mobile": ["fullstack-engineer"],
            "ml": ["ml-dl-engineer"],
            "data": ["ml-dl-engineer", "fullstack-engineer"],
            "devops": ["devops-engineer"],
            "desktop": ["fullstack-engineer"],
            "game": ["fullstack-engineer"],
            "blockchain": ["fullstack-engineer"],
            "testing": ["qa-engineer"],
        }
        
        for domain in analysis["domains"]:
            if domain in domain_agent_map:
                selected_agents.update(domain_agent_map[domain])
        
        # Technology-based selection
        for tech in analysis["technologies"]:
            if tech in self.tech_stack_agents:
                selected_agents.update(self.tech_stack_agents[tech])
        
        # Complexity-based selection
        if analysis["complexity"] == "high":
            # High complexity projects need more specialized agents
            selected_agents.add("devops-engineer")
            selected_agents.add("qa-engineer")
        elif analysis["complexity"] == "medium":
            # Medium complexity might need QA
            if len(selected_agents) < max_agents:
                selected_agents.add("qa-engineer")
        
        # Default fallback
        if not selected_agents:
            selected_agents.add("fullstack-engineer")
        
        # Always include QA for substantial projects
        if analysis["word_count"] > 20 and "qa-engineer" not in selected_agents:
            selected_agents.add("qa-engineer")
        
        # Limit to max_agents
        result = list(selected_agents)[:max_agents]
        
        # Ensure we have at least one agent
        if not result and self.available_agents:
            result = ["fullstack-engineer"]
        
        logger.info(f"Selected agents: {result}")
        return result
    
    def augment_agents(
        self,
        selected_agents: List[str],
        idea: str,
        custom_requirements: Optional[Dict[str, any]] = None,
    ) -> Dict[str, AgentConfig]:
        """Augment selected agents with custom requirements.
        
        Args:
            selected_agents: List of selected agent names
            idea: Project idea for context
            custom_requirements: Custom requirements for agents
            
        Returns:
            Dictionary of augmented agent configurations
        """
        augmented_agents = {}
        analysis = self.analyze_idea(idea)
        
        for agent_name in selected_agents:
            if agent_name not in self.available_agents:
                logger.warning(f"Agent not available for augmentation: {agent_name}")
                continue
            
            # Start with base agent config
            base_config = self.available_agents[agent_name]
            
            # Create augmented content
            augmented_content = self._augment_agent_content(
                base_config, analysis, custom_requirements
            )
            
            # Create new config with augmented content
            augmented_config = AgentConfig(
                name=base_config.name,
                description=base_config.description,
                tools=base_config.tools,
                parallelism=base_config.parallelism,
                patterns=base_config.patterns,
                content=augmented_content,
                file_path=base_config.file_path,
            )
            
            augmented_agents[agent_name] = augmented_config
            logger.debug(f"Augmented agent: {agent_name}")
        
        logger.info(f"Augmented {len(augmented_agents)} agents")
        return augmented_agents
    
    def _augment_agent_content(
        self,
        agent_config: AgentConfig,
        analysis: Dict[str, any],
        custom_requirements: Optional[Dict[str, any]] = None,
    ) -> str:
        """Augment agent content with project-specific information.
        
        Args:
            agent_config: Base agent configuration
            analysis: Project analysis results
            custom_requirements: Custom requirements
            
        Returns:
            Augmented agent content
        """
        base_content = agent_config.content
        
        # Add project context
        context_section = "\n\n## Project Context\n\n"
        context_section += f"- **Domains**: {', '.join(analysis['domains'])}\n"
        context_section += f"- **Technologies**: {', '.join(analysis['technologies'])}\n"
        context_section += f"- **Complexity**: {analysis['complexity']}\n"
        context_section += f"- **Project Type**: {analysis['project_type']}\n"
        
        # Add domain-specific guidance
        if analysis["domains"]:
            guidance_section = "\n\n## Domain-Specific Guidance\n\n"
            
            if "web" in analysis["domains"]:
                guidance_section += "- Focus on responsive design and modern web standards\n"
                guidance_section += "- Implement proper SEO and accessibility features\n"
                guidance_section += "- Use modern build tools and optimization techniques\n"
            
            if "ml" in analysis["domains"]:
                guidance_section += "- Prioritize data quality and model validation\n"
                guidance_section += "- Implement proper experiment tracking and versioning\n"
                guidance_section += "- Consider model deployment and monitoring needs\n"
            
            if "devops" in analysis["domains"]:
                guidance_section += "- Focus on automation and infrastructure as code\n"
                guidance_section += "- Implement comprehensive monitoring and alerting\n"
                guidance_section += "- Ensure security and compliance requirements\n"
            
            base_content += guidance_section
        
        # Add custom requirements
        if custom_requirements:
            custom_section = "\n\n## Custom Requirements\n\n"
            for key, value in custom_requirements.items():
                custom_section += f"- **{key.title()}**: {value}\n"
            base_content += custom_section
        
        # Add project context
        base_content += context_section
        
        return base_content
    
    def get_agent_combinations(self, max_combinations: int = 10) -> List[Tuple[str, ...]]:
        """Get recommended agent combinations.
        
        Args:
            max_combinations: Maximum number of combinations to return
            
        Returns:
            List of agent combination tuples
        """
        combinations = [
            ("fullstack-engineer",),
            ("fullstack-engineer", "qa-engineer"),
            ("fullstack-engineer", "devops-engineer"),
            ("ml-dl-engineer",),
            ("ml-dl-engineer", "fullstack-engineer"),
            ("fullstack-engineer", "qa-engineer", "devops-engineer"),
            ("ml-dl-engineer", "devops-engineer"),
            ("devops-engineer",),
            ("qa-engineer",),
            ("ml-dl-engineer", "qa-engineer"),
        ]
        
        # Filter to only include available agents
        available_combinations = []
        for combo in combinations:
            if all(agent in self.available_agents for agent in combo):
                available_combinations.append(combo)
        
        return available_combinations[:max_combinations]
    
    def validate_agent_selection(self, selected_agents: List[str]) -> List[str]:
        """Validate agent selection and return any issues.
        
        Args:
            selected_agents: List of selected agent names
            
        Returns:
            List of validation issues (empty if valid)
        """
        issues = []
        
        if not selected_agents:
            issues.append("No agents selected")
            return issues
        
        # Check agent availability
        for agent_name in selected_agents:
            if agent_name not in self.available_agents:
                issues.append(f"Agent not available: {agent_name}")
        
        # Check for conflicting agents (if any rules exist)
        # Currently no conflicts defined
        
        # Check for minimum requirements
        available_selected = [a for a in selected_agents if a in self.available_agents]
        
        if len(available_selected) == 0:
            issues.append("No valid agents selected")
        
        # Warn about potential over-engineering
        if len(available_selected) > 4:
            issues.append("Too many agents selected - may lead to complexity")
        
        return issues