"""Idea analysis engine for VCC."""

import re
from typing import Dict, List, Set, Any, Optional, Tuple
from collections import Counter
from pathlib import Path

from ..utils.logging import get_logger

logger = get_logger(__name__)


class IdeaAnalyzer:
    """Analyzes project ideas to extract requirements and suggest configurations."""
    
    def __init__(self):
        """Initialize idea analyzer."""
        self.domain_patterns = self._load_domain_patterns()
        self.tech_patterns = self._load_tech_patterns()
        self.complexity_indicators = self._load_complexity_indicators()
        self.project_type_patterns = self._load_project_type_patterns()
        
        logger.info("IdeaAnalyzer initialized")
    
    def _load_domain_patterns(self) -> Dict[str, List[str]]:
        """Load domain detection patterns."""
        return {
            "web": [
                r"\bweb(?:site|app)?\b",
                r"\bfrontend\b",
                r"\bbackend\b",
                r"\bfull[- ]?stack\b",
                r"\breact\b",
                r"\bvue\b",
                r"\bangular\b",
                r"\bnode(?:\.js)?\b",
                r"\bexpress\b",
                r"\bapi\b",
                r"\brest\b",
                r"\bgraphql\b",
                r"\bhtml\b",
                r"\bcss\b",
                r"\bjavascript\b",
                r"\btypescript\b",
                r"\bnext\.js\b",
                r"\bnuxt\b",
                r"\bsvelte\b",
                r"\belectron\b",
            ],
            "mobile": [
                r"\bmobile\b",
                r"\bapp\b",
                r"\bios\b",
                r"\bandroid\b",
                r"\breact native\b",
                r"\bflutter\b",
                r"\bswift\b",
                r"\bkotlin\b",
                r"\bxamarin\b",
                r"\bcordova\b",
                r"\bionic\b",
                r"\bphone\b",
                r"\btablet\b",
            ],
            "ml": [
                r"\bmachine learning\b",
                r"\bml\b",
                r"\bai\b",
                r"\bartificial intelligence\b",
                r"\bdeep learning\b",
                r"\bneural network\b",
                r"\bmodel\b",
                r"\bpytorch\b",
                r"\btensorflow\b",
                r"\bscikit[- ]?learn\b",
                r"\bpandas\b",
                r"\bnumpy\b",
                r"\bdata science\b",
                r"\bprediction\b",
                r"\bclassification\b",
                r"\bregression\b",
                r"\bnlp\b",
                r"\bnatural language\b",
                r"\bcomputer vision\b",
                r"\bcv\b",
                r"\btransformers\b",
                r"\bbert\b",
                r"\bgpt\b",
            ],
            "data": [
                r"\bdata\b",
                r"\banalytics\b",
                r"\bdatabase\b",
                r"\bsql\b",
                r"\bnosql\b",
                r"\bmongodb\b",
                r"\bpostgresql\b",
                r"\bmysql\b",
                r"\bredis\b",
                r"\belasticsearch\b",
                r"\betl\b",
                r"\bpipeline\b",
                r"\bwarehouse\b",
                r"\bbigquery\b",
                r"\bspark\b",
                r"\bhadoop\b",
                r"\bkafka\b",
                r"\bairflow\b",
            ],
            "devops": [
                r"\bdevops\b",
                r"\binfrastructure\b",
                r"\bdeployment\b",
                r"\bci/cd\b",
                r"\bdocker\b",
                r"\bkubernetes\b",
                r"\baws\b",
                r"\bazure\b",
                r"\bgcp\b",
                r"\bcloud\b",
                r"\bterraform\b",
                r"\bansible\b",
                r"\bjenkins\b",
                r"\bgithub actions\b",
                r"\bmonitoring\b",
                r"\bprometheus\b",
                r"\bgrafana\b",
                r"\bhelm\b",
            ],
            "desktop": [
                r"\bdesktop\b",
                r"\bgui\b",
                r"\btkinter\b",
                r"\bqt\b",
                r"\bgtk\b",
                r"\bwpf\b",
                r"\bwinforms\b",
                r"\belectron\b",
                r"\btauri\b",
                r"\bnative\b",
                r"\bcross[- ]?platform\b",
            ],
            "game": [
                r"\bgame\b",
                r"\bgaming\b",
                r"\bunity\b",
                r"\bunreal\b",
                r"\bgodot\b",
                r"\bpygame\b",
                r"\bthree\.js\b",
                r"\bwebgl\b",
                r"\bopengl\b",
                r"\bvulkan\b",
                r"\bdirectx\b",
                r"\b2d\b",
                r"\b3d\b",
            ],
            "blockchain": [
                r"\bblockchain\b",
                r"\bcrypto\b",
                r"\bweb3\b",
                r"\bethereum\b",
                r"\bbitcoin\b",
                r"\bsolidity\b",
                r"\bsmart contract\b",
                r"\bdefi\b",
                r"\bnft\b",
                r"\bdapp\b",
                r"\bmetamask\b",
            ],
        }
    
    def _load_tech_patterns(self) -> Dict[str, List[str]]:
        """Load technology detection patterns."""
        return {
            "python": [r"\bpython\b", r"\bdjango\b", r"\bflask\b", r"\bfastapi\b"],
            "javascript": [r"\bjavascript\b", r"\bjs\b", r"\bnode\b", r"\bnpm\b"],
            "typescript": [r"\btypescript\b", r"\bts\b"],
            "react": [r"\breact\b", r"\bjsx\b", r"\bnext\.js\b"],
            "vue": [r"\bvue\b", r"\bnuxt\b"],
            "angular": [r"\bangular\b"],
            "node": [r"\bnode(?:\.js)?\b", r"\bexpress\b", r"\bnestjs\b"],
            "docker": [r"\bdocker\b", r"\bcontainer\b"],
            "kubernetes": [r"\bkubernetes\b", r"\bk8s\b"],
            "aws": [r"\baws\b", r"\bamazon\b"],
            "terraform": [r"\bterraform\b", r"\biac\b"],
            "pytorch": [r"\bpytorch\b", r"\btorch\b"],
            "tensorflow": [r"\btensorflow\b", r"\btf\b", r"\bkeras\b"],
        }
    
    def _load_complexity_indicators(self) -> Dict[str, int]:
        """Load complexity indicator patterns and weights."""
        return {
            r"\benterprise\b": 3,
            r"\bscalable\b": 2,
            r"\bscaling\b": 2,
            r"\bdistributed\b": 3,
            r"\bmicroservices\b": 3,
            r"\breal[- ]?time\b": 2,
            r"\bhigh[- ]?performance\b": 2,
            r"\bmachine learning\b": 2,
            r"\bai\b": 2,
            r"\bblockchain\b": 3,
            r"\badvanced\b": 1,
            r"\bcomplex\b": 2,
            r"\bsophisticated\b": 2,
            r"\bmulti[- ]?tenant\b": 3,
            r"\bcustom\b": 1,
            r"\bintegration\b": 1,
            r"\bmulti[- ]?platform\b": 2,
            r"\bcross[- ]?platform\b": 2,
        }
    
    def _load_project_type_patterns(self) -> Dict[str, List[str]]:
        """Load project type detection patterns."""
        return {
            "api": [r"\bapi\b", r"\brest\b", r"\bgraphql\b", r"\bbackend\b", r"\bservice\b"],
            "webapp": [r"\bweb app\b", r"\bwebsite\b", r"\bfrontend\b", r"\bdashboard\b"],
            "mobile_app": [r"\bmobile app\b", r"\bios app\b", r"\bandroid app\b"],
            "desktop_app": [r"\bdesktop app\b", r"\bgui\b", r"\bapplication\b"],
            "cli": [r"\bcli\b", r"\bcommand line\b", r"\bterminal\b", r"\bscript\b"],
            "library": [r"\blibrary\b", r"\bpackage\b", r"\bmodule\b", r"\bsdk\b"],
            "data_pipeline": [r"\bpipeline\b", r"\betl\b", r"\bdata processing\b"],
            "ml_model": [r"\bmodel\b", r"\bprediction\b", r"\bclassification\b", r"\bml\b"],
            "game": [r"\bgame\b", r"\bgaming\b"],
            "ecommerce": [r"\becommerce\b", r"\be-commerce\b", r"\bshop\b", r"\bstore\b"],
            "cms": [r"\bcms\b", r"\bcontent management\b", r"\bblog\b"],
            "crm": [r"\bcrm\b", r"\bcustomer\b", r"\brelationship\b"],
            "social": [r"\bsocial\b", r"\bchat\b", r"\bmessaging\b", r"\bforum\b"],
        }
    
    def extract_keywords(self, idea: str) -> Dict[str, List[str]]:
        """Extract domain and technology keywords from idea.
        
        Args:
            idea: Project idea text
            
        Returns:
            Dictionary with 'domains' and 'technologies' lists
        """
        idea_lower = idea.lower()
        
        # Extract domains
        detected_domains = []
        for domain, patterns in self.domain_patterns.items():
            for pattern in patterns:
                if re.search(pattern, idea_lower):
                    detected_domains.append(domain)
                    break
        
        # Extract technologies
        detected_technologies = []
        for tech, patterns in self.tech_patterns.items():
            for pattern in patterns:
                if re.search(pattern, idea_lower):
                    detected_technologies.append(tech)
                    break
        
        # Remove duplicates while preserving order
        domains = list(dict.fromkeys(detected_domains))
        technologies = list(dict.fromkeys(detected_technologies))
        
        logger.debug(f"Extracted domains: {domains}")
        logger.debug(f"Extracted technologies: {technologies}")
        
        return {
            "domains": domains,
            "technologies": technologies,
        }
    
    def detect_technologies(self, idea: str) -> List[str]:
        """Detect specific technologies mentioned in the idea.
        
        Args:
            idea: Project idea text
            
        Returns:
            List of detected technologies
        """
        keywords = self.extract_keywords(idea)
        return keywords["technologies"]
    
    def estimate_complexity(self, idea: str) -> Dict[str, Any]:
        """Estimate project complexity based on various indicators.
        
        Args:
            idea: Project idea text
            
        Returns:
            Dictionary with complexity analysis
        """
        idea_lower = idea.lower()
        
        # Count complexity indicators
        complexity_score = 0
        matched_indicators = []
        
        for pattern, weight in self.complexity_indicators.items():
            matches = re.findall(pattern, idea_lower)
            if matches:
                complexity_score += weight * len(matches)
                matched_indicators.extend(matches)
        
        # Additional complexity factors
        word_count = len(idea.split())
        sentence_count = len(re.split(r'[.!?]+', idea))
        
        # Adjust score based on length (longer descriptions often indicate complexity)
        if word_count > 50:
            complexity_score += 1
        if word_count > 100:
            complexity_score += 1
        
        # Determine complexity level
        if complexity_score >= 6:
            complexity_level = "high"
        elif complexity_score >= 3:
            complexity_level = "medium"
        else:
            complexity_level = "low"
        
        return {
            "level": complexity_level,
            "score": complexity_score,
            "indicators": matched_indicators,
            "word_count": word_count,
            "sentence_count": sentence_count,
        }
    
    def suggest_agents(self, idea: str) -> List[str]:
        """Suggest appropriate agents based on idea analysis.
        
        Args:
            idea: Project idea text
            
        Returns:
            List of suggested agent names
        """
        keywords = self.extract_keywords(idea)
        complexity = self.estimate_complexity(idea)
        project_type = self.detect_project_type(idea)
        
        suggested_agents = set()
        
        # Domain-based agent suggestions
        domain_agent_map = {
            "web": ["fullstack-engineer"],
            "mobile": ["fullstack-engineer"],
            "ml": ["ml-dl-engineer"],
            "data": ["ml-dl-engineer", "fullstack-engineer"],
            "devops": ["devops-engineer"],
            "desktop": ["fullstack-engineer"],
            "game": ["fullstack-engineer"],
            "blockchain": ["fullstack-engineer"],
        }
        
        for domain in keywords["domains"]:
            if domain in domain_agent_map:
                suggested_agents.update(domain_agent_map[domain])
        
        # Technology-based suggestions
        tech_agent_map = {
            "python": ["ml-dl-engineer", "fullstack-engineer"],
            "javascript": ["fullstack-engineer"],
            "typescript": ["fullstack-engineer"],
            "react": ["fullstack-engineer"],
            "node": ["fullstack-engineer"],
            "docker": ["devops-engineer"],
            "kubernetes": ["devops-engineer"],
            "aws": ["devops-engineer"],
            "terraform": ["devops-engineer"],
            "pytorch": ["ml-dl-engineer"],
            "tensorflow": ["ml-dl-engineer"],
        }
        
        for tech in keywords["technologies"]:
            if tech in tech_agent_map:
                suggested_agents.update(tech_agent_map[tech])
        
        # Complexity-based suggestions
        if complexity["level"] == "high":
            suggested_agents.add("devops-engineer")
            suggested_agents.add("qa-engineer")
        elif complexity["level"] == "medium":
            suggested_agents.add("qa-engineer")
        
        # Project type considerations
        if project_type in ["api", "webapp", "library"]:
            suggested_agents.add("qa-engineer")
        
        # Default fallback
        if not suggested_agents:
            suggested_agents.add("fullstack-engineer")
        
        # Ensure reasonable limits
        result = list(suggested_agents)[:4]
        
        logger.info(f"Suggested agents: {result}")
        return result
    
    def detect_project_type(self, idea: str) -> str:
        """Detect the type of project from the idea.
        
        Args:
            idea: Project idea text
            
        Returns:
            Detected project type
        """
        idea_lower = idea.lower()
        
        # Score each project type
        type_scores = {}
        for ptype, patterns in self.project_type_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, idea_lower))
                score += matches
            if score > 0:
                type_scores[ptype] = score
        
        # Return highest scoring type
        if type_scores:
            detected_type = max(type_scores.items(), key=lambda x: x[1])[0]
            logger.debug(f"Detected project type: {detected_type}")
            return detected_type
        
        return "general"
    
    def analyze_comprehensive(self, idea: str) -> Dict[str, Any]:
        """Perform comprehensive analysis of the project idea.
        
        Args:
            idea: Project idea text
            
        Returns:
            Comprehensive analysis results
        """
        logger.info("Performing comprehensive idea analysis")
        
        keywords = self.extract_keywords(idea)
        complexity = self.estimate_complexity(idea)
        project_type = self.detect_project_type(idea)
        suggested_agents = self.suggest_agents(idea)
        
        # Additional analysis
        word_count = len(idea.split())
        char_count = len(idea)
        
        # Confidence scoring
        confidence = self._calculate_confidence(keywords, complexity, project_type)
        
        analysis = {
            "idea": idea,
            "domains": keywords["domains"],
            "technologies": keywords["technologies"],
            "complexity": complexity,
            "project_type": project_type,
            "suggested_agents": suggested_agents,
            "confidence": confidence,
            "meta": {
                "word_count": word_count,
                "char_count": char_count,
                "has_specific_requirements": len(keywords["domains"]) > 0 or len(keywords["technologies"]) > 0,
            }
        }
        
        logger.info(f"Analysis complete: {len(keywords['domains'])} domains, {len(keywords['technologies'])} technologies, {complexity['level']} complexity")
        return analysis
    
    def _calculate_confidence(
        self,
        keywords: Dict[str, List[str]],
        complexity: Dict[str, Any],
        project_type: str,
    ) -> Dict[str, float]:
        """Calculate confidence scores for analysis results.
        
        Args:
            keywords: Extracted keywords
            complexity: Complexity analysis
            project_type: Detected project type
            
        Returns:
            Confidence scores for different aspects
        """
        domain_confidence = min(len(keywords["domains"]) * 0.25, 1.0)
        tech_confidence = min(len(keywords["technologies"]) * 0.2, 1.0)
        complexity_confidence = min(complexity["score"] * 0.15, 1.0)
        type_confidence = 0.8 if project_type != "general" else 0.3
        
        overall_confidence = (
            domain_confidence * 0.3 +
            tech_confidence * 0.25 +
            complexity_confidence * 0.2 +
            type_confidence * 0.25
        )
        
        return {
            "overall": overall_confidence,
            "domains": domain_confidence,
            "technologies": tech_confidence,
            "complexity": complexity_confidence,
            "project_type": type_confidence,
        }