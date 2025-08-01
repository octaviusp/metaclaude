"""File system utilities for MetaClaude."""

import shutil
import tempfile
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

from .logging import get_logger
from .errors import MetaClaudeError

logger = get_logger(__name__)


def create_workspace(base_dir: Path, project_name: str, timestamp: Optional[str] = None) -> Path:
    """Create workspace directory with timestamp.
    
    Args:
        base_dir: Base directory for workspace
        project_name: Project name for workspace
        timestamp: Optional timestamp (auto-generated if None)
        
    Returns:
        Path to created workspace
        
    Raises:
        MetaClaudeError: If workspace creation fails
    """
    try:
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Sanitize project name
        safe_name = sanitize_filename(project_name)
        workspace_name = f"{timestamp}_{safe_name}"
        
        workspace_path = base_dir / "metaclaude_output" / workspace_name
        workspace_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Created workspace: {workspace_path}")
        return workspace_path
        
    except Exception as e:
        logger.error(f"Failed to create workspace: {e}")
        raise MetaClaudeError(f"Workspace creation failed: {e}")


def sanitize_filename(filename: str, max_length: int = 50) -> str:
    """Sanitize filename for safe file system usage.
    
    Args:
        filename: Original filename
        max_length: Maximum filename length
        
    Returns:
        Sanitized filename
    """
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    sanitized = "".join(c if c not in invalid_chars else "_" for c in filename)
    
    # Remove multiple underscores
    while "__" in sanitized:
        sanitized = sanitized.replace("__", "_")
    
    # Strip and limit length
    sanitized = sanitized.strip("_")[:max_length]
    
    # Ensure non-empty result
    if not sanitized:
        sanitized = "unnamed"
    
    return sanitized


def copy_directory_tree(src_dir: Path, dest_dir: Path, exclude_patterns: Optional[List[str]] = None) -> None:
    """Copy directory tree with optional exclusions.
    
    Args:
        src_dir: Source directory
        dest_dir: Destination directory
        exclude_patterns: List of glob patterns to exclude
        
    Raises:
        MetaClaudeError: If copy operation fails
    """
    try:
        dest_dir.mkdir(parents=True, exist_ok=True)
        
        exclude_patterns = exclude_patterns or []
        
        for item in src_dir.rglob("*"):
            if item.is_file():
                # Check exclusions
                relative_path = item.relative_to(src_dir)
                if _should_exclude(relative_path, exclude_patterns):
                    continue
                
                dest_file = dest_dir / relative_path
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, dest_file)
        
        logger.debug(f"Copied directory tree from {src_dir} to {dest_dir}")
        
    except Exception as e:
        logger.error(f"Failed to copy directory tree: {e}")
        raise MetaClaudeError(f"Directory copy failed: {e}")


def _should_exclude(file_path: Path, exclude_patterns: List[str]) -> bool:
    """Check if file should be excluded based on patterns.
    
    Args:
        file_path: File path to check
        exclude_patterns: List of glob patterns
        
    Returns:
        True if file should be excluded
    """
    import fnmatch
    
    file_str = str(file_path)
    
    for pattern in exclude_patterns:
        if fnmatch.fnmatch(file_str, pattern):
            return True
    
    return False


def ensure_directory_writable(directory: Path) -> bool:
    """Ensure directory exists and is writable.
    
    Args:
        directory: Directory to check
        
    Returns:
        True if directory is writable
    """
    try:
        directory.mkdir(parents=True, exist_ok=True)
        
        # Test write access
        test_file = directory / ".metaclaude_write_test"
        test_file.write_text("test")
        test_file.unlink()
        
        return True
        
    except Exception as e:
        logger.warning(f"Directory not writable {directory}: {e}")
        return False


def get_directory_size(directory: Path) -> int:
    """Get total size of directory in bytes.
    
    Args:
        directory: Directory to measure
        
    Returns:
        Directory size in bytes
    """
    total_size = 0
    
    try:
        for item in directory.rglob("*"):
            if item.is_file():
                total_size += item.stat().st_size
    except Exception as e:
        logger.warning(f"Failed to calculate directory size: {e}")
    
    return total_size


def cleanup_old_workspaces(base_dir: Path, max_age_days: int = 7, max_count: int = 10) -> int:
    """Clean up old workspace directories.
    
    Args:
        base_dir: Base directory containing workspaces
        max_age_days: Maximum age in days
        max_count: Maximum number of workspaces to keep
        
    Returns:
        Number of workspaces cleaned up
    """
    try:
        vcc_output_dir = base_dir / "metaclaude_output"
        if not vcc_output_dir.exists():
            return 0
        
        # Get all workspace directories
        workspaces = []
        for item in vcc_output_dir.iterdir():
            if item.is_dir():
                try:
                    # Extract timestamp from directory name
                    timestamp_str = item.name.split("_")[0]
                    timestamp = datetime.strptime(timestamp_str, "%Y%m%d")
                    workspaces.append((item, timestamp))
                except (ValueError, IndexError):
                    # Skip directories that don't match expected format
                    continue
        
        # Sort by timestamp (newest first)
        workspaces.sort(key=lambda x: x[1], reverse=True)
        
        cleaned_count = 0
        now = datetime.now()
        
        for i, (workspace_dir, timestamp) in enumerate(workspaces):
            # Keep recent workspaces within max_count
            if i < max_count:
                continue
            
            # Check age
            age_days = (now - timestamp).days
            
            if age_days > max_age_days or i >= max_count:
                try:
                    shutil.rmtree(workspace_dir)
                    cleaned_count += 1
                    logger.debug(f"Cleaned up old workspace: {workspace_dir}")
                except Exception as e:
                    logger.warning(f"Failed to clean up workspace {workspace_dir}: {e}")
        
        if cleaned_count > 0:
            logger.info(f"Cleaned up {cleaned_count} old workspaces")
        
        return cleaned_count
        
    except Exception as e:
        logger.error(f"Workspace cleanup failed: {e}")
        return 0


def create_temp_directory(prefix: str = "metaclaude_") -> Path:
    """Create temporary directory.
    
    Args:
        prefix: Directory name prefix
        
    Returns:
        Path to temporary directory
    """
    temp_dir = Path(tempfile.mkdtemp(prefix=prefix))
    logger.debug(f"Created temporary directory: {temp_dir}")
    return temp_dir


def validate_path_safety(path: Path, base_path: Path) -> bool:
    """Validate that path is safe (within base_path).
    
    Args:
        path: Path to validate
        base_path: Base path that should contain the path
        
    Returns:
        True if path is safe
    """
    try:
        # Resolve both paths to handle symlinks and relative paths
        resolved_path = path.resolve()
        resolved_base = base_path.resolve()
        
        # Check if path is within base_path
        return str(resolved_path).startswith(str(resolved_base))
        
    except Exception:
        return False


def find_files_by_pattern(directory: Path, pattern: str, recursive: bool = True) -> List[Path]:
    """Find files matching a glob pattern.
    
    Args:
        directory: Directory to search
        pattern: Glob pattern
        recursive: Whether to search recursively
        
    Returns:
        List of matching file paths
    """
    try:
        if recursive:
            return list(directory.rglob(pattern))
        else:
            return list(directory.glob(pattern))
    except Exception as e:
        logger.warning(f"File search failed: {e}")
        return []


def get_file_info(file_path: Path) -> Dict[str, Any]:
    """Get file information.
    
    Args:
        file_path: Path to file
        
    Returns:
        Dictionary with file information
    """
    try:
        stat = file_path.stat()
        
        return {
            "size": stat.st_size,
            "modified_time": datetime.fromtimestamp(stat.st_mtime),
            "created_time": datetime.fromtimestamp(stat.st_ctime),
            "is_file": file_path.is_file(),
            "is_directory": file_path.is_dir(),
            "is_symlink": file_path.is_symlink(),
            "permissions": oct(stat.st_mode)[-3:],
        }
        
    except Exception as e:
        logger.warning(f"Failed to get file info for {file_path}: {e}")
        return {"error": str(e)}


def safe_remove_directory(directory: Path, max_attempts: int = 3) -> bool:
    """Safely remove directory with retries.
    
    Args:
        directory: Directory to remove
        max_attempts: Maximum removal attempts
        
    Returns:
        True if successfully removed
    """
    import time
    
    for attempt in range(max_attempts):
        try:
            if directory.exists():
                shutil.rmtree(directory)
                logger.debug(f"Removed directory: {directory}")
            return True
            
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} to remove {directory} failed: {e}")
            if attempt < max_attempts - 1:
                time.sleep(1)  # Wait before retry
    
    return False