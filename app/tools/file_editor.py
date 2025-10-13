"""File editing and manipulation tool."""
import os
import aiofiles
from pathlib import Path
from typing import Dict, Any, Optional
from .base import BaseTool, ToolResult, ToolFailure


class FileEditorTool(BaseTool):
    """Tool for file operations including read, write, edit, and create."""
    
    name: str = "file_editor"
    description: str = "Create, read, write, and edit files"
    parameters: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["read", "write", "create", "append", "delete", "list"],
                "description": "The file operation to perform"
            },
            "path": {
                "type": "string",
                "description": "File or directory path"
            },
            "content": {
                "type": "string",
                "description": "Content to write (for write/create/append actions)"
            },
            "encoding": {
                "type": "string",
                "description": "File encoding (default: utf-8)",
                "default": "utf-8"
            }
        },
        "required": ["action", "path"]
    }
    
    async def execute(self, action: str, path: str, content: str = "", encoding: str = "utf-8", **kwargs) -> ToolResult:
        """Execute file operation."""
        try:
            file_path = Path(path)
            
            # Security check - prevent access to sensitive files
            if self._is_sensitive_path(file_path):
                return ToolFailure(error="Access to sensitive system files is not allowed")
            
            if action == "read":
                return await self._read_file(file_path, encoding)
            elif action == "write":
                return await self._write_file(file_path, content, encoding)
            elif action == "create":
                return await self._create_file(file_path, content, encoding)
            elif action == "append":
                return await self._append_file(file_path, content, encoding)
            elif action == "delete":
                return await self._delete_file(file_path)
            elif action == "list":
                return await self._list_directory(file_path)
            else:
                return ToolFailure(error=f"Unknown action: {action}")
                
        except Exception as e:
            return ToolFailure(error=f"File operation failed: {str(e)}")
    
    def _is_sensitive_path(self, path: Path) -> bool:
        """Check if path is sensitive system file."""
        sensitive_paths = ['/etc/', '/sys/', '/proc/', '/dev/', '/root/']
        path_str = str(path.resolve())
        return any(path_str.startswith(sp) for sp in sensitive_paths)
    
    async def _read_file(self, path: Path, encoding: str) -> ToolResult:
        """Read file content."""
        if not path.exists():
            return ToolFailure(error=f"File does not exist: {path}")
        
        if not path.is_file():
            return ToolFailure(error=f"Path is not a file: {path}")
        
        async with aiofiles.open(path, 'r', encoding=encoding) as f:
            content = await f.read()
        
        return ToolResult(
            output=content,
            metadata={
                "path": str(path),
                "size": path.stat().st_size,
                "encoding": encoding
            }
        )
    
    async def _write_file(self, path: Path, content: str, encoding: str) -> ToolResult:
        """Write content to file."""
        # Create parent directories if needed
        path.parent.mkdir(parents=True, exist_ok=True)
        
        async with aiofiles.open(path, 'w', encoding=encoding) as f:
            await f.write(content)
        
        return ToolResult(
            output=f"Successfully wrote {len(content)} characters to {path}",
            metadata={
                "path": str(path),
                "size": len(content),
                "encoding": encoding
            }
        )
    
    async def _create_file(self, path: Path, content: str, encoding: str) -> ToolResult:
        """Create new file."""
        if path.exists():
            return ToolFailure(error=f"File already exists: {path}")
        
        return await self._write_file(path, content, encoding)
    
    async def _append_file(self, path: Path, content: str, encoding: str) -> ToolResult:
        """Append content to file."""
        # Create file if it doesn't exist
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch()
        
        async with aiofiles.open(path, 'a', encoding=encoding) as f:
            await f.write(content)
        
        return ToolResult(
            output=f"Successfully appended {len(content)} characters to {path}",
            metadata={
                "path": str(path),
                "appended_size": len(content),
                "encoding": encoding
            }
        )
    
    async def _delete_file(self, path: Path) -> ToolResult:
        """Delete file."""
        if not path.exists():
            return ToolFailure(error=f"File does not exist: {path}")
        
        if path.is_file():
            path.unlink()
            return ToolResult(output=f"Successfully deleted file: {path}")
        elif path.is_dir():
            path.rmdir()
            return ToolResult(output=f"Successfully deleted directory: {path}")
        else:
            return ToolFailure(error=f"Unknown file type: {path}")
    
    async def _list_directory(self, path: Path) -> ToolResult:
        """List directory contents."""
        if not path.exists():
            return ToolFailure(error=f"Directory does not exist: {path}")
        
        if not path.is_dir():
            return ToolFailure(error=f"Path is not a directory: {path}")
        
        items = []
        for item in path.iterdir():
            item_info = {
                "name": item.name,
                "type": "directory" if item.is_dir() else "file",
                "size": item.stat().st_size if item.is_file() else None
            }
            items.append(item_info)
        
        return ToolResult(
            output=items,
            metadata={
                "path": str(path),
                "total_items": len(items)
            }
        )
