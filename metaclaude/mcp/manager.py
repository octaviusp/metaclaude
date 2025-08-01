"""MCP (Model Context Protocol) integration manager for MetaClaude."""

import json
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
from pydantic import BaseModel

from ..utils.logging import get_logger
from ..utils.errors import MetaClaudeError

logger = get_logger(__name__)


class MCPServerConfig(BaseModel):
    """MCP server configuration model."""
    
    name: str
    command: str
    args: List[str] = []
    env: Dict[str, str] = {}
    enabled: bool = True
    timeout: int = 30


class MCPManager:
    """Manages MCP server configurations and capabilities."""
    
    def __init__(self):
        """Initialize MCP manager."""
        self.available_servers: Dict[str, MCPServerConfig] = {}
        self.detected_servers: Set[str] = set()
        
        logger.info("MCPManager initialized")
    
    def detect_available_servers(self) -> Dict[str, bool]:
        """Detect which MCP servers are available on the system.
        
        Returns:
            Dictionary mapping server names to availability status
        """
        logger.info("Detecting available MCP servers")
        
        # Known MCP servers and their detection methods
        server_checks = {
            "github": self._check_github_server,
            "memory": self._check_memory_server,
            "puppeteer": self._check_puppeteer_server,
            "filesystem": self._check_filesystem_server,
            "brave-search": self._check_brave_search_server,
            "postgres": self._check_postgres_server,
        }
        
        availability = {}
        
        for server_name, check_func in server_checks.items():
            try:
                is_available = check_func()
                availability[server_name] = is_available
                
                if is_available:
                    self.detected_servers.add(server_name)
                    logger.debug(f"MCP server {server_name} is available")
                else:
                    logger.debug(f"MCP server {server_name} is not available")
                    
            except Exception as e:
                logger.warning(f"Failed to check MCP server {server_name}: {e}")
                availability[server_name] = False
        
        logger.info(f"Detected {len(self.detected_servers)} available MCP servers")
        return availability
    
    def _check_github_server(self) -> bool:
        """Check if GitHub MCP server is available."""
        try:
            result = subprocess.run(
                ["npx", "@modelcontextprotocol/server-github", "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def _check_memory_server(self) -> bool:
        """Check if Memory MCP server is available."""
        try:
            result = subprocess.run(
                ["npx", "@modelcontextprotocol/server-memory", "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def _check_puppeteer_server(self) -> bool:
        """Check if Puppeteer MCP server is available."""
        try:
            result = subprocess.run(
                ["npx", "@modelcontextprotocol/server-puppeteer", "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def _check_filesystem_server(self) -> bool:
        """Check if Filesystem MCP server is available."""
        try:
            result = subprocess.run(
                ["npx", "@modelcontextprotocol/server-filesystem", "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def _check_brave_search_server(self) -> bool:
        """Check if Brave Search MCP server is available."""
        try:
            result = subprocess.run(
                ["npx", "@modelcontextprotocol/server-brave-search", "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def _check_postgres_server(self) -> bool:
        """Check if Postgres MCP server is available."""
        try:
            result = subprocess.run(
                ["npx", "@modelcontextprotocol/server-postgres", "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def configure_servers(
        self,
        selected_servers: Optional[List[str]] = None,
        env_vars: Optional[Dict[str, str]] = None,
    ) -> Dict[str, MCPServerConfig]:
        """Configure MCP servers based on availability and selection.
        
        Args:
            selected_servers: Specific servers to configure (None for auto)
            env_vars: Environment variables for server configuration
            
        Returns:
            Dictionary of configured server configurations
        """
        logger.info("Configuring MCP servers")
        
        env_vars = env_vars or {}
        
        # Auto-select servers if none specified
        if selected_servers is None:
            selected_servers = list(self.detected_servers)
        
        configured_servers = {}
        
        for server_name in selected_servers:
            if server_name not in self.detected_servers:
                logger.warning(f"Server {server_name} not available, skipping")
                continue
            
            config = self._create_server_config(server_name, env_vars)
            if config:
                configured_servers[server_name] = config
                logger.debug(f"Configured MCP server: {server_name}")
        
        self.available_servers = configured_servers
        logger.info(f"Configured {len(configured_servers)} MCP servers")
        
        return configured_servers
    
    def _create_server_config(self, server_name: str, env_vars: Dict[str, str]) -> Optional[MCPServerConfig]:
        """Create configuration for specific MCP server.
        
        Args:
            server_name: Name of the server
            env_vars: Environment variables
            
        Returns:
            Server configuration or None if failed
        """
        try:
            if server_name == "github":
                return MCPServerConfig(
                    name="github",
                    command="npx",
                    args=["@modelcontextprotocol/server-github"],
                    env={
                        "GITHUB_PERSONAL_ACCESS_TOKEN": env_vars.get("GITHUB_TOKEN", "")
                    },
                )
            
            elif server_name == "memory":
                return MCPServerConfig(
                    name="memory",
                    command="npx",
                    args=["@modelcontextprotocol/server-memory"],
                )
            
            elif server_name == "puppeteer":
                return MCPServerConfig(
                    name="puppeteer",
                    command="npx",
                    args=["@modelcontextprotocol/server-puppeteer"],
                )
            
            elif server_name == "filesystem":
                return MCPServerConfig(
                    name="filesystem",
                    command="npx",
                    args=["@modelcontextprotocol/server-filesystem"],
                )
            
            elif server_name == "brave-search":
                return MCPServerConfig(
                    name="brave-search",
                    command="npx",
                    args=["@modelcontextprotocol/server-brave-search"],
                    env={
                        "BRAVE_API_KEY": env_vars.get("BRAVE_API_KEY", "")
                    },
                )
            
            elif server_name == "postgres":
                return MCPServerConfig(
                    name="postgres",
                    command="npx",
                    args=["@modelcontextprotocol/server-postgres"],
                    env={
                        "POSTGRES_CONNECTION_STRING": env_vars.get("POSTGRES_CONNECTION_STRING", "")
                    },
                )
            
            else:
                logger.warning(f"Unknown MCP server: {server_name}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to create config for {server_name}: {e}")
            return None
    
    def validate_credentials(self, server_configs: Optional[Dict[str, MCPServerConfig]] = None) -> Dict[str, bool]:
        """Validate credentials for configured servers.
        
        Args:
            server_configs: Server configurations to validate
            
        Returns:
            Dictionary mapping server names to credential validity
        """
        configs = server_configs or self.available_servers
        validation_results = {}
        
        for server_name, config in configs.items():
            try:
                is_valid = self._validate_server_credentials(config)
                validation_results[server_name] = is_valid
                
                if is_valid:
                    logger.debug(f"Credentials valid for {server_name}")
                else:
                    logger.warning(f"Invalid credentials for {server_name}")
                    
            except Exception as e:
                logger.error(f"Credential validation failed for {server_name}: {e}")
                validation_results[server_name] = False
        
        return validation_results
    
    def _validate_server_credentials(self, config: MCPServerConfig) -> bool:
        """Validate credentials for a specific server.
        
        Args:
            config: Server configuration
            
        Returns:
            True if credentials are valid
        """
        # For now, just check if required environment variables are present
        if config.name == "github":
            return bool(config.env.get("GITHUB_PERSONAL_ACCESS_TOKEN"))
        
        elif config.name == "brave-search":
            return bool(config.env.get("BRAVE_API_KEY"))
        
        elif config.name == "postgres":
            return bool(config.env.get("POSTGRES_CONNECTION_STRING"))
        
        # Servers without credentials always pass
        return True
    
    def generate_mcp_config(
        self,
        output_path: Path,
        server_configs: Optional[Dict[str, MCPServerConfig]] = None,
    ) -> None:
        """Generate MCP configuration file for Claude Code.
        
        Args:
            output_path: Path to output MCP configuration file
            server_configs: Server configurations to include
        """
        configs = server_configs or self.available_servers
        
        if not configs:
            logger.warning("No MCP servers configured, skipping config generation")
            return
        
        logger.info(f"Generating MCP configuration for {len(configs)} servers")
        
        mcp_config = {
            "mcpServers": {}
        }
        
        for server_name, config in configs.items():
            if not config.enabled:
                continue
            
            server_config = {
                "command": config.command,
                "args": config.args,
            }
            
            if config.env:
                server_config["env"] = config.env
            
            mcp_config["mcpServers"][server_name] = server_config
        
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(mcp_config, f, indent=2)
            
            logger.info(f"MCP configuration written to {output_path}")
            
        except Exception as e:
            logger.error(f"Failed to write MCP configuration: {e}")
            raise MetaClaudeError(f"MCP configuration generation failed: {e}")
    
    def get_server_capabilities(self, server_name: str) -> Dict[str, Any]:
        """Get capabilities for a specific MCP server.
        
        Args:
            server_name: Name of the server
            
        Returns:
            Dictionary describing server capabilities
        """
        capabilities = {
            "github": {
                "description": "GitHub repository management and operations",
                "tools": ["repository operations", "issue management", "PR operations"],
                "requires_auth": True,
                "auth_env_var": "GITHUB_PERSONAL_ACCESS_TOKEN",
            },
            "memory": {
                "description": "Persistent memory and knowledge storage",
                "tools": ["knowledge storage", "memory retrieval", "context persistence"],
                "requires_auth": False,
            },
            "puppeteer": {
                "description": "Web scraping and browser automation",
                "tools": ["web scraping", "screenshot capture", "form automation"],
                "requires_auth": False,
            },
            "filesystem": {
                "description": "Local filesystem operations",
                "tools": ["file operations", "directory management", "file search"],
                "requires_auth": False,
            },
            "brave-search": {
                "description": "Web search capabilities via Brave Search API",
                "tools": ["web search", "search results", "web content"],
                "requires_auth": True,
                "auth_env_var": "BRAVE_API_KEY",
            },
            "postgres": {
                "description": "PostgreSQL database operations",
                "tools": ["SQL queries", "database schema", "data operations"],
                "requires_auth": True,
                "auth_env_var": "POSTGRES_CONNECTION_STRING",
            },
        }
        
        return capabilities.get(server_name, {"description": "Unknown server"})
    
    def list_available_servers(self) -> Dict[str, Dict[str, Any]]:
        """List all available MCP servers with their capabilities.
        
        Returns:
            Dictionary mapping server names to their capabilities
        """
        server_list = {}
        
        for server_name in self.detected_servers:
            capabilities = self.get_server_capabilities(server_name)
            capabilities["available"] = True
            server_list[server_name] = capabilities
        
        return server_list
    
    def install_server(self, server_name: str) -> bool:
        """Install an MCP server via npm.
        
        Args:
            server_name: Name of the server to install
            
        Returns:
            True if installation succeeded
        """
        package_name = f"@modelcontextprotocol/server-{server_name}"
        
        try:
            logger.info(f"Installing MCP server: {server_name}")
            
            result = subprocess.run(
                ["npm", "install", "-g", package_name],
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutes
            )
            
            if result.returncode == 0:
                logger.info(f"Successfully installed {server_name}")
                self.detected_servers.add(server_name)
                return True
            else:
                logger.error(f"Failed to install {server_name}: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Installation failed for {server_name}: {e}")
            return False