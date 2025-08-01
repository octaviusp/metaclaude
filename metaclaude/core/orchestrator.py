"""Execution orchestrator for MetaClaude."""

import time
import signal
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from contextlib import contextmanager

from ..docker.manager import DockerManager
from ..templates.manager import TemplateManager
from ..agents.selector import AgentSelector
from ..agents.claude_agentic_integration import ClaudeAgenticIntegration
from ..core.analyzer import IdeaAnalyzer
from ..utils.errors import MetaClaudeExecutionError, MetaClaudeTimeoutError
from ..utils.logging import get_logger, log_execution_start, log_execution_complete, log_execution_error

logger = get_logger(__name__)


class MetaClaudeOrchestrator:
    """Main orchestrator for MetaClaude execution flow."""
    
    def __init__(
        self,
        templates_dir: Path,
        output_base_dir: Path,
        docker_image: str = "metaclaude",
        docker_tag: str = "latest",
        enable_agentic_mode: bool = True,
    ):
        """Initialize MetaClaude orchestrator.
        
        Args:
            templates_dir: Path to templates directory
            output_base_dir: Base directory for output
            docker_image: Docker image name
            docker_tag: Docker image tag
            enable_agentic_mode: Whether to enable agentic agent creation
        """
        self.templates_dir = templates_dir
        self.output_base_dir = output_base_dir
        self.enable_agentic_mode = enable_agentic_mode
        
        # Initialize components
        self.docker_manager = DockerManager(docker_image, docker_tag)
        self.template_manager = TemplateManager(templates_dir)
        self.agent_selector = AgentSelector(templates_dir / ".claude" / "agents")
        self.idea_analyzer = IdeaAnalyzer()
        
        # Initialize agentic integration if enabled
        if self.enable_agentic_mode:
            self.agentic_integration = ClaudeAgenticIntegration(templates_dir, self.docker_manager)
            logger.info("Agentic mode enabled - Claude Code will create specialized agents")
        else:
            self.agentic_integration = None
            logger.info("Agentic mode disabled - using traditional agent selection")
        
        # Execution state
        self.current_container = None
        self.start_time = None
        self.timeout_seconds = None
        self.agentic_metadata = None
        
        logger.info("MetaClaude Orchestrator initialized")
    
    def execute(
        self,
        idea: str,
        model: str = "opus",
        force_agents: Optional[List[str]] = None,
        no_cache: bool = False,
        timeout: int = 14400,  # 4 hours
        keep_container: bool = False,
        custom_template_vars: Optional[Dict[str, Any]] = None,
        force_traditional_mode: bool = False,
    ) -> Dict[str, Any]:
        """Execute complete MetaClaude workflow.
        
        Args:
            idea: Project idea description
            model: Claude model to use
            force_agents: Optional list of agents to force include (ignored in agentic mode)
            no_cache: Whether to rebuild Docker image
            timeout: Execution timeout in seconds
            keep_container: Whether to keep container after execution
            custom_template_vars: Custom template variables
            force_traditional_mode: Force traditional agent selection (disable agentic mode)
            
        Returns:
            Execution results dictionary
            
        Raises:
            VCCExecutionError: If execution fails
            VCCTimeoutError: If execution times out
        """
        self.start_time = datetime.now()
        self.timeout_seconds = timeout
        
        log_execution_start("MetaClaude execution", {"idea": idea[:100] + "..." if len(idea) > 100 else idea})
        
        execution_results = {
            "idea": idea,
            "model": model,
            "start_time": self.start_time.isoformat(),
            "status": "started",
            "workspace_path": None,
            "output_path": None,
            "analysis": None,
            "selected_agents": [],
            "container_id": None,
            "execution_time": None,
            "error": None,
            "agentic_mode": self.enable_agentic_mode and not force_traditional_mode,
            "agentic_metadata": None,
        }
        
        try:
            with self._timeout_context(timeout):
                # Step 1: Prepare workspace
                workspace_path, output_path = self._prepare_workspace(idea)
                execution_results.update({
                    "workspace_path": str(workspace_path),
                    "output_path": str(output_path),
                })
                
                # Step 2: Analyze idea
                analysis = self._analyze_idea(idea)
                execution_results["analysis"] = analysis
                
                # Step 3: Build/prepare Docker runtime first
                self._build_runtime(no_cache)
                
                # Step 4: Launch container early for Claude-powered agent creation
                use_agentic = self.enable_agentic_mode and not force_traditional_mode
                if use_agentic:
                    # Launch container first for Claude agent creation
                    container = self._launch_claude_session_for_agent_creation(workspace_path, output_path, model)
                    execution_results["container_id"] = container.short_id
                    self.current_container = container
                    
                    # Now use Claude Code to create agents
                    selected_agents, agentic_metadata = asyncio.run(self._select_agentic_agents_with_claude(
                        idea, model, force_agents, custom_template_vars, container, workspace_path
                    ))
                    self.agentic_metadata = agentic_metadata
                    execution_results["agentic_metadata"] = agentic_metadata
                    execution_results["selected_agents"] = [agent.name for agent in selected_agents]
                    
                    # Step 5: Generate and inject configuration with Claude-created agents
                    self._inject_agentic_configuration(
                        workspace_path, idea, model, self.agentic_metadata, custom_template_vars
                    )
                    
                    # Step 6: Continue with existing container (no need to relaunch)
                    
                else:
                    # Traditional mode: select agents first, then launch container
                    selected_agents = self._select_agents(idea, force_agents, analysis)
                    self.agentic_metadata = None
                    execution_results["selected_agents"] = [agent.name for agent in selected_agents]
                    
                    # Step 5: Generate and inject configuration
                    self._inject_configuration(
                        workspace_path, idea, model, selected_agents, 
                        analysis, custom_template_vars
                    )
                    
                    # Step 6: Launch Claude Code session
                    container = self._launch_claude_session(workspace_path, output_path, model, idea)
                    execution_results["container_id"] = container.short_id
                    self.current_container = container
                
                # Step 7: Monitor execution
                self._monitor_progress(container, timeout)
                
                # Step 8: Handle completion
                execution_results["status"] = "completed"
                
                # Step 9: Cleanup
                self._cleanup(container, keep_container)
                
        except MetaClaudeTimeoutError as e:
            execution_results["status"] = "timeout"
            execution_results["error"] = str(e)
            log_execution_error("MetaClaude execution", e)
            if self.current_container:
                self._cleanup(self.current_container, keep_container)
            raise
            
        except Exception as e:
            execution_results["status"] = "failed"
            execution_results["error"] = str(e)
            log_execution_error("MetaClaude execution", e)
            if self.current_container:
                self._cleanup(self.current_container, keep_container)
            raise MetaClaudeExecutionError(f"MetaClaude execution failed: {e}")
        
        finally:
            if self.start_time:
                execution_time = (datetime.now() - self.start_time).total_seconds()
                execution_results["execution_time"] = execution_time
                log_execution_complete("MetaClaude execution", execution_time)
        
        return execution_results
    
    def _prepare_workspace(self, idea: str) -> tuple[Path, Path]:
        """Prepare workspace directories.
        
        Args:
            idea: Project idea for naming
            
        Returns:
            Tuple of (workspace_path, output_path)
        """
        log_execution_start("workspace preparation")
        
        # Generate timestamp-based workspace name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create safe project name from idea
        safe_name = "".join(c for c in idea[:30] if c.isalnum() or c in "-_").strip("-_")
        if not safe_name:
            safe_name = "project"
        
        workspace_name = f"{timestamp}_{safe_name}"
        workspace_path = self.output_base_dir / "metaclaude_output" / workspace_name
        output_path = workspace_path / "output"
        
        # Create directories
        workspace_path.mkdir(parents=True, exist_ok=True)
        output_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Workspace prepared: {workspace_path}")
        log_execution_complete("workspace preparation")
        
        return workspace_path, output_path
    
    def _analyze_idea(self, idea: str) -> Dict[str, Any]:
        """Analyze project idea.
        
        Args:
            idea: Project idea text
            
        Returns:
            Analysis results
        """
        log_execution_start("idea analysis")
        
        analysis = self.idea_analyzer.analyze_comprehensive(idea)
        
        logger.info(f"Idea analysis complete: {analysis['confidence']['overall']:.2f} confidence")
        log_execution_complete("idea analysis")
        
        return analysis
    
    def _select_agents(
        self,
        idea: str,
        force_agents: Optional[List[str]],
        analysis: Dict[str, Any],
    ) -> List[str]:
        """Select appropriate agents.
        
        Args:
            idea: Project idea
            force_agents: Forced agent selection
            analysis: Idea analysis results
            
        Returns:
            List of selected agent names
        """
        log_execution_start("agent selection")
        
        if force_agents:
            # Validate forced agents
            validation_errors = self.agent_selector.validate_agent_selection(force_agents)
            if validation_errors:
                logger.warning(f"Agent selection issues: {validation_errors}")
            
            selected_agents = force_agents
        else:
            # Automatic agent selection
            selected_agents = self.agent_selector.select_agents(idea, max_agents=4)
        
        logger.info(f"Selected agents: {selected_agents}")
        log_execution_complete("agent selection")
        
        return selected_agents
    
    async def _select_agentic_agents_with_claude(
        self,
        idea: str,
        model: str,
        force_agents: Optional[List[str]] = None,
        custom_template_vars: Optional[Dict[str, Any]] = None,
        container = None,
        workspace_path: Path = None,
    ) -> Tuple[List[Any], Dict[str, Any]]:
        """Select agents using Claude Code intelligence.
        
        Args:
            idea: Project idea description
            model: Claude model to use
            force_agents: Optional list of agents to force (ignored in Claude mode)
            custom_template_vars: Custom template variables
            container: Docker container instance
            workspace_path: Path to workspace directory
            
        Returns:
            Tuple of (agent configs, agentic metadata)
        """
        log_execution_start("Claude-powered agent creation")
        
        if force_agents:
            logger.warning("force_agents parameter ignored in Claude mode - Claude will determine optimal agents")
        
        try:
            # Use Claude Code to create agents intelligently
            agent_configs, agentic_metadata = await self.agentic_integration.create_agentic_agents(
                idea=idea,
                model=model,
                force_agents=None,  # Always let Claude decide
                custom_template_vars=custom_template_vars,
                container_id=container.short_id if container else None,
                workspace_path=workspace_path
            )
            
            agent_names = [config.name for config in agent_configs]
            logger.info(f"Claude created {len(agent_configs)} agents: {agent_names}")
            
            if agentic_metadata.get("agentic_mode"):
                logger.info(f"Claude coordination strategy: {agentic_metadata.get('coordination_strategy', 'unknown')}")
                logger.info(f"Estimated duration: {agentic_metadata.get('estimated_duration', 'unknown')}")
            else:
                logger.warning("Claude agent creation failed, using fallback agent")
            
            log_execution_complete("Claude-powered agent creation")
            return agent_configs, agentic_metadata
            
        except Exception as e:
            logger.error(f"Claude agent creation failed: {e}")
            # Fall back to traditional agent selection
            logger.info("Falling back to traditional agent selection")
            analysis = self._analyze_idea(idea)
            traditional_agents = self._select_agents(idea, None, analysis)
            
            # Convert to agent configs for consistency
            agent_configs = []
            for agent_name in traditional_agents:
                if agent_name in self.agent_selector.available_agents:
                    agent_configs.append(self.agent_selector.available_agents[agent_name])
            
            fallback_metadata = {"agentic_mode": False, "fallback": True, "error": str(e)}
            log_execution_complete("Claude-powered agent creation")
            return agent_configs, fallback_metadata
    
    async def _select_agentic_agents(
        self,
        idea: str,
        model: str,
        force_agents: Optional[List[str]],
        custom_template_vars: Optional[Dict[str, Any]]
    ) -> tuple[List[Any], Dict[str, Any]]:
        """Select agents using agentic AI-powered creation.
        
        Args:
            idea: Project idea
            model: Claude model
            force_agents: Ignored in agentic mode (AI decides agents)
            custom_template_vars: Custom template variables
            
        Returns:
            Tuple of (agent configs, agentic metadata)
        """
        log_execution_start("agentic agent creation")
        
        if force_agents:
            logger.warning("force_agents parameter ignored in agentic mode - AI will determine optimal agents")
        
        try:
            # Use agentic integration to create AI-determined agents
            agent_configs, agentic_metadata = await self.agentic_integration.create_agentic_agents(
                idea=idea,
                model=model,
                force_agents=None,  # Always let AI decide
                custom_template_vars=custom_template_vars
            )
            
            agent_names = [config.name for config in agent_configs]
            logger.info(f"Agentic agents created: {agent_names}")
            
            if agentic_metadata.get("agentic_mode"):
                logger.info(f"Agentic coordination strategy: {agentic_metadata.get('coordination_strategy', 'unknown')}")
            else:
                logger.warning("Agentic mode failed, using fallback agent")
            
            log_execution_complete("agentic agent creation")
            return agent_configs, agentic_metadata
            
        except Exception as e:
            logger.error(f"Agentic agent creation failed: {e}")
            # Fall back to traditional agent selection
            logger.info("Falling back to traditional agent selection")
            analysis = self._analyze_idea(idea)
            traditional_agents = self._select_agents(idea, None, analysis)
            
            # Convert to agent configs for consistency
            agent_configs = []
            for agent_name in traditional_agents:
                if agent_name in self.agent_selector.available_agents:
                    agent_configs.append(self.agent_selector.available_agents[agent_name])
            
            fallback_metadata = {"agentic_mode": False, "fallback": True, "error": str(e)}
            log_execution_complete("agentic agent creation")
            return agent_configs, fallback_metadata
    
    def _inject_agentic_configuration(
        self,
        workspace_path: Path,
        idea: str,
        model: str,
        agentic_metadata: Dict[str, Any],
        custom_template_vars: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Generate and inject agentic Claude configuration.
        
        Args:
            workspace_path: Workspace directory
            idea: Project idea
            model: Claude model
            agentic_metadata: Agentic execution metadata
            custom_template_vars: Custom template variables
        """
        log_execution_start("agentic configuration injection")
        
        try:
            if agentic_metadata.get("agentic_mode") and "dynamic_agents" in agentic_metadata:
                # Generate agentic Claude configuration
                dynamic_agents = agentic_metadata["dynamic_agents"]
                blueprint = agentic_metadata["blueprint"]
                
                self.agentic_integration.generate_claude_configuration(
                    workspace_path=workspace_path,
                    idea=idea,
                    model=model,
                    dynamic_agents=dynamic_agents,
                    blueprint=blueprint,
                    custom_template_vars=custom_template_vars
                )
                
                logger.info(f"Agentic configuration generated for {len(dynamic_agents)} agents")
            else:
                # Fall back to traditional configuration
                logger.warning("Agentic metadata incomplete, falling back to traditional configuration")
                analysis = self._analyze_idea(idea)
                selected_agents = self._select_agents(idea, None, analysis)
                self._inject_configuration(
                    workspace_path, idea, model, selected_agents, analysis, custom_template_vars
                )
            
            log_execution_complete("agentic configuration injection")
            
        except Exception as e:
            logger.error(f"Agentic configuration injection failed: {e}")
            # Fall back to traditional configuration
            logger.info("Falling back to traditional configuration injection")
            analysis = self._analyze_idea(idea)
            selected_agents = self._select_agents(idea, None, analysis)
            self._inject_configuration(
                workspace_path, idea, model, selected_agents, analysis, custom_template_vars
            )
    
    def _build_runtime(self, no_cache: bool = False) -> None:
        """Build or verify Docker runtime.
        
        Args:
            no_cache: Whether to force rebuild
        """
        log_execution_start("Docker runtime preparation")
        
        dockerfile_path = self.templates_dir.parent / "docker"
        
        # Check if image exists and decide whether to build
        should_build = no_cache or not self.docker_manager.image_exists()
        
        if should_build:
            logger.info("Building Docker image...")
            self.docker_manager.build_image(dockerfile_path, no_cache=no_cache)
        else:
            logger.info("Using existing Docker image")
        
        log_execution_complete("Docker runtime preparation")
    
    def _inject_configuration(
        self,
        workspace_path: Path,
        idea: str,
        model: str,
        selected_agents: List[str],
        analysis: Dict[str, Any],
        custom_template_vars: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Generate and inject Claude configuration.
        
        Args:
            workspace_path: Workspace directory
            idea: Project idea
            model: Claude model
            selected_agents: Selected agents
            analysis: Idea analysis
            custom_template_vars: Custom template variables
        """
        log_execution_start("configuration injection")
        
        # Generate project name and description
        project_name = self._generate_project_name(idea, analysis)
        project_description = self._generate_project_description(idea, analysis)
        
        # Prepare template variables
        template_vars = {
            "model": model,
            "project_name": project_name,
            "project_description": project_description,
            "idea": idea,
            "domains": analysis["domains"],
            "technologies": analysis["technologies"],
            "complexity": analysis["complexity"]["level"],
            "project_type": analysis["project_type"],
        }
        
        if custom_template_vars:
            template_vars.update(custom_template_vars)
        
        # Render configuration
        self.template_manager.render_claude_config(
            output_dir=workspace_path,
            model=model,
            project_name=project_name,
            project_description=project_description,
            selected_agents=selected_agents,
            template_vars=template_vars,
        )
        
        logger.info(f"Configuration injected for {len(selected_agents)} agents")
        log_execution_complete("configuration injection")
    
    def _launch_claude_session_for_agent_creation(
        self,
        workspace_path: Path,
        output_path: Path,
        model: str,
    ) -> Any:
        """Launch Claude Code container early for agent creation.
        
        Args:
            workspace_path: Workspace directory
            output_path: Output directory
            model: Claude model
            
        Returns:
            Running container instance
        """
        log_execution_start("Claude Code container launch for agent creation")
        
        # Prepare environment variables
        import os
        anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "")
        if not anthropic_api_key:
            logger.warning("No ANTHROPIC_API_KEY found in environment. Claude Code may not work properly.")
            
        environment = {
            "CLAUDE_MODEL": model,
            "CLAUDE_AUTO_COMPACT": "false",
            "ANTHROPIC_API_KEY": anthropic_api_key
        }
        
        # Start container (don't launch Claude Code yet, just prepare environment)
        container = self.docker_manager.run_container(
            workspace_path=workspace_path,
            output_path=output_path,
            environment=environment,
            command=None  # No command yet, container stays running
        )
        
        logger.info(f"Container {container.short_id} started for agent creation")
        log_execution_complete("Claude Code container launch for agent creation")
        
        return container
    
    def _launch_claude_session(
        self,
        workspace_path: Path,
        output_path: Path,
        model: str,
        idea: str,
    ) -> Any:
        """Launch Claude Code session in container.
        
        Args:
            workspace_path: Workspace directory
            output_path: Output directory
            model: Claude model
            idea: Project idea/description
            
        Returns:
            Running container instance
        """
        log_execution_start("Claude Code session launch")
        
        # Prepare environment variables
        import os
        anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "")
        if not anthropic_api_key:
            logger.warning("No ANTHROPIC_API_KEY found in environment. Claude Code may not work properly.")
            
        environment = {
            "CLAUDE_MODEL": model,
            "CLAUDE_AUTO_COMPACT": "false",
            "CLAUDE_MAX_THINKING_TOKENS": "32000",
            "ANTHROPIC_API_KEY": anthropic_api_key,
        }
        
        # Create a comprehensive prompt for Claude Code
        claude_prompt = f'''Please create a complete software project based on this idea: "{idea}"

Instructions:
1. Analyze the requirements and create a full project structure
2. Generate all necessary files including source code, configuration, and documentation
3. Follow best practices for the chosen technology stack
4. Create a comprehensive README with setup and usage instructions
5. Include any necessary build scripts, package files, or configuration
6. Make sure the project is ready to run with minimal setup

Please create this project in the current directory and provide a summary when complete.'''
        
        # Create a startup script for Claude Code
        escaped_prompt = claude_prompt.replace('"', '\\"').replace('$', '\\$').replace('`', '\\`')
        startup_script = f'''#!/bin/bash
set -e
echo "Starting Claude Code session..."
cd /workspace
echo "Working directory: $(pwd)"
echo "Files in workspace: $(ls -la)"

# Check if API key is available
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "WARNING: No ANTHROPIC_API_KEY found. Claude Code requires authentication."
    echo "Please set your ANTHROPIC_API_KEY environment variable."
    echo "For testing purposes, creating a mock project structure..."
    
    # Create a basic mock project structure for demonstration
    mkdir -p /workspace/output/src /workspace/output/public
    echo "# {idea}" > /workspace/output/README.md
    echo "Mock project created for: {idea}" >> /workspace/output/README.md
    echo "{{\"name\": \"mock-project\", \"version\": \"1.0.0\"}}" > /workspace/output/package.json
    echo "console.log('Mock project for: {idea}');" > /workspace/output/src/index.js
    
    echo "Mock project structure created in /workspace/output/"
else
    # Run Claude Code with the comprehensive prompt
    echo "Launching Claude Code with project generation prompt..."
    cd /workspace/output
    claude --dangerously-skip-permissions --print "{escaped_prompt}"
    
    echo "Claude Code session completed"
fi

echo "Generated files:"
ls -la /workspace/output/
'''
        
        # Write startup script to workspace
        script_path = workspace_path / "startup.sh"
        script_path.write_text(startup_script)
        script_path.chmod(0o755)
        
        # Start container with the startup script
        container = self.docker_manager.run_container(
            workspace_path=workspace_path,
            output_path=output_path,
            command="bash /workspace/startup.sh",
            environment=environment,
        )
        
        logger.info(f"Claude Code session started in container {container.short_id}")
        log_execution_complete("Claude Code session launch")
        
        return container
    
    def _monitor_progress(self, container: Any, timeout: int) -> None:
        """Monitor container execution progress.
        
        Args:
            container: Docker container
            timeout: Timeout in seconds
        """
        log_execution_start("execution monitoring")
        
        start_time = time.time()
        
        try:
            # Monitor logs in real-time
            for log_line in self.docker_manager.monitor_logs(container):
                elapsed = time.time() - start_time
                
                # Check timeout (skip if timeout is 0 = unlimited)
                if timeout > 0 and elapsed > timeout:
                    raise VCCTimeoutError(f"Execution timed out after {timeout} seconds")
                
                # Log progress
                logger.debug(f"[Container] {log_line}")
                
                # Check for completion indicators
                if self._is_execution_complete(log_line):
                    logger.info("Execution completed successfully")
                    break
                
                # Check for errors
                if self._is_execution_error(log_line):
                    logger.error(f"Execution error detected: {log_line}")
                
        except Exception as e:
            if isinstance(e, VCCTimeoutError):
                raise
            logger.error(f"Monitoring error: {e}")
        
        log_execution_complete("execution monitoring")
    
    def _is_execution_complete(self, log_line: str) -> bool:
        """Check if execution is complete based on log line.
        
        Args:
            log_line: Log line from container
            
        Returns:
            True if execution appears complete
        """
        completion_indicators = [
            "Project generation complete",
            "All tasks completed",
            "Claude Code session ended",
            "Generation successful",
        ]
        
        return any(indicator.lower() in log_line.lower() for indicator in completion_indicators)
    
    def _is_execution_error(self, log_line: str) -> bool:
        """Check if log line indicates an error.
        
        Args:
            log_line: Log line from container
            
        Returns:
            True if line indicates error
        """
        error_indicators = [
            "ERROR:",
            "FATAL:",
            "Exception:",
            "failed",
            "error",
        ]
        
        return any(indicator.lower() in log_line.lower() for indicator in error_indicators)
    
    def _cleanup(self, container: Any, keep_container: bool = False) -> None:
        """Clean up resources after execution.
        
        Args:
            container: Docker container
            keep_container: Whether to keep container for debugging
        """
        log_execution_start("cleanup")
        
        try:
            # Stop container
            self.docker_manager.stop_container(container)
            
            # Clean up container
            self.docker_manager.cleanup_container(container, keep=keep_container)
            
        except Exception as e:
            logger.warning(f"Cleanup error: {e}")
        
        self.current_container = None
        log_execution_complete("cleanup")
    
    def _generate_project_name(self, idea: str, analysis: Dict[str, Any]) -> str:
        """Generate project name from idea and analysis.
        
        Args:
            idea: Original idea
            analysis: Analysis results
            
        Returns:
            Generated project name
        """
        # Extract key words from idea
        words = idea.split()[:5]  # First 5 words
        safe_words = []
        
        for word in words:
            # Clean word
            clean_word = "".join(c for c in word if c.isalnum())
            if clean_word and len(clean_word) > 2:
                safe_words.append(clean_word.title())
        
        if safe_words:
            base_name = "".join(safe_words)
        else:
            base_name = "GeneratedProject"
        
        # Add domain suffix if relevant
        if analysis["domains"]:
            domain = analysis["domains"][0]
            domain_suffix = domain.title().replace("_", "")
            if domain_suffix.lower() not in base_name.lower():
                base_name += domain_suffix
        
        return base_name[:50]  # Limit length
    
    def _generate_project_description(self, idea: str, analysis: Dict[str, Any]) -> str:
        """Generate project description from idea and analysis.
        
        Args:
            idea: Original idea
            analysis: Analysis results
            
        Returns:
            Generated project description
        """
        # Start with original idea
        description = idea.strip()
        
        # Add analysis insights
        if analysis["domains"]:
            domains_str = ", ".join(analysis["domains"])
            description += f"\n\nDomains: {domains_str}"
        
        if analysis["technologies"]:
            tech_str = ", ".join(analysis["technologies"])
            description += f"\nTechnologies: {tech_str}"
        
        description += f"\nComplexity: {analysis['complexity']['level']}"
        description += f"\nProject Type: {analysis['project_type']}"
        
        return description
    
    @contextmanager
    def _timeout_context(self, timeout_seconds: int):
        """Context manager for execution timeout.
        
        Args:
            timeout_seconds: Timeout in seconds
        """
        def timeout_handler(signum, frame):
            raise VCCTimeoutError(f"Execution timed out after {timeout_seconds} seconds")
        
        # Set up signal handler
        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(timeout_seconds)
        
        try:
            yield
        finally:
            # Restore old handler and cancel alarm
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)