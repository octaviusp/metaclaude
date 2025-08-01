"""Docker management module for MetaClaude runtime environment."""

import time
from pathlib import Path
from typing import Dict, Any, Optional, Generator
import docker
from docker.models.containers import Container
from docker.models.images import Image
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

from ..utils.errors import MetaClaudeDockerError
from ..utils.logging import get_logger

logger = get_logger(__name__)
console = Console()


class DockerManager:
    """Manages Docker operations for MetaClaude runtime environment."""
    
    def __init__(self, image_name: str = "metaclaude", image_tag: str = "latest"):
        """Initialize Docker manager.
        
        Args:
            image_name: Name for the Docker image
            image_tag: Tag for the Docker image
        """
        self.image_name = image_name
        self.image_tag = image_tag
        self.full_image_name = f"{image_name}:{image_tag}"
        
        try:
            self.client = docker.from_env()
            # Test Docker connection
            self.client.ping()
            logger.info("Docker connection established")
        except Exception as e:
            raise MetaClaudeDockerError(f"Failed to connect to Docker daemon: {e}")
    
    def build_image(self, dockerfile_path: Path, no_cache: bool = False) -> Image:
        """Build or rebuild the Docker image.
        
        Args:
            dockerfile_path: Path to the Dockerfile directory
            no_cache: Whether to disable build cache
            
        Returns:
            Built Docker image
            
        Raises:
            MetaClaudeDockerError: If image build fails
        """
        logger.info(f"Building Docker image {self.full_image_name}")
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                console=console,
            ) as progress:
                build_task = progress.add_task("Building Docker image...", total=None)
                
                # Build the image
                image, build_logs = self.client.images.build(
                    path=str(dockerfile_path),
                    tag=self.full_image_name,
                    nocache=no_cache,
                    rm=True,
                    forcerm=True,
                )
                
                progress.update(build_task, completed=True)
                
            logger.info(f"Docker image {self.full_image_name} built successfully")
            return image
            
        except Exception as e:
            logger.error(f"Failed to build Docker image: {e}")
            raise MetaClaudeDockerError(f"Docker image build failed: {e}")
    
    def image_exists(self) -> bool:
        """Check if the Docker image exists locally.
        
        Returns:
            True if image exists, False otherwise
        """
        try:
            self.client.images.get(self.full_image_name)
            return True
        except docker.errors.ImageNotFound:
            return False
    
    def run_container(
        self,
        workspace_path: Path,
        output_path: Path,
        command: Optional[str] = None,
        environment: Optional[Dict[str, str]] = None,
        timeout: int = 14400,  # 4 hours default
    ) -> Container:
        """Run MetaClaude container with mounted volumes.
        
        Args:
            workspace_path: Path to workspace directory on host
            output_path: Path to output directory on host
            command: Command to run in container
            environment: Environment variables
            timeout: Container timeout in seconds
            
        Returns:
            Running Docker container
            
        Raises:
            MetaClaudeDockerError: If container fails to start
        """
        logger.info(f"Starting container from {self.full_image_name}")
        
        # Ensure directories exist
        workspace_path.mkdir(parents=True, exist_ok=True)
        output_path.mkdir(parents=True, exist_ok=True)
        
        volumes = {
            str(workspace_path): {"bind": "/workspace", "mode": "rw"},
            str(output_path): {"bind": "/workspace/output", "mode": "rw"},
        }
        
        env_vars = environment or {}
        env_vars.update({
            "CLAUDE_CODE_WORKSPACE": "/workspace",
            "CLAUDE_CODE_OUTPUT": "/workspace/output",
        })
        
        try:
            container = self.client.containers.run(
                self.full_image_name,
                command=command or "tail -f /dev/null",
                volumes=volumes,
                environment=env_vars,
                detach=True,
                remove=False,  # Keep container for debugging if needed
                working_dir="/workspace",
                user="metaclaude",
                network_mode="bridge",
            )
            
            logger.info(f"Container {container.short_id} started successfully")
            return container
            
        except Exception as e:
            logger.error(f"Failed to start container: {e}")
            raise MetaClaudeDockerError(f"Container startup failed: {e}")
    
    def copy_to_container(self, container: Container, src_path: Path, dest_path: str) -> None:
        """Copy files/directories to container.
        
        Args:
            container: Target container
            src_path: Source path on host
            dest_path: Destination path in container
            
        Raises:
            MetaClaudeDockerError: If copy operation fails
        """
        try:
            import tarfile
            import io
            
            # Create tar archive in memory
            tar_stream = io.BytesIO()
            with tarfile.open(fileobj=tar_stream, mode="w") as tar:
                if src_path.is_file():
                    tar.add(src_path, arcname=src_path.name)
                else:
                    for item in src_path.rglob("*"):
                        if item.is_file():
                            arcname = item.relative_to(src_path.parent)
                            tar.add(item, arcname=str(arcname))
            
            tar_stream.seek(0)
            
            # Copy to container
            container.put_archive(dest_path, tar_stream.getvalue())
            logger.info(f"Copied {src_path} to container:{dest_path}")
            
        except Exception as e:
            logger.error(f"Failed to copy files to container: {e}")
            raise MetaClaudeDockerError(f"File copy failed: {e}")
    
    def execute_command(
        self,
        container: Container,
        command: str,
        workdir: str = "/workspace",
    ) -> tuple[int, str]:
        """Execute command in running container.
        
        Args:
            container: Target container
            command: Command to execute
            workdir: Working directory for command
            
        Returns:
            Tuple of (exit_code, output)
            
        Raises:
            MetaClaudeDockerError: If command execution fails
        """
        try:
            logger.info(f"Executing command in container: {command}")
            
            exec_result = container.exec_run(
                command,
                workdir=workdir,
                user="metaclaude",
                stdout=True,
                stderr=True,
            )
            
            output = exec_result.output.decode("utf-8") if exec_result.output else ""
            logger.info(f"Command completed with exit code: {exec_result.exit_code}")
            
            return exec_result.exit_code, output
            
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            raise MetaClaudeDockerError(f"Command execution failed: {e}")
    
    def monitor_logs(self, container: Container) -> Generator[str, None, None]:
        """Monitor container logs in real-time.
        
        Args:
            container: Container to monitor
            
        Yields:
            Log lines from container
        """
        try:
            for log_line in container.logs(stream=True, follow=True):
                yield log_line.decode("utf-8").strip()
        except Exception as e:
            logger.error(f"Log monitoring failed: {e}")
            raise MetaClaudeDockerError(f"Log monitoring failed: {e}")
    
    def stop_container(self, container: Container, timeout: int = 10) -> None:
        """Stop running container gracefully.
        
        Args:
            container: Container to stop
            timeout: Timeout for graceful stop
        """
        try:
            logger.info(f"Stopping container {container.short_id}")
            container.stop(timeout=timeout)
            logger.info("Container stopped successfully")
        except Exception as e:
            logger.warning(f"Failed to stop container gracefully: {e}")
            try:
                container.kill()
                logger.info("Container killed forcefully")
            except Exception as kill_error:
                logger.error(f"Failed to kill container: {kill_error}")
    
    def cleanup_container(self, container: Container, keep: bool = False) -> None:
        """Clean up container resources.
        
        Args:
            container: Container to clean up
            keep: Whether to keep container for debugging
        """
        try:
            if not keep:
                container.remove(force=True)
                logger.info(f"Container {container.short_id} removed")
            else:
                logger.info(f"Container {container.short_id} kept for debugging")
        except Exception as e:
            logger.warning(f"Container cleanup failed: {e}")
    
    def get_container_status(self, container: Container) -> str:
        """Get current container status.
        
        Args:
            container: Container to check
            
        Returns:
            Container status string
        """
        try:
            container.reload()
            return container.status
        except Exception as e:
            logger.error(f"Failed to get container status: {e}")
            return "unknown"