"""Configuration manager for MetaClaude."""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, Union, List
from pydantic import ValidationError

from .models import MetaClaudeConfig, ConfigDefaults
from ..utils.errors import MetaClaudeConfigError
from ..utils.logging import get_logger

logger = get_logger(__name__)


class ConfigManager:
    """Manages MetaClaude configuration from multiple sources."""
    
    def __init__(self, config_file: Optional[Path] = None):
        """Initialize configuration manager.
        
        Args:
            config_file: Optional path to configuration file
        """
        self.config_file = config_file
        self.config: Optional[MetaClaudeConfig] = None
        self._config_sources = []
        
        logger.info("ConfigManager initialized")
    
    def load_config(
        self,
        config_file: Optional[Path] = None,
        cli_overrides: Optional[Dict[str, Any]] = None,
        validate: bool = True,
    ) -> MetaClaudeConfig:
        """Load configuration from multiple sources.
        
        Sources (in order of precedence):
        1. CLI arguments/overrides
        2. Configuration file
        3. Environment variables
        4. Default values
        
        Args:
            config_file: Optional configuration file path
            cli_overrides: CLI argument overrides
            validate: Whether to validate configuration
            
        Returns:
            Loaded MetaClaude configuration
            
        Raises:
            MetaClaudeConfigError: If configuration loading fails
        """
        try:
            logger.info("Loading MetaClaude configuration")
            
            # Start with defaults
            config_dict = ConfigDefaults.get_default_config()
            self._config_sources.append("defaults")
            
            # Load from environment variables
            env_config = self._load_from_environment()
            if env_config:
                config_dict = self._deep_merge(config_dict, env_config)
                self._config_sources.append("environment")
            
            # Load from configuration file
            file_config = self._load_from_file(config_file or self.config_file)
            if file_config:
                config_dict = self._deep_merge(config_dict, file_config)
                self._config_sources.append(f"file:{config_file or self.config_file}")
            
            # Apply CLI overrides
            if cli_overrides:
                config_dict = self._deep_merge(config_dict, cli_overrides)
                self._config_sources.append("cli")
            
            # Add templates directory if not specified
            if "templates" not in config_dict:
                templates_dir = Path(__file__).parent.parent.parent / "templates"
                config_dict["templates"] = {"templates_dir": templates_dir}
            
            # Create and validate configuration
            if validate:
                self.config = MetaClaudeConfig(**config_dict)
            else:
                # Skip validation for partial configs
                self.config = MetaClaudeConfig.parse_obj(config_dict)
            
            logger.info(f"Configuration loaded from sources: {', '.join(self._config_sources)}")
            return self.config
            
        except ValidationError as e:
            logger.error(f"Configuration validation failed: {e}")
            raise MetaClaudeConfigError(f"Invalid configuration: {e}")
        except Exception as e:
            logger.error(f"Configuration loading failed: {e}")
            raise MetaClaudeConfigError(f"Failed to load configuration: {e}")
    
    def _load_from_file(self, config_file: Optional[Path]) -> Optional[Dict[str, Any]]:
        """Load configuration from file.
        
        Args:
            config_file: Configuration file path
            
        Returns:
            Configuration dictionary or None
        """
        if not config_file or not config_file.exists():
            return None
        
        try:
            logger.debug(f"Loading configuration from file: {config_file}")
            
            content = config_file.read_text(encoding="utf-8")
            
            if config_file.suffix.lower() in [".yaml", ".yml"]:
                config_dict = yaml.safe_load(content)
            elif config_file.suffix.lower() == ".json":
                config_dict = json.loads(content)
            else:
                # Try to detect format from content
                try:
                    config_dict = yaml.safe_load(content)
                except yaml.YAMLError:
                    config_dict = json.loads(content)
            
            logger.debug(f"Loaded configuration from file: {len(config_dict)} keys")
            return config_dict
            
        except Exception as e:
            logger.warning(f"Failed to load configuration file {config_file}: {e}")
            return None
    
    def _load_from_environment(self) -> Dict[str, Any]:
        """Load configuration from environment variables.
        
        Environment variables use METACLAUDE_ prefix and dot notation:
        METACLAUDE_DOCKER_IMAGE_NAME -> docker.image_name
        METACLAUDE_CLAUDE_MODEL -> claude.model
        
        Returns:
            Configuration dictionary from environment
        """
        config_dict = {}
        
        for key, value in os.environ.items():
            if not key.startswith("METACLAUDE_"):
                continue
            
            # Convert METACLAUDE_DOCKER_IMAGE_NAME to docker.image_name
            config_key = key[11:].lower().replace("_", ".")
            
            # Parse value
            parsed_value = self._parse_env_value(value)
            
            # Set nested value
            self._set_nested_value(config_dict, config_key, parsed_value)
        
        if config_dict:
            logger.debug(f"Loaded configuration from environment: {len(config_dict)} keys")
        
        return config_dict
    
    def _parse_env_value(self, value: str) -> Any:
        """Parse environment variable value to appropriate type.
        
        Args:
            value: Environment variable value
            
        Returns:
            Parsed value
        """
        # Boolean values
        if value.lower() in ("true", "false"):
            return value.lower() == "true"
        
        # Integer values
        if value.isdigit():
            return int(value)
        
        # Float values
        try:
            return float(value)
        except ValueError:
            pass
        
        # JSON values (for complex types)
        if value.startswith(("[", "{")):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                pass
        
        # String value
        return value
    
    def _set_nested_value(self, config_dict: Dict[str, Any], key: str, value: Any) -> None:
        """Set nested dictionary value using dot notation.
        
        Args:
            config_dict: Target dictionary
            key: Dot-notation key (e.g., 'docker.image_name')
            value: Value to set
        """
        keys = key.split(".")
        current = config_dict
        
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        current[keys[-1]] = value
    
    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries.
        
        Args:
            base: Base dictionary
            override: Override dictionary
            
        Returns:
            Merged dictionary
        """
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def save_config(self, config_file: Path, format_type: str = "yaml") -> None:
        """Save current configuration to file.
        
        Args:
            config_file: Target configuration file
            format_type: File format ('yaml' or 'json')
            
        Raises:
            MetaClaudeConfigError: If saving fails
        """
        if not self.config:
            raise MetaClaudeConfigError("No configuration loaded to save")
        
        try:
            logger.info(f"Saving configuration to {config_file}")
            
            # Convert to dictionary
            config_dict = self.config.dict()
            
            # Create directory if needed
            config_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            if format_type.lower() == "json":
                with open(config_file, "w", encoding="utf-8") as f:
                    json.dump(config_dict, f, indent=2, default=str)
            else:  # yaml
                with open(config_file, "w", encoding="utf-8") as f:
                    yaml.dump(config_dict, f, default_flow_style=False, default=str)
            
            logger.info(f"Configuration saved to {config_file}")
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            raise MetaClaudeConfigError(f"Failed to save configuration: {e}")
    
    def get_config(self) -> MetaClaudeConfig:
        """Get current configuration.
        
        Returns:
            Current MetaClaude configuration
            
        Raises:
            MetaClaudeConfigError: If no configuration is loaded
        """
        if not self.config:
            raise MetaClaudeConfigError("No configuration loaded. Call load_config() first.")
        return self.config
    
    def validate_config(self, config_dict: Optional[Dict[str, Any]] = None) -> List[str]:
        """Validate configuration dictionary.
        
        Args:
            config_dict: Configuration to validate (or current if None)
            
        Returns:
            List of validation errors (empty if valid)
        """
        if config_dict is None:
            if not self.config:
                return ["No configuration loaded"]
            config_dict = self.config.dict()
        
        errors = []
        
        try:
            # Attempt to create MetaClaudeConfig instance
            MetaClaudeConfig(**config_dict)
        except ValidationError as e:
            for error in e.errors():
                field = ".".join(str(x) for x in error["loc"])
                message = error["msg"]
                errors.append(f"{field}: {message}")
        except Exception as e:
            errors.append(f"Validation error: {e}")
        
        return errors
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get configuration summary for display.
        
        Returns:
            Configuration summary dictionary
        """
        if not self.config:
            return {"status": "No configuration loaded"}
        
        return {
            "status": "Loaded",
            "sources": self._config_sources,
            "docker_image": self.config.get_full_docker_image_name(),
            "claude_model": self.config.claude.model,
            "timeout": f"{self.config.execution.timeout}s",
            "log_level": self.config.logging.level,
            "debug_mode": self.config.is_debug_enabled(),
            "agents_count": len(self.config.agents),
            "enabled_agents": len(self.config.get_enabled_agents()),
            "templates_dir": str(self.config.templates.templates_dir),
            "output_dir": str(self.config.execution.output_base_dir),
        }
    
    def create_cli_overrides(
        self,
        model: Optional[str] = None,
        timeout: Optional[int] = None,
        keep_container: Optional[bool] = None,
        no_cache: Optional[bool] = None,
        verbose: Optional[bool] = None,
        output_dir: Optional[Path] = None,
        log_file: Optional[Path] = None,
    ) -> Dict[str, Any]:
        """Create CLI overrides dictionary.
        
        Args:
            model: Claude model override
            timeout: Timeout override
            keep_container: Keep container flag
            no_cache: No cache flag
            verbose: Verbose flag
            output_dir: Output directory override
            log_file: Log file override
            
        Returns:
            CLI overrides dictionary
        """
        overrides = {}
        
        if model is not None:
            overrides["claude"] = {"model": model}
        
        if timeout is not None:
            overrides["execution"] = overrides.get("execution", {})
            overrides["execution"]["timeout"] = timeout
        
        if keep_container is not None:
            overrides["execution"] = overrides.get("execution", {})
            overrides["execution"]["keep_container"] = keep_container
        
        if no_cache is not None:
            overrides["docker"] = {"no_cache": no_cache}
        
        if verbose is not None:
            overrides["logging"] = overrides.get("logging", {})
            overrides["logging"]["level"] = "DEBUG" if verbose else "INFO"
        
        if output_dir is not None:
            overrides["execution"] = overrides.get("execution", {})
            overrides["execution"]["output_base_dir"] = output_dir
        
        if log_file is not None:
            overrides["logging"] = overrides.get("logging", {})
            overrides["logging"]["log_file"] = log_file
        
        return overrides
    
    @staticmethod
    def find_config_file(start_dir: Optional[Path] = None) -> Optional[Path]:
        """Find MetaClaude configuration file in directory hierarchy.
        
        Searches for:
        - metaclaude.yaml
        - metaclaude.yml
        - metaclaude.json
        - .metaclaude.yaml
        - .metaclaude.yml
        - .metaclaude.json
        
        Args:
            start_dir: Starting directory (defaults to current)
            
        Returns:
            Path to configuration file or None
        """
        start_dir = start_dir or Path.cwd()
        
        config_names = [
            "metaclaude.yaml", "metaclaude.yml", "metaclaude.json",
            ".metaclaude.yaml", ".metaclaude.yml", ".metaclaude.json"
        ]
        
        # Search up the directory tree
        current_dir = start_dir.resolve()
        
        while True:
            for config_name in config_names:
                config_file = current_dir / config_name
                if config_file.exists():
                    return config_file
            
            # Move to parent directory
            parent = current_dir.parent
            if parent == current_dir:  # Reached root
                break
            current_dir = parent
        
        return None