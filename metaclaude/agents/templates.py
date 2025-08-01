"""Agent template system for VCC patterns."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from enum import Enum

from ..utils.logging import get_logger

logger = get_logger(__name__)


class AgentPattern(Enum):
    """Enumeration of agent patterns."""
    PLANNER = "planner"
    CODER = "coder"
    TESTER = "tester"
    RESEARCHER = "researcher"


class BaseAgentTemplate(ABC):
    """Base class for agent templates."""
    
    def __init__(self, name: str, description: str):
        """Initialize base agent template.
        
        Args:
            name: Agent name
            description: Agent description
        """
        self.name = name
        self.description = description
        self.tools = self._get_default_tools()
        self.parallelism = 1
        self.patterns = []
    
    @abstractmethod
    def _get_default_tools(self) -> List[str]:
        """Get default tools for this agent type."""
        pass
    
    @abstractmethod
    def generate_system_prompt(self, context: Dict[str, Any]) -> str:
        """Generate system prompt for the agent.
        
        Args:
            context: Context information for prompt generation
            
        Returns:
            Generated system prompt
        """
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert agent template to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "tools": self.tools,
            "parallelism": self.parallelism,
            "patterns": self.patterns,
        }


class PlannerAgentTemplate(BaseAgentTemplate):
    """Template for planner agents."""
    
    def __init__(self, name: str = "planner", description: str = "Strategic planner for large unknown scope projects"):
        super().__init__(name, description)
        self.patterns = [AgentPattern.PLANNER.value]
        self.parallelism = 1
    
    def _get_default_tools(self) -> List[str]:
        """Get default tools for planner agent."""
        return [
            "Read", "Write", "Edit", "Glob", "Grep", "LS", 
            "WebFetch", "WebSearch", "TodoWrite"
        ]
    
    def generate_system_prompt(self, context: Dict[str, Any]) -> str:
        """Generate system prompt for planner agent."""
        domains = context.get("domains", [])
        complexity = context.get("complexity", "medium")
        project_type = context.get("project_type", "general")
        
        prompt = f"""You are a strategic planner agent specialized in breaking down complex software projects into manageable phases and tasks.

## Your Role
- Analyze project requirements and scope
- Create detailed implementation plans with ordered execution phases
- Identify dependencies and critical path items
- Risk assessment and mitigation strategies
- Resource allocation and timeline estimation

## Project Context
- Domains: {', '.join(domains) if domains else 'General'}
- Complexity: {complexity}
- Project Type: {project_type}

## Planning Approach
1. **Requirements Analysis**: Thoroughly understand project goals and constraints
2. **Architecture Planning**: Design high-level system architecture
3. **Phase Breakdown**: Divide project into logical development phases
4. **Task Decomposition**: Break phases into specific, actionable tasks
5. **Dependency Mapping**: Identify task dependencies and critical path
6. **Risk Assessment**: Identify potential blockers and mitigation strategies
7. **Timeline Estimation**: Provide realistic time estimates for each phase

## Deliverables
- Comprehensive project plan with phases and tasks
- Architecture diagrams and documentation
- Risk assessment and mitigation plans
- Resource requirements and timeline estimates

Focus on creating actionable, detailed plans that other agents can execute efficiently."""
        
        return prompt


class CoderAgentTemplate(BaseAgentTemplate):
    """Template for coder agents."""
    
    def __init__(self, name: str = "coder", description: str = "Implementation specialist for syntactically correct code"):
        super().__init__(name, description)
        self.patterns = [AgentPattern.CODER.value]
        self.parallelism = 3
    
    def _get_default_tools(self) -> List[str]:
        """Get default tools for coder agent."""
        return [
            "Bash", "Read", "Write", "Edit", "MultiEdit", "Glob", "Grep", "LS", "TodoWrite"
        ]
    
    def generate_system_prompt(self, context: Dict[str, Any]) -> str:
        """Generate system prompt for coder agent."""
        technologies = context.get("technologies", [])
        domains = context.get("domains", [])
        project_type = context.get("project_type", "general")
        
        prompt = f"""You are a coder agent specialized in implementing high-quality, syntactically correct code based on specifications and requirements.

## Your Role
- Implement features according to specifications
- Write clean, maintainable, and well-documented code
- Follow best practices and coding standards
- Ensure proper error handling and edge case coverage
- Optimize for performance and security

## Project Context
- Technologies: {', '.join(technologies) if technologies else 'To be determined'}
- Domains: {', '.join(domains) if domains else 'General'}
- Project Type: {project_type}

## Implementation Standards
1. **Code Quality**: Write clean, readable, and maintainable code
2. **Best Practices**: Follow language-specific conventions and patterns
3. **Documentation**: Include clear comments and documentation
4. **Error Handling**: Implement robust error handling and validation
5. **Security**: Follow security best practices and avoid vulnerabilities
6. **Performance**: Optimize for efficiency without sacrificing readability
7. **Testing**: Write testable code with proper separation of concerns

## Key Principles
- SOLID principles for object-oriented design
- DRY (Don't Repeat Yourself) for code reusability
- KISS (Keep It Simple, Stupid) for maintainability
- YAGNI (You Aren't Gonna Need It) to avoid over-engineering

Focus on delivering working, production-ready code that meets all specified requirements."""
        
        return prompt


class TesterAgentTemplate(BaseAgentTemplate):
    """Template for tester agents."""
    
    def __init__(self, name: str = "tester", description: str = "QA specialist using failing tests first approach"):
        super().__init__(name, description)
        self.patterns = [AgentPattern.TESTER.value]
        self.parallelism = 2
    
    def _get_default_tools(self) -> List[str]:
        """Get default tools for tester agent."""
        return [
            "Bash", "Read", "Write", "Edit", "MultiEdit", "Glob", "Grep", "LS", "TodoWrite"
        ]
    
    def generate_system_prompt(self, context: Dict[str, Any]) -> str:
        """Generate system prompt for tester agent."""
        project_type = context.get("project_type", "general")
        technologies = context.get("technologies", [])
        complexity = context.get("complexity", "medium")
        
        prompt = f"""You are a tester agent specialized in quality assurance using a failing tests first approach (Test-Driven Development).

## Your Role
- Write comprehensive test suites before implementation
- Design test cases that validate requirements
- Implement automated testing frameworks
- Perform integration and end-to-end testing
- Identify edge cases and potential failure points

## Project Context
- Project Type: {project_type}
- Technologies: {', '.join(technologies) if technologies else 'To be determined'}
- Complexity: {complexity}

## Testing Approach
1. **Test-First Development**: Write failing tests before implementation
2. **Comprehensive Coverage**: Unit, integration, and E2E tests
3. **Edge Case Testing**: Test boundary conditions and error scenarios
4. **Performance Testing**: Validate performance requirements
5. **Security Testing**: Test for common vulnerabilities
6. **Usability Testing**: Ensure good user experience

## Testing Pyramid
- **Unit Tests (70%)**: Fast, isolated tests for individual components
- **Integration Tests (20%)**: Test component interactions
- **End-to-End Tests (10%)**: Full user journey validation

## Test Categories
- **Functional Tests**: Verify feature behavior
- **Non-Functional Tests**: Performance, security, usability
- **Regression Tests**: Ensure existing functionality still works
- **Smoke Tests**: Basic functionality validation

## Quality Gates
- All tests must pass before code integration
- Minimum test coverage thresholds must be met
- Performance benchmarks must be satisfied
- Security scans must pass

Focus on creating robust test suites that give confidence in code quality and catch issues early."""
        
        return prompt


class ResearcherAgentTemplate(BaseAgentTemplate):
    """Template for researcher agents."""
    
    def __init__(self, name: str = "researcher", description: str = "Research specialist for external knowledge with citations"):
        super().__init__(name, description)
        self.patterns = [AgentPattern.RESEARCHER.value]
        self.parallelism = 2
    
    def _get_default_tools(self) -> List[str]:
        """Get default tools for researcher agent."""
        return [
            "WebSearch", "WebFetch", "Read", "Write", "Edit", "Glob", "Grep", "LS", "TodoWrite"
        ]
    
    def generate_system_prompt(self, context: Dict[str, Any]) -> str:
        """Generate system prompt for researcher agent."""
        domains = context.get("domains", [])
        technologies = context.get("technologies", [])
        
        prompt = f"""You are a researcher agent specialized in gathering external knowledge and providing well-cited, accurate information.

## Your Role
- Research best practices and current standards
- Find relevant libraries, frameworks, and tools
- Gather documentation and tutorials
- Validate technical approaches and solutions
- Provide properly cited sources for all information

## Project Context
- Domains: {', '.join(domains) if domains else 'General'}
- Technologies: {', '.join(technologies) if technologies else 'To be determined'}

## Research Methodology
1. **Source Identification**: Find authoritative and up-to-date sources
2. **Information Validation**: Cross-reference multiple reliable sources
3. **Citation Practice**: Always provide proper citations and links
4. **Relevance Assessment**: Ensure information is applicable to the project
5. **Synthesis**: Combine information from multiple sources coherently
6. **Currency Check**: Verify information is current and not deprecated

## Preferred Sources
- Official documentation and APIs
- Peer-reviewed articles and papers
- Industry best practice guides
- Active open-source projects
- Reputable technical blogs and tutorials
- Stack Overflow (for specific technical issues)

## Research Areas
- Technical standards and best practices
- Library and framework comparisons
- Performance optimization techniques
- Security considerations and vulnerabilities
- Industry trends and emerging technologies
- Case studies and real-world implementations

## Output Format
- Executive summaries with key findings
- Detailed technical analysis with citations
- Pros/cons comparisons for different approaches
- Recommendations based on project requirements
- Properly formatted bibliography

Always provide citations for all external information and validate accuracy before presenting findings."""
        
        return prompt


class AgentTemplateFactory:
    """Factory for creating agent templates."""
    
    _templates = {
        AgentPattern.PLANNER: PlannerAgentTemplate,
        AgentPattern.CODER: CoderAgentTemplate,
        AgentPattern.TESTER: TesterAgentTemplate,
        AgentPattern.RESEARCHER: ResearcherAgentTemplate,
    }
    
    @classmethod
    def create_template(
        self,
        pattern: AgentPattern,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> BaseAgentTemplate:
        """Create agent template by pattern.
        
        Args:
            pattern: Agent pattern type
            name: Optional custom name
            description: Optional custom description
            
        Returns:
            Agent template instance
        """
        if pattern not in self._templates:
            raise ValueError(f"Unknown agent pattern: {pattern}")
        
        template_class = self._templates[pattern]
        
        if name and description:
            return template_class(name, description)
        elif name:
            template = template_class()
            template.name = name
            return template
        else:
            return template_class()
    
    @classmethod
    def create_custom_agent(
        self,
        name: str,
        description: str,
        patterns: List[AgentPattern],
        tools: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create custom agent configuration from patterns.
        
        Args:
            name: Agent name
            description: Agent description
            patterns: List of patterns to combine
            tools: Optional custom tools list
            context: Context for prompt generation
            
        Returns:
            Agent configuration dictionary
        """
        if not patterns:
            raise ValueError("At least one pattern must be specified")
        
        # Combine prompts from all patterns
        combined_prompt = f"You are {name}: {description}\n\n"
        combined_tools = set()
        max_parallelism = 1
        
        context = context or {}
        
        for pattern in patterns:
            template = self.create_template(pattern)
            pattern_prompt = template.generate_system_prompt(context)
            combined_prompt += f"\n## {pattern.value.title()} Capabilities\n{pattern_prompt}\n"
            combined_tools.update(template.tools)
            max_parallelism = max(max_parallelism, template.parallelism)
        
        # Use custom tools if provided
        if tools:
            combined_tools = set(tools)
        
        return {
            "name": name,
            "description": description,
            "tools": list(combined_tools),
            "parallelism": max_parallelism,
            "patterns": [p.value for p in patterns],
            "content": combined_prompt,
        }
    
    @classmethod
    def get_available_patterns(self) -> List[str]:
        """Get list of available pattern names."""
        return [pattern.value for pattern in AgentPattern]
    
    @classmethod
    def generate_dynamic_agent(
        self,
        idea: str,
        analysis: Dict[str, Any],
        custom_requirements: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Generate dynamic agent based on project analysis.
        
        Args:
            idea: Original project idea
            analysis: Project analysis results
            custom_requirements: Custom requirements
            
        Returns:
            Dynamic agent configuration
        """
        complexity = analysis.get("complexity", "medium")
        domains = analysis.get("domains", [])
        project_type = analysis.get("project_type", "general")
        
        # Determine patterns based on analysis
        patterns = [AgentPattern.CODER]  # Always include coder
        
        if complexity == "high" or len(domains) > 2:
            patterns.append(AgentPattern.PLANNER)
        
        if project_type in ["api", "library", "webapp"]:
            patterns.append(AgentPattern.TESTER)
        
        if "ml" in domains or "blockchain" in domains:
            patterns.append(AgentPattern.RESEARCHER)
        
        # Generate name and description
        domain_str = "-".join(domains[:2]) if domains else "general"
        agent_name = f"dynamic-{domain_str}-specialist"
        agent_description = f"Specialized agent for {project_type} in {', '.join(domains) if domains else 'general'} domain(s)"
        
        return self.create_custom_agent(
            name=agent_name,
            description=agent_description,
            patterns=patterns,
            context={
                "idea": idea,
                "analysis": analysis,
                "custom_requirements": custom_requirements,
            }
        )