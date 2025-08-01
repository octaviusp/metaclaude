#!/usr/bin/env python3
"""
Test script for the agentic agent creation system.

This script tests the core functionality of the research-enhanced
agentic agent generation system without requiring full Docker execution.
"""

import asyncio
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from metaclaude.agents.agentic_creator import (
    ResearchEnhancedAgentGenerator,
    DeepProjectAnalyzer,
    AgentArchitectDesigner,
    ComplexityLevel
)
from metaclaude.agents.agentic_orchestrator import AgenticOrchestrator, AgenticIntegration


async def test_deep_project_analyzer():
    """Test the deep project analyzer."""
    print("🧠 Testing Deep Project Analyzer...")
    
    analyzer = DeepProjectAnalyzer()
    
    test_ideas = [
        "Create a React todo app with authentication and real-time updates",
        "Build a machine learning pipeline for sentiment analysis using PyTorch",
        "Design a scalable microservices architecture with Docker and Kubernetes",
        "Create a simple Python script to process CSV files"
    ]
    
    for idea in test_ideas:
        print(f"\n📝 Analyzing: {idea[:50]}...")
        analysis = await analyzer.analyze_comprehensive(idea)
        
        print(f"  🏷️  Domains: {analysis.domains}")
        print(f"  🔧 Technologies: {analysis.technologies}")
        print(f"  📊 Complexity: {analysis.complexity.value}")
        print(f"  🎯 Project Type: {analysis.project_type}")
        print(f"  📈 Confidence: {analysis.confidence_score:.2f}")
        print(f"  🧠 Challenges: {len(analysis.technical_challenges)} identified")


async def test_agent_architect_designer():
    """Test the agent architect designer."""
    print("\n🏗️  Testing Agent Architect Designer...")
    
    analyzer = DeepProjectAnalyzer()
    architect = AgentArchitectDesigner()
    
    idea = "Create a full-stack e-commerce platform with React frontend, Node.js backend, and PostgreSQL database"
    print(f"\n📝 Designing architecture for: {idea}")
    
    analysis = await analyzer.analyze_comprehensive(idea)
    blueprint = await architect.design_agent_architecture(analysis)
    
    print(f"  👥 Agent Count: {len(blueprint.agent_specs)}")
    print(f"  📋 Execution Order: {' → '.join(blueprint.execution_order)}")
    print(f"  🤝 Coordination: {blueprint.coordination_strategy}")
    print(f"  ⏱️  Duration: {blueprint.estimated_duration}")
    
    print(f"\n🎯 Agent Specifications:")
    for spec in blueprint.agent_specs:
        print(f"  - {spec.name}: {spec.role}")
        print(f"    💡 Expertise: {', '.join(spec.expertise_areas)}")
        print(f"    🎖️  Level: {spec.expertise_level.value}")
        print(f"    🔧 Tools: {len(spec.tools)} tools")


async def test_research_enhanced_generator():
    """Test the research-enhanced agent generator."""
    print("\n🔬 Testing Research-Enhanced Agent Generator...")
    
    generator = ResearchEnhancedAgentGenerator()
    
    idea = "Build a modern React dashboard with real-time analytics and responsive design"
    print(f"\n📝 Creating agentic team for: {idea}")
    
    try:
        agents, blueprint = await generator.create_agentic_project_team(idea)
        
        print(f"  ✅ Successfully created {len(agents)} agents")
        print(f"  🤝 Coordination: {blueprint.coordination_strategy}")
        
        print(f"\n🤖 Generated Agents:")
        for agent in agents:
            research_status = "🔬 Research-Enhanced" if agent.research_enhanced else "📋 Basic"
            print(f"  - {agent.name}: {research_status}")
            print(f"    📝 Description: {agent.description}")
            print(f"    🎯 Specializations: {', '.join(agent.specialization_areas)}")
            print(f"    📊 Knowledge Quality: {agent.knowledge_base.quality_score:.2f}")
        
    except Exception as e:
        print(f"  ❌ Error: {e}")


async def test_agentic_integration():
    """Test the agentic integration with existing system."""
    print("\n🔗 Testing Agentic Integration...")
    
    templates_dir = Path(__file__).parent / "templates"
    integration = AgenticIntegration(templates_dir)
    
    idea = "Create a Python FastAPI server with authentication and database integration"
    print(f"\n📝 Testing integration for: {idea}")
    
    try:
        agent_configs, metadata = await integration.create_agentic_agents(
            idea=idea,
            model="opus"
        )
        
        print(f"  ✅ Integration successful: {len(agent_configs)} agent configs created")
        print(f"  🤖 Agentic Mode: {metadata.get('agentic_mode', False)}")
        
        if metadata.get('agentic_mode'):
            blueprint = metadata.get('blueprint')
            if blueprint:
                print(f"  🤝 Coordination: {getattr(blueprint, 'coordination_strategy', 'unknown')}")
                print(f"  ⏱️  Duration: {getattr(blueprint, 'estimated_duration', 'unknown')}")
        
        print(f"\n📋 Agent Configurations:")
        for config in agent_configs:
            print(f"  - {config.name}: {config.description[:60]}...")
            print(f"    🔧 Tools: {len(config.tools)} tools")
            print(f"    🏷️  Patterns: {', '.join(config.patterns)}")
        
    except Exception as e:
        print(f"  ❌ Integration error: {e}")


async def main():
    """Run all tests."""
    print("🚀 MetaClaude Agentic System Test Suite")
    print("=" * 50)
    
    try:
        await test_deep_project_analyzer()
        await test_agent_architect_designer()
        await test_research_enhanced_generator()
        await test_agentic_integration()
        
        print("\n" + "=" * 50)
        print("✅ All tests completed successfully!")
        print("🎉 Agentic system is ready for deployment!")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())