"""Pydantic models for MetaClaude configuration."""

from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from pydantic import BaseModel, Field, validator, root_validator


class DockerConfig(BaseModel):
    """Docker configuration model."""
    
    image_name: str = Field(default="metaclaude", description="Docker image name")
    image_tag: str = Field(default="latest", description="Docker image tag")
    build_context: Optional[Path] = Field(default=None, description="Docker build context path")
    dockerfile_path: Optional[Path] = Field(default=None, description="Path to Dockerfile")
    no_cache: bool = Field(default=False, description="Disable Docker build cache")
    
    @validator("build_context", "dockerfile_path", pre=True)
    def convert_path(cls, v):
        """Convert string paths to Path objects."""
        if v is not None and not isinstance(v, Path):
            return Path(v)
        return v


class AgentConfig(BaseModel):
    """Agent configuration model."""
    
    name: str = Field(..., description="Agent name")
    description: str = Field(..., description="Agent description")
    tools: List[str] = Field(..., description="Available tools")
    parallelism: int = Field(default=1, description="Parallelism level")
    patterns: List[str] = Field(default_factory=list, description="Agent patterns")
    enabled: bool = Field(default=True, description="Whether agent is enabled")
    
    @validator("parallelism")
    def validate_parallelism(cls, v):
        """Validate parallelism range."""
        if v < 1 or v > 10:
            raise ValueError("Parallelism must be between 1 and 10")
        return v


class TemplateConfig(BaseModel):
    """Template system configuration model."""
    
    templates_dir: Path = Field(..., description="Templates directory path")
    auto_reload: bool = Field(default=False, description="Auto-reload templates")
    strict_mode: bool = Field(default=True, description="Strict template validation")
    custom_variables: Dict[str, Any] = Field(default_factory=dict, description="Custom template variables")
    
    @validator("templates_dir", pre=True)
    def convert_templates_dir(cls, v):
        """Convert string path to Path object."""
        if not isinstance(v, Path):
            return Path(v)
        return v
    
    @validator("templates_dir")
    def validate_templates_dir(cls, v):
        """Validate templates directory exists."""
        if not v.exists():
            raise ValueError(f"Templates directory does not exist: {v}")
        return v


class ExecutionConfig(BaseModel):
    """Execution configuration model."""
    
    timeout: int = Field(default=14400, description="Execution timeout in seconds")  # 4 hours
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    keep_container: bool = Field(default=False, description="Keep container after execution")
    output_base_dir: Path = Field(default=Path.cwd(), description="Base output directory")
    
    @validator("timeout")
    def validate_timeout(cls, v):
        """Validate timeout range."""
        if v < 60 or v > 86400:  # 1 minute to 24 hours
            raise ValueError("Timeout must be between 60 and 86400 seconds")
        return v
    
    @validator("max_retries")
    def validate_retries(cls, v):
        """Validate retry count."""
        if v < 0 or v > 10:
            raise ValueError("Max retries must be between 0 and 10")
        return v
    
    @validator("output_base_dir", pre=True)
    def convert_output_dir(cls, v):
        """Convert string path to Path object."""
        if not isinstance(v, Path):
            return Path(v)
        return v


class LoggingConfig(BaseModel):
    """Logging configuration model."""
    
    level: str = Field(default="INFO", description="Logging level")
    log_file: Optional[Path] = Field(default=None, description="Log file path")
    console_output: bool = Field(default=True, description="Enable console output")
    structured_logging: bool = Field(default=False, description="Use structured logging")
    max_file_size: int = Field(default=10485760, description="Max log file size in bytes")  # 10MB
    backup_count: int = Field(default=5, description="Number of backup log files")
    
    @validator("level")
    def validate_level(cls, v):
        """Validate logging level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Invalid logging level. Must be one of: {valid_levels}")
        return v.upper()
    
    @validator("log_file", pre=True)
    def convert_log_file(cls, v):
        """Convert string path to Path object."""
        if v is not None and not isinstance(v, Path):
            return Path(v)
        return v


class ClaudeConfig(BaseModel):
    """Claude-specific configuration model."""
    
    model: str = Field(default="opus", description="Claude model to use")
    max_thinking_tokens: int = Field(default=32000, description="Maximum thinking tokens")
    auto_compact: bool = Field(default=False, description="Enable auto-compact")
    temperature: Optional[float] = Field(default=None, description="Model temperature")
    
    @validator("model")
    def validate_model(cls, v):
        """Validate Claude model name."""
        valid_models = [
            "opus", "sonnet", "haiku",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229", 
            "claude-3-haiku-20240307"
        ]
        if v not in valid_models:
            raise ValueError(f"Invalid model. Must be one of: {valid_models}")
        return v
    
    @validator("max_thinking_tokens")
    def validate_thinking_tokens(cls, v):
        """Validate thinking tokens range."""
        if v < 1000 or v > 100000:
            raise ValueError("Max thinking tokens must be between 1000 and 100000")
        return v
    
    @validator("temperature")
    def validate_temperature(cls, v):
        """Validate temperature range."""
        if v is not None and (v < 0.0 or v > 1.0):
            raise ValueError("Temperature must be between 0.0 and 1.0")
        return v


class MCPConfig(BaseModel):
    """MCP (Model Context Protocol) configuration model."""
    
    enabled: bool = Field(default=True, description="Enable MCP integration")
    servers: Dict[str, Dict[str, Any]] = Field(default_factory=dict, description="MCP server configurations")
    timeout: int = Field(default=30, description="MCP operation timeout")
    
    @validator("timeout")
    def validate_timeout(cls, v):
        """Validate MCP timeout."""
        if v < 5 or v > 300:
            raise ValueError("MCP timeout must be between 5 and 300 seconds")
        return v


class MetaClaudeConfig(BaseModel):
    """Main MetaClaude configuration model."""
    
    # Core configuration sections
    docker: DockerConfig = Field(default_factory=DockerConfig)
    templates: TemplateConfig = Field(..., description="Template configuration")
    execution: ExecutionConfig = Field(default_factory=ExecutionConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    claude: ClaudeConfig = Field(default_factory=ClaudeConfig)
    mcp: MCPConfig = Field(default_factory=MCPConfig)
    
    # Agent configurations
    agents: Dict[str, AgentConfig] = Field(default_factory=dict, description="Agent configurations")
    
    # Global settings
    version: str = Field(default="0.1.0", description="MetaClaude version")
    debug: bool = Field(default=False, description="Enable debug mode")
    
    class Config:
        """Pydantic configuration."""
        validate_assignment = True
        use_enum_values = True
        arbitrary_types_allowed = True
    
    @root_validator
    def validate_config_consistency(cls, values):
        """Validate configuration consistency."""
        # Ensure Docker build context exists if specified
        docker_config = values.get("docker")
        if docker_config and docker_config.build_context:
            if not docker_config.build_context.exists():
                raise ValueError(f"Docker build context does not exist: {docker_config.build_context}")
        
        # Ensure output directory is writable
        execution_config = values.get("execution")
        if execution_config:
            try:
                execution_config.output_base_dir.mkdir(parents=True, exist_ok=True)
            except (OSError, PermissionError) as e:
                raise ValueError(f"Cannot create output directory: {e}")
        
        return values
    
    def get_full_docker_image_name(self) -> str:
        """Get full Docker image name with tag."""
        return f"{self.docker.image_name}:{self.docker.image_tag}"
    
    def get_timeout_seconds(self) -> int:
        """Get execution timeout in seconds."""
        return self.execution.timeout
    
    def is_debug_enabled(self) -> bool:
        """Check if debug mode is enabled."""
        return self.debug or self.logging.level == "DEBUG"
    
    def get_agent_names(self) -> List[str]:
        """Get list of configured agent names."""
        return list(self.agents.keys())
    
    def get_enabled_agents(self) -> Dict[str, AgentConfig]:
        """Get enabled agents only."""
        return {name: config for name, config in self.agents.items() if config.enabled}


class ConfigDefaults:
    """Default configuration values."""
    
    @staticmethod
    def get_default_config() -> Dict[str, Any]:
        """Get default configuration dictionary."""
        return {
            "docker": {
                "image_name": "metaclaude",
                "image_tag": "latest",
                "no_cache": False,
            },
            "execution": {
                "timeout": 14400,  # 4 hours
                "max_retries": 3,
                "keep_container": False,
            },
            "logging": {
                "level": "INFO",
                "console_output": True,
                "structured_logging": False,
            },
            "claude": {
                "model": "opus",
                "max_thinking_tokens": 32000,
                "auto_compact": False,
            },
            "mcp": {
                "enabled": True,
                "timeout": 30,
                "servers": {},
            },
            "debug": False,
        }
    
    @staticmethod
    def get_development_config() -> Dict[str, Any]:
        """Get development-specific configuration."""
        config = ConfigDefaults.get_default_config()
        config.update({
            "debug": True,
            "logging": {
                "level": "DEBUG",
                "console_output": True,
                "structured_logging": True,
            },
            "execution": {
                "timeout": 1800,  # 30 minutes for development
                "keep_container": True,
            },
            "docker": {
                "no_cache": True,
            },
        })
        return config