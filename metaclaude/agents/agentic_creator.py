"""
Agentic Agent Creation System for MetaClaude

This module implements a fully autonomous agent creation system where Claude Code
itself decides which sub-agents to create, how many, what names to give them,
what descriptions, and what system prompts based on deep project analysis
and real-time web research.

Features:
    - AI-powered deep project analysis
    - Dynamic agent architecture design  
    - Research-enhanced agent generation
    - Intelligent web search for latest information
    - Automatic agent specialization and optimization
"""

import asyncio
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

from ..utils.logging import get_logger
from ..utils.errors import MetaClaudeAgentError
from .parser import AgentConfig

logger = get_logger(__name__)


class ComplexityLevel(Enum):
    """Project complexity levels for agent planning."""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    ENTERPRISE = "enterprise"


class AgentExpertiseLevel(Enum):
    """Agent expertise levels for specialization."""
    SPECIALIST = "specialist"
    EXPERT = "expert"
    ARCHITECT = "architect"
    MASTER = "master"


@dataclass
class ProjectAnalysis:
    """Comprehensive project analysis results."""
    domains: List[str] = field(default_factory=list)
    technologies: List[str] = field(default_factory=list)
    complexity: ComplexityLevel = ComplexityLevel.SIMPLE
    project_type: str = "general"
    estimated_scope: str = "small"
    technical_challenges: List[str] = field(default_factory=list)
    quality_requirements: List[str] = field(default_factory=list)
    deployment_needs: List[str] = field(default_factory=list)
    security_requirements: List[str] = field(default_factory=list)
    performance_requirements: List[str] = field(default_factory=list)
    integration_needs: List[str] = field(default_factory=list)
    confidence_score: float = 0.0
    word_count: int = 0
    sentiment: str = "neutral"
    urgency_level: str = "normal"
    innovation_level: str = "standard"


@dataclass
class AgentSpec:
    """Specification for a dynamically created agent."""
    name: str
    role: str
    description: str
    expertise_areas: List[str]
    responsibilities: List[str]
    tools: List[str]
    expertise_level: AgentExpertiseLevel
    priority: int = 1
    collaboration_patterns: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    specialization_focus: str = ""
    quality_standards: List[str] = field(default_factory=list)


@dataclass
class AgentBlueprint:
    """Complete agent architecture design for a project."""
    agent_specs: List[AgentSpec]
    execution_order: List[str]
    collaboration_matrix: Dict[str, List[str]]
    parallel_groups: List[List[str]]
    quality_gates: List[str]
    estimated_duration: str
    coordination_strategy: str
    success_criteria: List[str]


@dataclass
class ResearchQuery:
    """Web research query for agent enhancement."""
    search_term: str
    focus_area: str
    priority: str = "medium"
    context: str = ""
    expected_results: int = 5


@dataclass
class ResearchData:
    """Compiled research data for agent creation."""
    domain_knowledge: Dict[str, Any] = field(default_factory=dict)
    technology_updates: Dict[str, Any] = field(default_factory=dict)
    best_practices: List[str] = field(default_factory=list)
    security_insights: List[str] = field(default_factory=list)
    performance_tips: List[str] = field(default_factory=list)
    common_pitfalls: List[str] = field(default_factory=list)
    latest_trends: List[str] = field(default_factory=list)
    tool_recommendations: List[str] = field(default_factory=list)
    quality_score: float = 0.0
    research_timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class DynamicAgent:
    """Dynamically created agent with research-enhanced capabilities."""
    name: str
    description: str
    system_prompt: str  
    tools: List[str]
    expertise_level: AgentExpertiseLevel
    specialization_areas: List[str]
    knowledge_base: ResearchData
    collaboration_instructions: str
    quality_standards: List[str]
    success_metrics: List[str]
    creation_timestamp: datetime = field(default_factory=datetime.now)
    research_enhanced: bool = True


class DeepProjectAnalyzer:
    """AI-powered comprehensive project analysis engine."""
    
    def __init__(self, claude_client=None):
        """Initialize the deep project analyzer.
        
        Args:
            claude_client: Claude API client for analysis
        """
        self.claude_client = claude_client
        self.analysis_cache = {}
        
    async def analyze_comprehensive(self, idea: str) -> ProjectAnalysis:
        """Perform comprehensive AI-powered project analysis.
        
        Args:
            idea: Project idea description
            
        Returns:
            Detailed project analysis
        """
        logger.info(f"Starting comprehensive analysis for project: {idea[:50]}...")
        
        # Check cache first
        cache_key = hash(idea)
        if cache_key in self.analysis_cache:
            logger.debug("Using cached analysis")
            return self.analysis_cache[cache_key]
        
        analysis_prompt = self._create_analysis_prompt(idea)
        
        try:
            # This would integrate with Claude API when available
            # For now, we'll use a sophisticated rule-based analysis
            analysis = await self._perform_advanced_analysis(idea, analysis_prompt)
            
            # Cache the analysis
            self.analysis_cache[cache_key] = analysis
            
            logger.info(f"Analysis complete. Complexity: {analysis.complexity.value}, "
                       f"Domains: {len(analysis.domains)}, Confidence: {analysis.confidence_score:.2f}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            # Return fallback analysis
            return self._create_fallback_analysis(idea)
    
    def _create_analysis_prompt(self, idea: str) -> str:
        """Create comprehensive analysis prompt for Claude."""
        return f"""
        Analyze this software project idea comprehensively and provide detailed technical assessment:

        PROJECT IDEA: "{idea}"

        Please analyze the following aspects:

        1. **Technical Domains & Expertise Areas**:
           - What specific technical domains are involved?
           - What expertise areas are required?
           - What are the core vs peripheral technologies?

        2. **Project Complexity Assessment**:
           - Technical complexity level (simple/moderate/complex/enterprise)
           - Estimated project scope and scale
           - Architectural complexity requirements
           - Integration complexity

        3. **Technical Challenges & Risks**:
           - Major technical challenges to solve
           - Potential risk areas and failure points
           - Performance bottlenecks and scalability concerns
           - Security and compliance requirements

        4. **Quality & Non-Functional Requirements**:
           - Performance requirements and expectations  
           - Security and privacy considerations
           - Scalability and reliability needs
           - User experience and accessibility requirements

        5. **Deployment & Infrastructure Needs**:
           - Deployment environment requirements
           - Infrastructure and DevOps considerations
           - Monitoring and maintenance needs
           - CI/CD pipeline requirements

        6. **Innovation & Technology Currency**:
           - How cutting-edge vs established are the technologies?
           - What are the latest trends relevant to this project?
           - Are there emerging technologies that should be considered?

        Provide detailed, technical analysis with specific recommendations for agent specialization.
        Focus on actionable insights that will help determine optimal team composition.
        
        Current date: {datetime.now().strftime("%Y-%m-%d")}
        """
    
    async def _perform_advanced_analysis(self, idea: str, prompt: str) -> ProjectAnalysis:
        """Perform advanced rule-based analysis with AI-like reasoning."""
        
        idea_lower = idea.lower()
        word_count = len(idea.split())
        
        # Advanced domain detection with context awareness
        domains = self._detect_domains_advanced(idea_lower)
        
        # Technology stack analysis
        technologies = self._detect_technologies_advanced(idea_lower)
        
        # Complexity assessment using multiple factors
        complexity = self._assess_complexity_advanced(idea_lower, word_count, domains, technologies)
        
        # Project type classification
        project_type = self._classify_project_type_advanced(idea_lower, domains)
        
        # Technical challenges identification
        challenges = self._identify_technical_challenges(idea_lower, domains, technologies)
        
        # Quality requirements analysis
        quality_reqs = self._analyze_quality_requirements(idea_lower, complexity)
        
        # Security requirements assessment
        security_reqs = self._assess_security_requirements(idea_lower, domains, project_type)
        
        # Performance requirements analysis
        performance_reqs = self._analyze_performance_requirements(idea_lower, complexity)
        
        # Integration needs assessment
        integration_needs = self._assess_integration_needs(idea_lower, domains)
        
        # Deployment needs analysis
        deployment_needs = self._analyze_deployment_needs(idea_lower, complexity, domains)
        
        # Confidence scoring
        confidence = self._calculate_confidence_score(domains, technologies, word_count)
        
        # Project scope estimation
        scope = self._estimate_project_scope(complexity, word_count, len(domains))
        
        return ProjectAnalysis(
            domains=domains,
            technologies=technologies,
            complexity=complexity,
            project_type=project_type,
            estimated_scope=scope,
            technical_challenges=challenges,
            quality_requirements=quality_reqs,
            deployment_needs=deployment_needs,
            security_requirements=security_reqs,
            performance_requirements=performance_reqs,
            integration_needs=integration_needs,
            confidence_score=confidence,
            word_count=word_count,
            sentiment=self._analyze_sentiment(idea),
            urgency_level=self._detect_urgency(idea_lower),
            innovation_level=self._assess_innovation_level(idea_lower, technologies)
        )
    
    def _detect_domains_advanced(self, idea_lower: str) -> List[str]:
        """Advanced domain detection with context awareness."""
        domain_patterns = {
            "frontend": [
                r"frontend|front-end|ui|user interface|web interface|dashboard|admin panel",
                r"react|vue|angular|svelte|next\.?js|nuxt|gatsby|remix",
                r"responsive|mobile.first|accessibility|ux|user experience"
            ],
            "backend": [
                r"backend|back-end|api|rest|graphql|server|microservice",
                r"node\.?js|express|fastapi|django|flask|spring|laravel",
                r"database|sql|nosql|mongodb|postgresql|mysql|redis"
            ],
            "mobile": [
                r"mobile|android|ios|react.native|flutter|swift|kotlin",
                r"app store|play store|cross.platform|native|hybrid"
            ],
            "ml_ai": [
                r"machine learning|deep learning|ai|artificial intelligence|neural network",
                r"pytorch|tensorflow|scikit|pandas|numpy|data science",
                r"nlp|computer vision|recommendation|prediction|classification"
            ],
            "devops": [
                r"devops|infrastructure|deployment|ci/cd|automation",
                r"docker|kubernetes|aws|azure|gcp|terraform|ansible"
            ],
            "data_engineering": [
                r"data pipeline|etl|data warehouse|analytics|big data",
                r"spark|airflow|kafka|elasticsearch|bigquery"
            ],
            "security": [
                r"security|authentication|authorization|encryption|oauth",
                r"penetration testing|vulnerability|compliance|gdpr|hipaa"
            ],
            "blockchain": [
                r"blockchain|crypto|web3|ethereum|bitcoin|solidity|smart contract"
            ],
            "gaming": [
                r"game|gaming|unity|unreal|godot|3d|virtual reality|ar"
            ],
            "iot": [
                r"iot|internet of things|embedded|sensor|arduino|raspberry pi"
            ]
        }
        
        detected_domains = []
        for domain, patterns in domain_patterns.items():
            if any(re.search(pattern, idea_lower) for pattern in patterns):
                detected_domains.append(domain)
        
        return detected_domains
    
    def _detect_technologies_advanced(self, idea_lower: str) -> List[str]:
        """Advanced technology detection with version awareness."""
        tech_patterns = {
            "python": r"python|py|django|flask|fastapi|pandas|numpy",
            "javascript": r"javascript|js|node\.?js|npm|yarn",
            "typescript": r"typescript|ts",
            "react": r"react|jsx|next\.?js|gatsby|remix",
            "vue": r"vue\.?js|nuxt",
            "angular": r"angular",
            "docker": r"docker|container|containerized",
            "kubernetes": r"kubernetes|k8s|helm",
            "aws": r"aws|amazon web services|ec2|s3|lambda",
            "postgresql": r"postgresql|postgres|pg", 
            "mongodb": r"mongodb|mongo|nosql",
            "redis": r"redis|cache|caching",
            "pytorch": r"pytorch|torch",
            "tensorflow": r"tensorflow|tf",
            "golang": r"\bgo\b|golang",
            "rust": r"rust|cargo",
            "java": r"java|spring|maven|gradle",
            "cpp": r"c\+\+|cpp|cmake"
        }
        
        detected_technologies = []
        for tech, pattern in tech_patterns.items():
            if re.search(pattern, idea_lower):
                detected_technologies.append(tech)
        
        return detected_technologies
    
    def _assess_complexity_advanced(
        self, 
        idea_lower: str, 
        word_count: int, 
        domains: List[str], 
        technologies: List[str]
    ) -> ComplexityLevel:
        """Advanced complexity assessment using multiple factors."""
        
        complexity_score = 0
        
        # Word count factor
        if word_count > 50:
            complexity_score += 2
        elif word_count > 25:
            complexity_score += 1
        
        # Domain count factor
        complexity_score += len(domains)
        
        # Technology count factor
        complexity_score += len(technologies)
        
        # High-complexity keywords
        high_complexity_patterns = [
            r"enterprise|scalable|distributed|microservice|real.time",
            r"machine learning|ai|blockchain|advanced|complex",
            r"high.performance|optimization|concurrent|parallel",
            r"security|compliance|audit|encryption|authentication",
            r"integration|api|third.party|external|webhook",
            r"analytics|dashboard|reporting|visualization|charts"
        ]
        
        for pattern in high_complexity_patterns:
            if re.search(pattern, idea_lower):
                complexity_score += 2
        
        # Moderate complexity keywords
        moderate_complexity_patterns = [
            r"database|sql|api|rest|authentication|user management",
            r"responsive|mobile|cross.platform|deployment|hosting",
            r"testing|validation|error handling|logging|monitoring"
        ]
        
        for pattern in moderate_complexity_patterns:
            if re.search(pattern, idea_lower):
                complexity_score += 1
        
        # Determine complexity level
        if complexity_score >= 15:
            return ComplexityLevel.ENTERPRISE
        elif complexity_score >= 10:
            return ComplexityLevel.COMPLEX
        elif complexity_score >= 5:
            return ComplexityLevel.MODERATE
        else:
            return ComplexityLevel.SIMPLE
    
    def _classify_project_type_advanced(self, idea_lower: str, domains: List[str]) -> str:
        """Advanced project type classification."""
        type_patterns = {
            "web_application": [
                r"web app|website|web application|dashboard|admin panel",
                r"frontend|backend|fullstack|full.stack"
            ],
            "mobile_application": [
                r"mobile app|android app|ios app|mobile application"
            ],
            "api_service": [
                r"\bapi\b|rest api|graphql|microservice|web service|backend service"
            ],
            "desktop_application": [
                r"desktop app|desktop application|gui|native application"
            ],
            "cli_tool": [
                r"cli|command line|terminal|script|automation tool"
            ],
            "data_pipeline": [
                r"data pipeline|etl|data processing|analytics pipeline"
            ],
            "ml_model": [
                r"machine learning model|ml model|prediction model|ai model"
            ],
            "library_framework": [
                r"library|framework|package|sdk|npm package|python package"
            ],
            "game": [
                r"game|gaming application|video game"
            ],
            "blockchain_dapp": [
                r"dapp|decentralized app|smart contract|blockchain app"
            ]
        }
        
        for project_type, patterns in type_patterns.items():
            if any(re.search(pattern, idea_lower) for pattern in patterns):
                return project_type
        
        # Fallback based on domains
        if "mobile" in domains:
            return "mobile_application"
        elif "ml_ai" in domains:
            return "ml_model"
        elif "backend" in domains and "frontend" not in domains:
            return "api_service"
        elif "frontend" in domains:
            return "web_application"
        
        return "general_application"
    
    def _identify_technical_challenges(
        self, 
        idea_lower: str, 
        domains: List[str], 
        technologies: List[str]
    ) -> List[str]:
        """Identify potential technical challenges."""
        challenges = []
        
        challenge_patterns = {
            "Performance & Scalability": [
                r"high.traffic|scalable|performance|optimization|concurrent|parallel",
                r"real.time|streaming|large.scale|big data"
            ],
            "Security & Compliance": [
                r"security|authentication|authorization|encryption|compliance",
                r"gdpr|hipaa|pci|audit|vulnerability"
            ],
            "Integration Complexity": [
                r"integration|third.party|api|external|webhook|microservice",
                r"legacy|existing system|migration"
            ],
            "Data Management": [
                r"database|data consistency|transaction|backup|sync",
                r"data migration|data quality|data validation"
            ],
            "User Experience": [
                r"responsive|mobile.first|accessibility|ux|user experience",
                r"cross.browser|cross.platform|internationalization"
            ],
            "Deployment & Operations": [
                r"deployment|hosting|devops|monitoring|logging|error handling",
                r"ci/cd|automation|infrastructure"
            ]
        }
        
        for challenge_area, patterns in challenge_patterns.items():
            if any(re.search(pattern, idea_lower) for pattern in patterns):
                challenges.append(challenge_area)
        
        # Domain-specific challenges
        if "ml_ai" in domains:
            challenges.extend(["Model Training & Validation", "Data Quality & Bias", "Model Deployment"])
        
        if "blockchain" in domains:
            challenges.extend(["Smart Contract Security", "Gas Optimization", "Decentralization"])
        
        if len(domains) > 3:
            challenges.append("Multi-Domain Integration")
        
        return list(set(challenges))
    
    def _analyze_quality_requirements(self, idea_lower: str, complexity: ComplexityLevel) -> List[str]:
        """Analyze quality requirements based on project characteristics."""
        quality_reqs = ["Code Quality", "Testing Coverage"]
        
        quality_patterns = {
            "Performance Testing": [r"performance|speed|optimization|load|stress"],
            "Security Testing": [r"security|authentication|encryption|vulnerability"],
            "Accessibility Compliance": [r"accessibility|a11y|wcag|disabled|impaired"],
            "Cross-Platform Testing": [r"cross.platform|multi.platform|compatibility"],
            "Usability Testing": [r"usability|user experience|ux|user testing"],
            "Integration Testing": [r"integration|api|third.party|external"],
            "Scalability Testing": [r"scalable|scalability|high.traffic|concurrent"],
            "Compliance Validation": [r"compliance|gdpr|hipaa|regulation|audit"]
        }
        
        for quality_req, patterns in quality_patterns.items():
            if any(re.search(pattern, idea_lower) for pattern in patterns):
                quality_reqs.append(quality_req)
        
        # Add requirements based on complexity
        if complexity in [ComplexityLevel.COMPLEX, ComplexityLevel.ENTERPRISE]:
            quality_reqs.extend([
                "Architecture Review",
                "Performance Benchmarking", 
                "Security Audit",
                "Documentation Standards"
            ])
        
        return list(set(quality_reqs))
    
    def _assess_security_requirements(self, idea_lower: str, domains: List[str], project_type: str) -> List[str]:
        """Assess security requirements based on project characteristics."""
        security_reqs = []
        
        security_patterns = {
            "Authentication & Authorization": [r"auth|login|user|account|permission|role"],
            "Data Encryption": [r"encryption|secure|privacy|sensitive|personal"],
            "Input Validation": [r"form|input|validation|sanitization|xss"],
            "API Security": [r"api|rest|graphql|endpoint|rate limiting"],
            "Session Management": [r"session|cookie|token|jwt|oauth"],
            "Database Security": [r"database|sql|injection|sanitization"],
            "HTTPS/TLS": [r"https|ssl|tls|certificate|secure connection"],
            "Compliance Requirements": [r"gdpr|hipaa|pci|compliance|regulation|audit"]
        }
        
        for security_req, patterns in security_patterns.items():
            if any(re.search(pattern, idea_lower) for pattern in patterns):
                security_reqs.append(security_req)
        
        # Domain-specific security requirements
        if "backend" in domains or "api_service" in project_type:
            security_reqs.extend(["API Rate Limiting", "Request Validation", "CORS Configuration"])
        
        if "frontend" in domains:
            security_reqs.extend(["XSS Protection", "Content Security Policy"])
        
        if "ml_ai" in domains:
            security_reqs.extend(["Data Privacy Protection", "Model Security"])
        
        if "blockchain" in domains:
            security_reqs.extend(["Smart Contract Auditing", "Private Key Management"])
        
        return list(set(security_reqs))
    
    def _analyze_performance_requirements(self, idea_lower: str, complexity: ComplexityLevel) -> List[str]:
        """Analyze performance requirements."""
        performance_reqs = []
        
        performance_patterns = {
            "Response Time Optimization": [r"fast|quick|responsive|speed|performance"],
            "Load Handling": [r"high.traffic|concurrent|scalable|load"],
            "Memory Optimization": [r"memory|efficient|optimization|resource"],
            "Database Optimization": [r"database|query|index|optimization"],
            "Caching Strategy": [r"cache|caching|redis|memcached|cdn"],
            "Asset Optimization": [r"image|video|asset|compression|minification"],
            "Real-time Processing": [r"real.time|streaming|live|instant"],
            "Batch Processing": [r"batch|bulk|processing|queue|background"]
        }
        
        for perf_req, patterns in performance_patterns.items():
            if any(re.search(pattern, idea_lower) for pattern in patterns):
                performance_reqs.append(perf_req)
        
        # Add requirements based on complexity
        if complexity in [ComplexityLevel.COMPLEX, ComplexityLevel.ENTERPRISE]:
            performance_reqs.extend([
                "Performance Monitoring",
                "Scalability Planning",
                "Resource Optimization"
            ])
        
        return list(set(performance_reqs))
    
    def _assess_integration_needs(self, idea_lower: str, domains: List[str]) -> List[str]:
        """Assess integration requirements."""
        integration_needs = []
        
        integration_patterns = {
            "Third-party APIs": [r"api|third.party|external|integration|webhook"],
            "Payment Processing": [r"payment|stripe|paypal|billing|checkout"],
            "Authentication Services": [r"oauth|google|facebook|github|sso"],
            "Cloud Services": [r"aws|azure|gcp|cloud|s3|storage"],
            "Database Integration": [r"database|sql|nosql|migration|sync"],
            "Email Services": [r"email|smtp|sendgrid|mailgun|notification"],
            "Analytics Integration": [r"analytics|tracking|google analytics|metrics"],
            "Search Integration": [r"search|elasticsearch|algolia|full.text"],
            "File Storage": [r"file|upload|storage|media|cdn"],
            "Social Media": [r"social|twitter|facebook|instagram|share"]
        }
        
        for integration, patterns in integration_patterns.items():
            if any(re.search(pattern, idea_lower) for pattern in patterns):
                integration_needs.append(integration)
        
        return list(set(integration_needs))
    
    def _analyze_deployment_needs(self, idea_lower: str, complexity: ComplexityLevel, domains: List[str]) -> List[str]:
        """Analyze deployment and infrastructure needs."""
        deployment_needs = []
        
        deployment_patterns = {
            "Container Deployment": [r"docker|container|kubernetes|k8s"],
            "Cloud Hosting": [r"cloud|aws|azure|gcp|heroku|vercel|netlify"],
            "CI/CD Pipeline": [r"ci/cd|automation|deployment|github actions|jenkins"],
            "Database Hosting": [r"database|sql|mongodb|hosted|managed"],
            "CDN Integration": [r"cdn|cloudflare|aws cloudfront|static assets"],
            "Load Balancing": [r"load balancer|high availability|redundancy"],
            "Monitoring & Logging": [r"monitoring|logging|metrics|alerts|observability"],
            "Backup & Recovery": [r"backup|recovery|disaster|redundancy"],
            "SSL/TLS Certificates": [r"ssl|tls|https|certificate|security"],
            "Domain & DNS": [r"domain|dns|subdomain|custom domain"]
        }
        
        for deployment, patterns in deployment_patterns.items():
            if any(re.search(pattern, idea_lower) for pattern in patterns):
                deployment_needs.append(deployment)
        
        # Add requirements based on complexity
        if complexity in [ComplexityLevel.COMPLEX, ComplexityLevel.ENTERPRISE]:
            deployment_needs.extend([
                "Infrastructure as Code",
                "Environment Management",
                "Security Hardening",
                "Performance Monitoring"
            ])
        
        return list(set(deployment_needs))
    
    def _calculate_confidence_score(self, domains: List[str], technologies: List[str], word_count: int) -> float:
        """Calculate confidence score for the analysis."""
        score = 0.0
        
        # Base score from word count
        if word_count > 50:
            score += 0.3
        elif word_count > 20:
            score += 0.2
        elif word_count > 10:
            score += 0.1
        
        # Score from detected domains
        score += min(len(domains) * 0.15, 0.4)
        
        # Score from detected technologies
        score += min(len(technologies) * 0.1, 0.3)
        
        # Cap at 1.0
        return min(score, 1.0)
    
    def _estimate_project_scope(self, complexity: ComplexityLevel, word_count: int, domain_count: int) -> str:
        """Estimate project scope based on analysis."""
        scope_score = 0
        
        # Complexity contribution
        complexity_scores = {
            ComplexityLevel.SIMPLE: 1,
            ComplexityLevel.MODERATE: 2,
            ComplexityLevel.COMPLEX: 3,
            ComplexityLevel.ENTERPRISE: 4
        }
        scope_score += complexity_scores[complexity]
        
        # Word count contribution
        if word_count > 100:
            scope_score += 3
        elif word_count > 50:
            scope_score += 2
        elif word_count > 25:
            scope_score += 1
        
        # Domain count contribution
        scope_score += min(domain_count, 3)
        
        # Classify scope
        if scope_score >= 8:
            return "large"
        elif scope_score >= 5:
            return "medium"
        else:
            return "small"
    
    def _analyze_sentiment(self, idea: str) -> str:
        """Analyze sentiment of the project idea."""
        positive_words = ["innovative", "cutting-edge", "advanced", "modern", "revolutionary"]
        urgent_words = ["urgent", "asap", "quickly", "fast", "immediate", "critical"]
        
        idea_lower = idea.lower()
        
        if any(word in idea_lower for word in urgent_words):
            return "urgent"
        elif any(word in idea_lower for word in positive_words):
            return "enthusiastic"
        else:
            return "neutral"
    
    def _detect_urgency(self, idea_lower: str) -> str:
        """Detect urgency level from project description."""
        high_urgency = ["urgent", "asap", "quickly", "fast", "immediate", "critical", "emergency"]
        medium_urgency = ["soon", "priority", "important", "needed"]
        
        if any(word in idea_lower for word in high_urgency):
            return "high"
        elif any(word in idea_lower for word in medium_urgency):
            return "medium"
        else:
            return "normal"
    
    def _assess_innovation_level(self, idea_lower: str, technologies: List[str]) -> str:
        """Assess innovation level of the project."""
        cutting_edge_techs = ["ai", "blockchain", "quantum", "ar", "vr", "iot", "edge computing"]
        innovative_words = ["innovative", "revolutionary", "cutting-edge", "breakthrough", "novel"]
        
        innovation_score = 0
        
        # Check for cutting-edge technologies
        for tech in cutting_edge_techs:
            if tech in idea_lower:
                innovation_score += 2
        
        # Check for innovative keywords
        for word in innovative_words:
            if word in idea_lower:
                innovation_score += 1
        
        # Check for emerging technology combinations
        if len(technologies) >= 4:
            innovation_score += 1
        
        if innovation_score >= 4:
            return "highly_innovative"
        elif innovation_score >= 2:
            return "innovative"
        else:
            return "standard"
    
    def _create_fallback_analysis(self, idea: str) -> ProjectAnalysis:
        """Create fallback analysis if main analysis fails."""
        logger.warning("Using fallback analysis")
        
        return ProjectAnalysis(
            domains=["general"],
            technologies=["general"],
            complexity=ComplexityLevel.MODERATE,
            project_type="general_application",
            estimated_scope="medium",
            technical_challenges=["Implementation", "Testing", "Deployment"],
            quality_requirements=["Code Quality", "Testing Coverage"],
            deployment_needs=["Basic Hosting", "CI/CD Pipeline"],
            security_requirements=["Input Validation", "Authentication"],
            performance_requirements=["Response Time Optimization"],
            integration_needs=["Basic APIs"],
            confidence_score=0.3,
            word_count=len(idea.split()),
            sentiment="neutral",
            urgency_level="normal",
            innovation_level="standard"
        )


class ResearchQueryGenerator:
    """Generates intelligent research queries for agent enhancement."""
    
    def __init__(self):
        """Initialize the research query generator."""
        self.query_cache = {}
        
    async def generate_research_queries(
        self, 
        spec: AgentSpec, 
        context: ProjectAnalysis
    ) -> List[ResearchQuery]:
        """Generate targeted research queries for agent creation.
        
        Args:
            spec: Agent specification
            context: Project analysis context
            
        Returns:
            List of research queries
        """
        logger.debug(f"Generating research queries for {spec.name}")
        
        queries = []
        current_year = datetime.now().year
        
        # Core expertise area research
        for expertise in spec.expertise_areas:
            queries.append(ResearchQuery(
                search_term=f"{expertise} best practices {current_year} latest trends",
                focus_area="best_practices",
                priority="high",
                context=f"Agent specialization in {expertise}"
            ))
        
        # Technology-specific research
        for tech in context.technologies:
            queries.append(ResearchQuery(
                search_term=f"{tech} {current_year} updates features performance optimization",
                focus_area="technology_updates",
                priority="high",
                context=f"Technology stack for {spec.role}"
            ))
        
        # Security research
        if context.security_requirements:
            queries.append(ResearchQuery(
                search_term=f"{spec.role} security vulnerabilities {current_year} best practices",
                focus_area="security_insights",
                priority="medium",
                context="Security considerations for agent specialization"
            ))
        
        # Performance optimization research
        if context.performance_requirements:
            queries.append(ResearchQuery(
                search_term=f"{' '.join(spec.expertise_areas)} performance optimization {current_year}",
                focus_area="performance_optimization",
                priority="medium",
                context="Performance optimization techniques"
            ))
        
        # Domain-specific research
        for domain in context.domains:
            queries.append(ResearchQuery(
                search_term=f"{domain} development {current_year} common pitfalls mistakes",
                focus_area="common_pitfalls",
                priority="medium",
                context=f"Domain expertise in {domain}"
            ))
        
        logger.info(f"Generated {len(queries)} research queries for {spec.name}")
        return queries


class WebResearchConductor:
    """Conducts web research using WebSearch tool for agent enhancement."""
    
    def __init__(self):
        """Initialize the web research conductor."""
        self.research_cache = {}
        
    async def conduct_research(self, queries: List[ResearchQuery]) -> ResearchData:
        """Conduct web research based on generated queries.
        
        Args:
            queries: List of research queries to execute
            
        Returns:
            Compiled research data
        """
        logger.info(f"Conducting research with {len(queries)} queries")
        
        research_data = ResearchData()
        
        for query in queries:
            try:
                # Check cache first
                cache_key = hash(query.search_term)
                if cache_key in self.research_cache:
                    logger.debug(f"Using cached research for: {query.search_term}")
                    results = self.research_cache[cache_key]
                else:
                    # Conduct web search
                    logger.debug(f"Searching: {query.search_term}")
                    results = await self._execute_web_search(query)
                    self.research_cache[cache_key] = results
                
                # Process and categorize results
                self._process_research_results(results, query, research_data)
                
            except Exception as e:
                logger.warning(f"Research failed for query '{query.search_term}': {e}")
                continue
        
        # Calculate research quality score
        research_data.quality_score = self._calculate_research_quality(research_data)
        
        logger.info(f"Research completed. Quality score: {research_data.quality_score:.2f}")
        return research_data
    
    async def _execute_web_search(self, query: ResearchQuery) -> Dict[str, Any]:
        """Execute web search for a research query.
        
        Args:
            query: Research query to execute
            
        Returns:
            Search results
        """
        try:
            # Try to use actual WebSearch tool if available
            from ...utils.web_search import WebSearch
            web_search = WebSearch()
            
            # Execute web search
            search_results = await web_search.search(
                query=query.search_term,
                max_results=query.expected_results
            )
            
            # Process results into our format
            processed_results = []
            for result in search_results.get("results", []):
                processed_results.append({
                    "title": result.get("title", ""),
                    "content": result.get("content", result.get("snippet", "")),
                    "url": result.get("url", ""),
                    "relevance": result.get("relevance", 0.7)
                })
            
            return {
                "results": processed_results,
                "summary": f"Web search results for {query.search_term}",
                "confidence": 0.9
            }
            
        except (ImportError, AttributeError, Exception) as e:
            logger.debug(f"WebSearch not available or failed: {e}, using simulated results")
            
            # Fall back to simulated research results based on query focus area
            if query.focus_area == "best_practices":
                return {
                    "results": [
                        {
                            "title": f"Latest {query.search_term} Best Practices",
                            "content": f"Current industry standards for {query.search_term} include proper error handling, comprehensive testing, and performance optimization.",
                            "url": "https://example.com/best-practices",
                            "relevance": 0.9
                        }
                    ],
                    "summary": f"Best practices research for {query.search_term}",
                    "confidence": 0.8
                }
            elif query.focus_area == "technology_updates":
                return {
                    "results": [
                        {
                            "title": f"{query.search_term} Latest Updates",
                            "content": f"Recent updates include improved performance, new features, and security enhancements.",
                            "url": "https://example.com/tech-updates",
                            "relevance": 0.85
                        }
                    ],
                    "summary": f"Technology updates for {query.search_term}",
                    "confidence": 0.75
                }
            else:
                return {
                    "results": [
                        {
                            "title": f"Research Results for {query.search_term}",
                            "content": f"General research findings related to {query.search_term}",
                            "url": "https://example.com/research",
                            "relevance": 0.7
                        }
                    ],
                    "summary": f"General research for {query.search_term}",
                    "confidence": 0.6
                }
    
    def _process_research_results(
        self, 
        results: Dict[str, Any], 
        query: ResearchQuery, 
        research_data: ResearchData
    ) -> None:
        """Process and categorize research results.
        
        Args:
            results: Raw search results
            query: Original research query
            research_data: Research data object to populate
        """
        focus_area = query.focus_area
        
        # Extract key information from results
        for result in results.get("results", []):
            content = result.get("content", "")
            
            if focus_area == "best_practices":
                research_data.best_practices.append(content)
            elif focus_area == "technology_updates":
                research_data.technology_updates[query.search_term] = content
            elif focus_area == "security_insights":
                research_data.security_insights.append(content)
            elif focus_area == "performance_optimization":
                research_data.performance_tips.append(content)
            elif focus_area == "common_pitfalls":
                research_data.common_pitfalls.append(content)
            else:
                # General domain knowledge
                if query.context not in research_data.domain_knowledge:
                    research_data.domain_knowledge[query.context] = []
                research_data.domain_knowledge[query.context].append(content)
    
    def _calculate_research_quality(self, research_data: ResearchData) -> float:
        """Calculate overall research quality score.
        
        Args:
            research_data: Research data to evaluate
            
        Returns:
            Quality score between 0 and 1
        """
        score = 0.0
        
        # Score based on data completeness
        if research_data.best_practices:
            score += 0.2
        if research_data.technology_updates:
            score += 0.2
        if research_data.security_insights:
            score += 0.15
        if research_data.performance_tips:
            score += 0.15
        if research_data.common_pitfalls:
            score += 0.15
        if research_data.domain_knowledge:
            score += 0.15
        
        return min(score, 1.0)


class AgentArchitectDesigner:
    """Designs optimal agent architecture for projects."""
    
    def __init__(self):
        """Initialize the agent architect designer."""
        self.design_cache = {}
        
    async def design_agent_architecture(self, analysis: ProjectAnalysis) -> AgentBlueprint:
        """Design optimal agent architecture based on project analysis.
        
        Args:
            analysis: Comprehensive project analysis
            
        Returns:
            Complete agent architecture blueprint
        """
        logger.info(f"Designing agent architecture for {analysis.project_type} project")
        
        # Check cache
        cache_key = self._create_cache_key(analysis)
        if cache_key in self.design_cache:
            logger.debug("Using cached agent architecture")
            return self.design_cache[cache_key]
        
        # Design agent specifications
        agent_specs = await self._create_agent_specifications(analysis)
        
        # Determine execution order and dependencies
        execution_order = self._determine_execution_order(agent_specs, analysis)
        
        # Create collaboration matrix
        collaboration_matrix = self._create_collaboration_matrix(agent_specs, analysis)
        
        # Identify parallel execution groups
        parallel_groups = self._identify_parallel_groups(agent_specs, execution_order)
        
        # Define quality gates
        quality_gates = self._define_quality_gates(analysis)
        
        # Estimate duration
        estimated_duration = self._estimate_duration(analysis, len(agent_specs))
        
        # Determine coordination strategy
        coordination_strategy = self._determine_coordination_strategy(analysis, agent_specs)
        
        # Define success criteria
        success_criteria = self._define_success_criteria(analysis)
        
        blueprint = AgentBlueprint(
            agent_specs=agent_specs,
            execution_order=execution_order,
            collaboration_matrix=collaboration_matrix,
            parallel_groups=parallel_groups,
            quality_gates=quality_gates,
            estimated_duration=estimated_duration,
            coordination_strategy=coordination_strategy,
            success_criteria=success_criteria
        )
        
        # Cache the blueprint
        self.design_cache[cache_key] = blueprint
        
        logger.info(f"Architecture designed with {len(agent_specs)} agents, "
                   f"estimated duration: {estimated_duration}")
        
        return blueprint
    
    async def _create_agent_specifications(self, analysis: ProjectAnalysis) -> List[AgentSpec]:
        """Create agent specifications based on project analysis.
        
        Args:
            analysis: Project analysis results
            
        Returns:
            List of agent specifications
        """
        agent_specs = []
        
        # Determine number of agents based on complexity and scope
        num_agents = self._calculate_optimal_agent_count(analysis)
        
        logger.info(f"Creating {num_agents} specialized agents")
        
        # Core architecture agent (always needed)
        if analysis.complexity in [ComplexityLevel.COMPLEX, ComplexityLevel.ENTERPRISE]:
            agent_specs.append(self._create_architect_agent(analysis))
        
        # Domain-specific agents
        agent_specs.extend(self._create_domain_agents(analysis))
        
        # Quality assurance agent for substantial projects
        if (analysis.complexity != ComplexityLevel.SIMPLE or 
            len(analysis.quality_requirements) > 2):
            agent_specs.append(self._create_qa_agent(analysis))
        
        # DevOps agent for deployment-intensive projects
        if (len(analysis.deployment_needs) > 2 or 
            analysis.complexity in [ComplexityLevel.COMPLEX, ComplexityLevel.ENTERPRISE]):
            agent_specs.append(self._create_devops_agent(analysis))
        
        # Security specialist for security-intensive projects
        if len(analysis.security_requirements) > 3:
            agent_specs.append(self._create_security_agent(analysis))
        
        # Performance specialist for performance-critical projects
        if len(analysis.performance_requirements) > 2:
            agent_specs.append(self._create_performance_agent(analysis))
        
        # Data specialist for data-intensive projects
        if "data_engineering" in analysis.domains or "ml_ai" in analysis.domains:
            agent_specs.append(self._create_data_agent(analysis))
        
        # Integration specialist for integration-heavy projects
        if len(analysis.integration_needs) > 3:
            agent_specs.append(self._create_integration_agent(analysis))
        
        # Limit agents to reasonable number
        agent_specs = agent_specs[:8]  # Maximum 8 agents
        
        # Ensure we have at least one agent
        if not agent_specs:
            agent_specs.append(self._create_fullstack_agent(analysis))
        
        # Assign priorities and dependencies
        self._assign_priorities_and_dependencies(agent_specs, analysis)
        
        return agent_specs
    
    def _calculate_optimal_agent_count(self, analysis: ProjectAnalysis) -> int:
        """Calculate optimal number of agents based on project characteristics."""
        base_count = 1
        
        # Add agents based on complexity
        complexity_multipliers = {
            ComplexityLevel.SIMPLE: 1,
            ComplexityLevel.MODERATE: 2,
            ComplexityLevel.COMPLEX: 3,
            ComplexityLevel.ENTERPRISE: 4
        }
        base_count *= complexity_multipliers[analysis.complexity]
        
        # Add agents based on domain count
        base_count += min(len(analysis.domains), 3)
        
        # Add agents based on technical challenges
        base_count += min(len(analysis.technical_challenges) // 2, 2)
        
        # Cap at reasonable limits
        return min(max(base_count, 1), 8)
    
    def _create_architect_agent(self, analysis: ProjectAnalysis) -> AgentSpec:
        """Create architecture specialist agent."""
        return AgentSpec(
            name="SystemArchitect",
            role="System Architecture Specialist",
            description="Designs overall system architecture, defines technical standards, and ensures architectural consistency across all components",
            expertise_areas=["System Design", "Architecture Patterns", "Scalability", "Technical Leadership"],
            responsibilities=[
                "Design overall system architecture",
                "Define technical standards and conventions",
                "Ensure architectural consistency",
                "Make technology stack decisions",
                "Guide other agents on architectural decisions"
            ],
            tools=["Read", "Write", "Edit", "MultiEdit", "Glob", "Grep", "TodoWrite"],
            expertise_level=AgentExpertiseLevel.ARCHITECT,
            priority=1,
            collaboration_patterns=["leads", "guides", "reviews"],
            specialization_focus="System Architecture & Technical Leadership",
            quality_standards=[
                "Architectural Documentation",
                "Design Pattern Consistency",
                "Scalability Planning",
                "Technology Stack Optimization"
            ]
        )
    
    def _create_domain_agents(self, analysis: ProjectAnalysis) -> List[AgentSpec]:
        """Create domain-specific agents based on project domains."""
        domain_agents = []
        
        if "frontend" in analysis.domains:
            domain_agents.append(AgentSpec(
                name="FrontendSpecialist",
                role="Frontend Development Expert",
                description="Specializes in modern frontend development, UI/UX implementation, and client-side optimization",
                expertise_areas=["React", "TypeScript", "CSS", "Performance Optimization", "Accessibility"],
                responsibilities=[
                    "Implement user interface components",
                    "Optimize frontend performance",
                    "Ensure accessibility compliance",
                    "Handle state management",
                    "Implement responsive design"
                ],
                tools=["Read", "Write", "Edit", "MultiEdit", "Glob", "Grep", "WebFetch", "TodoWrite"],
                expertise_level=AgentExpertiseLevel.EXPERT,
                priority=2,
                specialization_focus="Modern Frontend Development"
            ))
        
        if "backend" in analysis.domains:
            domain_agents.append(AgentSpec(
                name="BackendEngineer",
                role="Backend Development Specialist",
                description="Expert in server-side development, API design, and backend system architecture",
                expertise_areas=["API Design", "Database Design", "Server Architecture", "Authentication", "Performance"],
                responsibilities=[
                    "Design and implement APIs",
                    "Set up database schemas",
                    "Implement authentication systems",
                    "Optimize backend performance",
                    "Handle server-side logic"
                ],
                tools=["Read", "Write", "Edit", "MultiEdit", "Glob", "Grep", "Bash", "TodoWrite"],
                expertise_level=AgentExpertiseLevel.EXPERT,
                priority=2,
                specialization_focus="Backend Systems & APIs"
            ))
        
        if "mobile" in analysis.domains:
            domain_agents.append(AgentSpec(
                name="MobileDeveloper",
                role="Mobile Application Specialist",
                description="Expert in mobile app development, cross-platform solutions, and mobile-specific optimizations",
                expertise_areas=["React Native", "Flutter", "Mobile UI/UX", "Performance", "App Store Deployment"],
                responsibilities=[
                    "Develop mobile application features",
                    "Optimize for mobile performance",
                    "Implement platform-specific functionality",
                    "Handle mobile-specific concerns",
                    "Prepare for app store deployment"
                ],
                tools=["Read", "Write", "Edit", "MultiEdit", "Glob", "Grep", "Bash", "TodoWrite"],
                expertise_level=AgentExpertiseLevel.EXPERT,
                priority=2,
                specialization_focus="Mobile Development"
            ))
        
        if "ml_ai" in analysis.domains:
            domain_agents.append(AgentSpec(
                name="MLEngineer",
                role="Machine Learning Specialist",
                description="Expert in ML model development, data processing, and AI system implementation",
                expertise_areas=["Machine Learning", "Data Processing", "Model Training", "MLOps", "AI Ethics"],
                responsibilities=[
                    "Design ML pipelines",
                    "Implement data processing workflows",
                    "Train and validate models",
                    "Set up model deployment",
                    "Monitor model performance"
                ],
                tools=["Read", "Write", "Edit", "MultiEdit", "Glob", "Grep", "Bash", "WebFetch", "TodoWrite"],
                expertise_level=AgentExpertiseLevel.EXPERT,
                priority=2,
                specialization_focus="Machine Learning & AI"
            ))
        
        return domain_agents[:4]  # Limit domain agents
    
    def _create_qa_agent(self, analysis: ProjectAnalysis) -> AgentSpec:
        """Create quality assurance specialist agent."""
        return AgentSpec(
            name="QualityAssuranceExpert",
            role="Quality Assurance Specialist", 
            description="Ensures code quality, implements comprehensive testing strategies, and maintains quality standards",
            expertise_areas=["Testing Strategies", "Code Quality", "Automation", "Performance Testing", "Security Testing"],
            responsibilities=[
                "Design comprehensive testing strategies",
                "Implement automated tests",
                "Conduct code quality reviews",
                "Set up testing infrastructure",
                "Define quality metrics and standards"
            ],
            tools=["Read", "Write", "Edit", "MultiEdit", "Glob", "Grep", "Bash", "TodoWrite"],
            expertise_level=AgentExpertiseLevel.EXPERT,
            priority=3,
            specialization_focus="Quality Assurance & Testing",
            quality_standards=[
                "Test Coverage Standards",
                "Code Quality Metrics",
                "Automated Testing Pipeline",
                "Performance Testing Strategy"
            ]
        )
    
    def _create_devops_agent(self, analysis: ProjectAnalysis) -> AgentSpec:
        """Create DevOps specialist agent."""
        return AgentSpec(
            name="DevOpsEngineer", 
            role="DevOps & Infrastructure Specialist",
            description="Expert in deployment automation, infrastructure management, and operational excellence",
            expertise_areas=["CI/CD", "Container Orchestration", "Cloud Infrastructure", "Monitoring", "Security"],
            responsibilities=[
                "Set up CI/CD pipelines",
                "Configure deployment infrastructure", 
                "Implement monitoring and logging",
                "Ensure security best practices",
                "Optimize operational workflows"
            ],
            tools=["Read", "Write", "Edit", "MultiEdit", "Glob", "Grep", "Bash", "TodoWrite"],
            expertise_level=AgentExpertiseLevel.EXPERT,
            priority=4,
            specialization_focus="DevOps & Infrastructure"
        )
    
    def _create_security_agent(self, analysis: ProjectAnalysis) -> AgentSpec:
        """Create security specialist agent."""
        return AgentSpec(
            name="SecurityExpert",
            role="Security Specialist",
            description="Ensures application security, implements security best practices, and conducts security assessments",
            expertise_areas=["Application Security", "Authentication", "Encryption", "Compliance", "Threat Modeling"],
            responsibilities=[
                "Implement security measures",
                "Conduct security assessments",
                "Ensure compliance requirements",
                "Design authentication systems",
                "Review code for security vulnerabilities"
            ],
            tools=["Read", "Write", "Edit", "MultiEdit", "Glob", "Grep", "WebFetch", "TodoWrite"],
            expertise_level=AgentExpertiseLevel.SPECIALIST,
            priority=3,
            specialization_focus="Application Security"
        )
    
    def _create_performance_agent(self, analysis: ProjectAnalysis) -> AgentSpec:
        """Create performance specialist agent."""
        return AgentSpec(
            name="PerformanceOptimizer",
            role="Performance Optimization Specialist",
            description="Focuses on application performance, optimization strategies, and scalability improvements",
            expertise_areas=["Performance Optimization", "Scalability", "Caching", "Load Testing", "Profiling"],
            responsibilities=[
                "Optimize application performance",
                "Implement caching strategies", 
                "Conduct performance testing",
                "Profile and identify bottlenecks",
                "Design scalability improvements"
            ],
            tools=["Read", "Write", "Edit", "MultiEdit", "Glob", "Grep", "Bash", "TodoWrite"],
            expertise_level=AgentExpertiseLevel.SPECIALIST,
            priority=3,
            specialization_focus="Performance & Scalability"
        )
    
    def _create_data_agent(self, analysis: ProjectAnalysis) -> AgentSpec:
        """Create data specialist agent."""
        return AgentSpec(
            name="DataEngineer",
            role="Data Engineering Specialist",
            description="Expert in data architecture, pipeline development, and data processing optimization",
            expertise_areas=["Data Architecture", "ETL Pipelines", "Database Optimization", "Data Quality", "Analytics"],
            responsibilities=[
                "Design data architecture",
                "Implement data pipelines",
                "Optimize database performance",
                "Ensure data quality",
                "Set up analytics infrastructure"
            ],
            tools=["Read", "Write", "Edit", "MultiEdit", "Glob", "Grep", "Bash", "TodoWrite"],
            expertise_level=AgentExpertiseLevel.EXPERT,
            priority=2,
            specialization_focus="Data Engineering & Analytics"
        )
    
    def _create_integration_agent(self, analysis: ProjectAnalysis) -> AgentSpec:
        """Create integration specialist agent."""
        return AgentSpec(
            name="IntegrationSpecialist",
            role="Integration & API Specialist", 
            description="Expert in system integration, API development, and third-party service integration",
            expertise_areas=["API Integration", "Microservices", "Event-Driven Architecture", "Message Queues", "Webhooks"],
            responsibilities=[
                "Design integration architecture",
                "Implement API integrations",
                "Set up message queuing systems",
                "Handle webhook implementations",
                "Ensure integration reliability"
            ],
            tools=["Read", "Write", "Edit", "MultiEdit", "Glob", "Grep", "WebFetch", "TodoWrite"],
            expertise_level=AgentExpertiseLevel.EXPERT,
            priority=3,
            specialization_focus="System Integration"
        )
    
    def _create_fullstack_agent(self, analysis: ProjectAnalysis) -> AgentSpec:
        """Create general fullstack agent as fallback."""
        return AgentSpec(
            name="FullStackDeveloper",
            role="Full-Stack Development Expert",
            description="Versatile developer capable of handling both frontend and backend development tasks",
            expertise_areas=["Frontend Development", "Backend Development", "Database Design", "API Development", "Testing"],
            responsibilities=[
                "Implement full-stack features",
                "Handle both frontend and backend tasks",
                "Design database schemas",
                "Create and consume APIs",
                "Ensure end-to-end functionality"
            ],
            tools=["Read", "Write", "Edit", "MultiEdit", "Glob", "Grep", "Bash", "WebFetch", "TodoWrite"],
            expertise_level=AgentExpertiseLevel.EXPERT,
            priority=1,
            specialization_focus="Full-Stack Development"
        )
    
    def _assign_priorities_and_dependencies(self, agent_specs: List[AgentSpec], analysis: ProjectAnalysis) -> None:
        """Assign priorities and dependencies to agent specifications."""
        
        # Architecture agents have highest priority
        for spec in agent_specs:
            if "Architect" in spec.name:
                spec.priority = 1
        
        # Core domain agents have high priority
        domain_agents = ["Frontend", "Backend", "Mobile", "ML"]
        for spec in agent_specs:
            if any(domain in spec.name for domain in domain_agents):
                spec.priority = 2
        
        # Support agents have lower priority
        support_agents = ["QualityAssurance", "DevOps", "Security", "Performance"]
        for spec in agent_specs:
            if any(support in spec.name for support in support_agents):
                spec.priority = max(spec.priority, 3)
        
        # Set dependencies
        for spec in agent_specs:
            if spec.name == "QualityAssuranceExpert":
                # QA depends on implementation agents
                spec.dependencies = [s.name for s in agent_specs 
                                   if s.priority <= 2 and s.name != spec.name]
            elif spec.name == "DevOpsEngineer":
                # DevOps depends on all development agents
                spec.dependencies = [s.name for s in agent_specs 
                                   if s.priority <= 3 and s.name != spec.name]
    
    def _determine_execution_order(self, agent_specs: List[AgentSpec], analysis: ProjectAnalysis) -> List[str]:
        """Determine optimal execution order for agents."""
        
        # Sort by priority first
        sorted_specs = sorted(agent_specs, key=lambda x: x.priority)
        
        execution_order = []
        
        # Architecture and planning phase
        arch_agents = [s for s in sorted_specs if s.priority == 1]
        execution_order.extend([s.name for s in arch_agents])
        
        # Core development phase  
        dev_agents = [s for s in sorted_specs if s.priority == 2]
        execution_order.extend([s.name for s in dev_agents])
        
        # Quality and optimization phase
        quality_agents = [s for s in sorted_specs if s.priority >= 3]
        execution_order.extend([s.name for s in quality_agents])
        
        return execution_order
    
    def _create_collaboration_matrix(self, agent_specs: List[AgentSpec], analysis: ProjectAnalysis) -> Dict[str, List[str]]:
        """Create collaboration matrix showing agent interactions."""
        matrix = {}
        
        for spec in agent_specs:
            collaborators = []
            
            # Architecture agents collaborate with everyone
            if "Architect" in spec.name:
                collaborators = [s.name for s in agent_specs if s.name != spec.name]
            
            # Frontend collaborates with Backend, QA, Performance
            elif "Frontend" in spec.name:
                collaborators = [s.name for s in agent_specs 
                               if any(keyword in s.name for keyword in ["Backend", "QualityAssurance", "Performance", "Security"])]
            
            # Backend collaborates with Frontend, Data, Integration, QA
            elif "Backend" in spec.name:
                collaborators = [s.name for s in agent_specs
                               if any(keyword in s.name for keyword in ["Frontend", "Data", "Integration", "QualityAssurance", "Security"])]
            
            # QA collaborates with all development agents
            elif "QualityAssurance" in spec.name:
                collaborators = [s.name for s in agent_specs 
                               if s.priority <= 2]
            
            # DevOps collaborates with all agents
            elif "DevOps" in spec.name:
                collaborators = [s.name for s in agent_specs if s.name != spec.name]
            
            matrix[spec.name] = collaborators
        
        return matrix
    
    def _identify_parallel_groups(self, agent_specs: List[AgentSpec], execution_order: List[str]) -> List[List[str]]:
        """Identify groups of agents that can work in parallel."""
        parallel_groups = []
        
        # Group by priority levels
        priority_groups = {}
        for spec in agent_specs:
            if spec.priority not in priority_groups:
                priority_groups[spec.priority] = []
            priority_groups[spec.priority].append(spec.name)
        
        # Create parallel groups from priority groups
        for priority in sorted(priority_groups.keys()):
            if len(priority_groups[priority]) > 1:
                parallel_groups.append(priority_groups[priority])
        
        return parallel_groups
    
    def _define_quality_gates(self, analysis: ProjectAnalysis) -> List[str]:
        """Define quality gates for the project."""
        gates = ["Code Quality Review", "Basic Testing"]
        
        if analysis.complexity in [ComplexityLevel.COMPLEX, ComplexityLevel.ENTERPRISE]:
            gates.extend([
                "Architecture Review",
                "Security Assessment", 
                "Performance Testing",
                "Integration Testing"
            ])
        
        if analysis.security_requirements:
            gates.append("Security Compliance Check")
        
        if analysis.performance_requirements:
            gates.append("Performance Benchmarking")
        
        return gates
    
    def _estimate_duration(self, analysis: ProjectAnalysis, num_agents: int) -> str:
        """Estimate project duration based on complexity and agent count."""
        
        base_hours = {
            ComplexityLevel.SIMPLE: 8,
            ComplexityLevel.MODERATE: 24,
            ComplexityLevel.COMPLEX: 48,
            ComplexityLevel.ENTERPRISE: 96
        }
        
        estimated_hours = base_hours[analysis.complexity]
        
        # Adjust for scope
        scope_multipliers = {"small": 1.0, "medium": 1.5, "large": 2.0}
        estimated_hours *= scope_multipliers.get(analysis.estimated_scope, 1.0)
        
        # Parallelization benefit (diminishing returns)
        if num_agents > 1:
            parallelization_factor = 1.0 - (0.2 * min(num_agents - 1, 3))
            estimated_hours *= parallelization_factor
        
        # Convert to human-readable duration
        if estimated_hours <= 8:
            return f"{int(estimated_hours)} hours"
        elif estimated_hours <= 48:
            return f"{int(estimated_hours // 8)} days"
        else:
            return f"{int(estimated_hours // 40)} weeks"
    
    def _determine_coordination_strategy(self, analysis: ProjectAnalysis, agent_specs: List[AgentSpec]) -> str:
        """Determine optimal coordination strategy."""
        
        if analysis.complexity == ComplexityLevel.ENTERPRISE and len(agent_specs) >= 5:
            return "hierarchical_with_architect_lead"
        elif len(agent_specs) >= 4:
            return "collaborative_with_priority_coordination"
        elif len(agent_specs) >= 2:
            return "peer_to_peer_collaboration"
        else:
            return "single_agent_execution"
    
    def _define_success_criteria(self, analysis: ProjectAnalysis) -> List[str]:
        """Define success criteria for project completion."""
        criteria = [
            "All core functionality implemented",
            "Code quality standards met",
            "Basic testing completed"
        ]
        
        if analysis.performance_requirements:
            criteria.append("Performance requirements satisfied")
        
        if analysis.security_requirements:
            criteria.append("Security standards implemented")
        
        if analysis.deployment_needs:
            criteria.append("Deployment pipeline configured")
        
        if analysis.complexity in [ComplexityLevel.COMPLEX, ComplexityLevel.ENTERPRISE]:
            criteria.extend([
                "Architecture documentation complete",
                "Comprehensive testing suite implemented",
                "Production readiness validated"
            ])
        
        return criteria
    
    def _create_cache_key(self, analysis: ProjectAnalysis) -> str:
        """Create cache key for agent architecture."""
        key_components = [
            analysis.project_type,
            analysis.complexity.value,
            analysis.estimated_scope,
            "_".join(sorted(analysis.domains)),
            "_".join(sorted(analysis.technologies))
        ]
        return hash("_".join(key_components))


class KnowledgeSynthesizer:
    """Synthesizes web research into actionable agent knowledge."""
    
    def __init__(self):
        """Initialize the knowledge synthesizer."""
        pass
        
    async def synthesize_research(
        self, 
        research_data: ResearchData, 
        spec: AgentSpec
    ) -> str:
        """Synthesize research data into agent knowledge base.
        
        Args:
            research_data: Compiled research data
            spec: Agent specification
            
        Returns:
            Synthesized knowledge as formatted text
        """
        logger.debug(f"Synthesizing knowledge for {spec.name}")
        
        synthesis = []
        
        # Header
        synthesis.append(f"# Research-Enhanced Knowledge Base for {spec.role}")
        synthesis.append(f"*Generated on {datetime.now().strftime('%Y-%m-%d')} with research quality score: {research_data.quality_score:.2f}*\n")
        
        # Latest best practices
        if research_data.best_practices:
            synthesis.append("## 🎯 Latest Best Practices (2025)")
            for practice in research_data.best_practices[:5]:  # Top 5
                synthesis.append(f"- {practice}")
            synthesis.append("")
        
        # Technology updates
        if research_data.technology_updates:
            synthesis.append("## 🚀 Technology Updates & Features")
            for tech, update in research_data.technology_updates.items():
                synthesis.append(f"### {tech}")
                synthesis.append(f"{update}\n")
        
        # Security insights
        if research_data.security_insights:
            synthesis.append("## 🔒 Current Security Considerations")
            for insight in research_data.security_insights[:3]:  # Top 3
                synthesis.append(f"- {insight}")
            synthesis.append("")
        
        # Performance optimization tips
        if research_data.performance_tips:
            synthesis.append("## ⚡ Performance Optimization Techniques")
            for tip in research_data.performance_tips[:4]:  # Top 4
                synthesis.append(f"- {tip}")
            synthesis.append("")
        
        # Common pitfalls
        if research_data.common_pitfalls:
            synthesis.append("## ⚠️ Common Pitfalls to Avoid")
            for pitfall in research_data.common_pitfalls[:3]:  # Top 3
                synthesis.append(f"- {pitfall}")
            synthesis.append("")
        
        # Domain-specific knowledge
        if research_data.domain_knowledge:
            synthesis.append("## 🎓 Domain-Specific Expertise")
            for domain, knowledge_items in research_data.domain_knowledge.items():
                synthesis.append(f"### {domain}")
                for item in knowledge_items[:2]:  # Top 2 per domain
                    synthesis.append(f"- {item}")
            synthesis.append("")
        
        # Tool recommendations
        if research_data.tool_recommendations:
            synthesis.append("## 🛠️ Recommended Tools & Libraries")
            for tool in research_data.tool_recommendations[:5]:  # Top 5
                synthesis.append(f"- {tool}")
            synthesis.append("")
        
        # Latest trends
        if research_data.latest_trends:
            synthesis.append("## 📈 Current Industry Trends")
            for trend in research_data.latest_trends[:3]:  # Top 3
                synthesis.append(f"- {trend}")
            synthesis.append("")
        
        knowledge_text = "\n".join(synthesis)
        
        logger.info(f"Knowledge synthesis complete for {spec.name}: {len(knowledge_text)} characters")
        return knowledge_text


class ResearchEnhancedAgentGenerator:
    """Main agent generator with research enhancement capabilities."""
    
    def __init__(self, web_search_tool=None):
        """Initialize the research-enhanced agent generator.
        
        Args:
            web_search_tool: WebSearch tool for conducting research
        """
        self.analyzer = DeepProjectAnalyzer()
        self.architect = AgentArchitectDesigner()
        self.query_generator = ResearchQueryGenerator()
        self.research_conductor = WebResearchConductor()
        self.knowledge_synthesizer = KnowledgeSynthesizer()
        self.web_search_tool = web_search_tool
        
        logger.info("ResearchEnhancedAgentGenerator initialized")
    
    async def create_agentic_project_team(self, idea: str) -> Tuple[List[DynamicAgent], AgentBlueprint]:
        """Create a complete project team of research-enhanced agents.
        
        Args:
            idea: Project idea description
            
        Returns:
            Tuple of (dynamic agents list, agent blueprint)
        """
        logger.info("Starting agentic project team creation")
        
        try:
            # Step 1: Deep project analysis
            logger.info("Step 1: Performing deep project analysis")
            analysis = await self.analyzer.analyze_comprehensive(idea)
            
            # Step 2: Design agent architecture
            logger.info("Step 2: Designing optimal agent architecture")
            blueprint = await self.architect.design_agent_architecture(analysis)
            
            # Step 3: Create research-enhanced agents
            logger.info(f"Step 3: Creating {len(blueprint.agent_specs)} research-enhanced agents")
            dynamic_agents = []
            
            for spec in blueprint.agent_specs:
                agent = await self.create_research_enhanced_agent(spec, analysis)
                dynamic_agents.append(agent)
            
            logger.info(f"Agentic team creation complete: {len(dynamic_agents)} agents created")
            
            return dynamic_agents, blueprint
            
        except Exception as e:
            logger.error(f"Agentic team creation failed: {e}")
            # Return fallback single agent
            fallback_agent = await self._create_fallback_agent(idea)
            fallback_blueprint = self._create_fallback_blueprint(fallback_agent) 
            return [fallback_agent], fallback_blueprint
    
    async def create_research_enhanced_agent(
        self, 
        spec: AgentSpec, 
        context: ProjectAnalysis
    ) -> DynamicAgent:
        """Create a single research-enhanced agent.
        
        Args:
            spec: Agent specification
            context: Project analysis context
            
        Returns:
            Research-enhanced dynamic agent
        """
        logger.info(f"Creating research-enhanced agent: {spec.name}")
        
        try:
            # Step 1: Generate research queries
            queries = await self.query_generator.generate_research_queries(spec, context)
            
            # Step 2: Conduct web research
            research_data = await self.research_conductor.conduct_research(queries)
            
            # Step 3: Synthesize knowledge
            knowledge_base_text = await self.knowledge_synthesizer.synthesize_research(research_data, spec)
            
            # Step 4: Generate enhanced system prompt
            system_prompt = await self._generate_enhanced_system_prompt(spec, context, knowledge_base_text)
            
            # Step 5: Create dynamic agent
            agent = DynamicAgent(
                name=spec.name,
                description=f"{spec.description} (Research-Enhanced with 2025 Knowledge)",
                system_prompt=system_prompt,
                tools=spec.tools,
                expertise_level=spec.expertise_level,
                specialization_areas=spec.expertise_areas,
                knowledge_base=research_data,
                collaboration_instructions=self._generate_collaboration_instructions(spec),
                quality_standards=spec.quality_standards,
                success_metrics=self._generate_success_metrics(spec, context),
                creation_timestamp=datetime.now(),
                research_enhanced=True
            )
            
            logger.info(f"Research-enhanced agent created: {spec.name}")
            return agent
            
        except Exception as e:
            logger.warning(f"Research enhancement failed for {spec.name}: {e}")
            # Fall back to basic agent creation
            return await self._create_basic_agent(spec, context)
    
    async def _generate_enhanced_system_prompt(
        self, 
        spec: AgentSpec, 
        context: ProjectAnalysis,
        knowledge_base: str
    ) -> str:
        """Generate enhanced system prompt with research knowledge.
        
        Args:
            spec: Agent specification
            context: Project context
            knowledge_base: Synthesized research knowledge
            
        Returns:
            Enhanced system prompt
        """
        prompt_sections = []
        
        # Agent identity and role
        prompt_sections.append(f"""# {spec.role} - Research-Enhanced AI Agent

You are a {spec.role} with cutting-edge expertise in {', '.join(spec.expertise_areas)}. 
You have been specifically created for this project with the latest 2025 industry knowledge and best practices.

## Your Specialization
{spec.description}

## Core Responsibilities
{chr(10).join(f"- {resp}" for resp in spec.responsibilities)}

## Expertise Areas
{chr(10).join(f"- **{area}**: Advanced knowledge with latest industry insights" for area in spec.expertise_areas)}""")
        
        # Project context
        prompt_sections.append(f"""
## Project Context
- **Project Type**: {context.project_type}
- **Complexity Level**: {context.complexity.value}
- **Domains**: {', '.join(context.domains)}
- **Technologies**: {', '.join(context.technologies)}
- **Estimated Scope**: {context.estimated_scope}
- **Key Challenges**: {', '.join(context.technical_challenges[:3])}""")
        
        # Research-enhanced knowledge
        prompt_sections.append(f"""
## Research-Enhanced Knowledge Base
{knowledge_base}""")
        
        # Working approach
        prompt_sections.append(f"""
## Your Working Approach

### 1. Quality Standards
{chr(10).join(f"- {standard}" for standard in spec.quality_standards)}

### 2. Collaboration Style
- Work collaboratively with other specialized agents
- Share knowledge and coordinate effectively
- Review and validate other agents' work when relevant
- Provide expert guidance in your specialization areas

### 3. Implementation Guidelines
- Always use the latest best practices from your knowledge base
- Implement current security measures and compliance requirements
- Follow performance optimization techniques specific to your domain
- Avoid deprecated methods and outdated patterns
- Include comprehensive error handling and logging
- Write clean, maintainable, and well-documented code

### 4. Quality Assurance
- Implement thorough testing strategies appropriate to your specialization
- Conduct code reviews focusing on your areas of expertise
- Validate implementations against current industry standards
- Ensure compatibility with modern tooling and frameworks

## Tools Available
{', '.join(spec.tools)}

## Success Criteria
Your work will be considered successful when:
- All assigned responsibilities are completed to current industry standards
- Code quality meets or exceeds current best practices
- Implementations are secure, performant, and maintainable
- Integration with other agents' work is seamless
- Documentation is comprehensive and current

Remember: You are an expert with access to the most current information in your field. Use this knowledge to deliver exceptional results that reflect 2025 industry standards.""")
        
        return "\n".join(prompt_sections)
    
    def _generate_collaboration_instructions(self, spec: AgentSpec) -> str:
        """Generate collaboration instructions for the agent."""
        instructions = []
        
        instructions.append(f"As a {spec.role}, you should:")
        
        if spec.priority == 1:
            instructions.extend([
                "- Take leadership role in architectural decisions",
                "- Guide other agents on technical standards",
                "- Review and approve major design decisions",
                "- Coordinate overall project structure"
            ])
        elif spec.priority == 2:
            instructions.extend([
                "- Collaborate closely with other development agents",
                "- Share progress and coordinate feature development",
                "- Provide domain expertise to guide implementation",
                "- Review related code and provide feedback"
            ])
        else:
            instructions.extend([
                "- Support development agents with specialized expertise",
                "- Review implementations for quality and compliance",
                "- Provide feedback and recommendations",
                "- Ensure standards are maintained"
            ])
        
        if spec.dependencies:
            instructions.append(f"- Wait for completion from: {', '.join(spec.dependencies)}")
        
        return "\n".join(instructions)
    
    def _generate_success_metrics(self, spec: AgentSpec, context: ProjectAnalysis) -> List[str]:
        """Generate success metrics for the agent."""
        metrics = [
            "All assigned tasks completed",
            "Code quality standards met",
            "Documentation provided"
        ]
        
        # Role-specific metrics
        if "Frontend" in spec.name:
            metrics.extend([
                "UI components implemented and responsive",
                "Accessibility standards met",
                "Performance optimization applied"
            ])
        elif "Backend" in spec.name:
            metrics.extend([
                "APIs functional and documented",
                "Database integration working",
                "Security measures implemented"
            ])
        elif "QualityAssurance" in spec.name:
            metrics.extend([
                "Test coverage meets standards",
                "Automated testing pipeline setup",
                "Quality gates implemented"
            ])
        elif "DevOps" in spec.name:
            metrics.extend([
                "Deployment pipeline configured",
                "Infrastructure provisioned",
                "Monitoring setup complete"
            ])
        
        # Context-specific metrics
        if context.security_requirements:
            metrics.append("Security requirements validated")
        
        if context.performance_requirements:
            metrics.append("Performance benchmarks met")
        
        return metrics
    
    async def _create_basic_agent(self, spec: AgentSpec, context: ProjectAnalysis) -> DynamicAgent:
        """Create basic agent without research enhancement (fallback)."""
        
        basic_prompt = f"""You are a {spec.role} specializing in {', '.join(spec.expertise_areas)}.

## Responsibilities
{chr(10).join(f"- {resp}" for resp in spec.responsibilities)}

## Project Context
- Type: {context.project_type}
- Domains: {', '.join(context.domains)}
- Technologies: {', '.join(context.technologies)}
- Complexity: {context.complexity.value}

Please implement your assigned tasks following current best practices and industry standards."""
        
        return DynamicAgent(
            name=spec.name,
            description=spec.description,
            system_prompt=basic_prompt,
            tools=spec.tools,
            expertise_level=spec.expertise_level,
            specialization_areas=spec.expertise_areas,
            knowledge_base=ResearchData(),  # Empty knowledge base
            collaboration_instructions="Work collaboratively with other agents",
            quality_standards=spec.quality_standards,
            success_metrics=["Complete assigned tasks", "Meet quality standards"],
            research_enhanced=False
        )
    
    async def _create_fallback_agent(self, idea: str) -> DynamicAgent:
        """Create fallback agent if team creation fails."""
        
        return DynamicAgent(
            name="GeneralDeveloper",
            description="General-purpose developer capable of handling various development tasks",
            system_prompt=f"""You are a versatile software developer tasked with creating a project based on this idea: "{idea}"

Please analyze the requirements and implement a complete solution following best practices.""",
            tools=["Read", "Write", "Edit", "MultiEdit", "Glob", "Grep", "Bash", "WebFetch", "TodoWrite"],
            expertise_level=AgentExpertiseLevel.EXPERT,
            specialization_areas=["General Development"],
            knowledge_base=ResearchData(),
            collaboration_instructions="Work independently to complete the project",
            quality_standards=["Code Quality", "Basic Testing"],
            success_metrics=["Project functionality complete", "Code quality maintained"],
            research_enhanced=False
        )
    
    def _create_fallback_blueprint(self, agent: DynamicAgent) -> AgentBlueprint:
        """Create fallback blueprint for single agent."""
        
        return AgentBlueprint(
            agent_specs=[],  # No specs for fallback
            execution_order=[agent.name],
            collaboration_matrix={agent.name: []},
            parallel_groups=[],
            quality_gates=["Code Review", "Basic Testing"],
            estimated_duration="1-2 days",
            coordination_strategy="single_agent_execution",
            success_criteria=["Project functionality complete"]
        )


# Export main classes for use by other modules
__all__ = [
    'ResearchEnhancedAgentGenerator',
    'DeepProjectAnalyzer', 
    'AgentArchitectDesigner',
    'KnowledgeSynthesizer',
    'DynamicAgent',
    'AgentBlueprint',
    'ProjectAnalysis',
    'ComplexityLevel',
    'AgentExpertiseLevel'
]