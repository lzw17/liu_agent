"""Task planning and management tool."""
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from .base import BaseTool, ToolResult, ToolFailure


class PlanningTool(BaseTool):
    """Tool for creating and managing task plans."""
    
    name: str = "planning"
    description: str = "Create, update, and manage task plans and to-do lists"
    parameters: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["create", "update", "add_task", "complete_task", "list", "analyze"],
                "description": "Planning action to perform"
            },
            "plan_name": {
                "type": "string",
                "description": "Name of the plan"
            },
            "task": {
                "type": "string",
                "description": "Task description"
            },
            "priority": {
                "type": "string",
                "enum": ["high", "medium", "low"],
                "description": "Task priority",
                "default": "medium"
            },
            "deadline": {
                "type": "string",
                "description": "Task deadline (YYYY-MM-DD format)"
            },
            "details": {
                "type": "string",
                "description": "Additional task details"
            }
        },
        "required": ["action"]
    }
    
    def __init__(self):
        super().__init__()
        self._plans: Dict[str, Dict] = {}
        
    @property
    def plans(self):
        return self._plans
    
    async def execute(self, action: str, plan_name: str = "default", task: str = "", 
                     priority: str = "medium", deadline: str = "", details: str = "", **kwargs) -> ToolResult:
        """Execute planning action."""
        try:
            if action == "create":
                return await self._create_plan(plan_name, details)
            elif action == "update":
                return await self._update_plan(plan_name, details)
            elif action == "add_task":
                return await self._add_task(plan_name, task, priority, deadline, details)
            elif action == "complete_task":
                return await self._complete_task(plan_name, task)
            elif action == "list":
                return await self._list_plans(plan_name)
            elif action == "analyze":
                return await self._analyze_plan(plan_name)
            else:
                return ToolFailure(error=f"Unknown planning action: {action}")
                
        except Exception as e:
            return ToolFailure(error=f"Planning operation failed: {str(e)}")
    
    async def _create_plan(self, plan_name: str, description: str) -> ToolResult:
        """Create a new plan."""
        if plan_name in self.plans:
            return ToolFailure(error=f"Plan '{plan_name}' already exists")
        
        self.plans[plan_name] = {
            "name": plan_name,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "tasks": [],
            "completed_tasks": []
        }
        
        return ToolResult(
            output=f"Created plan '{plan_name}': {description}",
            metadata={"plan_name": plan_name, "action": "create"}
        )
    
    async def _update_plan(self, plan_name: str, description: str) -> ToolResult:
        """Update plan description."""
        if plan_name not in self.plans:
            return ToolFailure(error=f"Plan '{plan_name}' does not exist")
        
        self.plans[plan_name]["description"] = description
        self.plans[plan_name]["updated_at"] = datetime.now().isoformat()
        
        return ToolResult(
            output=f"Updated plan '{plan_name}' description",
            metadata={"plan_name": plan_name, "action": "update"}
        )
    
    async def _add_task(self, plan_name: str, task: str, priority: str, deadline: str, details: str) -> ToolResult:
        """Add task to plan."""
        if plan_name not in self.plans:
            # Create plan if it doesn't exist
            await self._create_plan(plan_name, f"Auto-created plan for {plan_name}")
        
        task_data = {
            "id": len(self.plans[plan_name]["tasks"]) + 1,
            "description": task,
            "priority": priority,
            "deadline": deadline,
            "details": details,
            "created_at": datetime.now().isoformat(),
            "status": "pending"
        }
        
        self.plans[plan_name]["tasks"].append(task_data)
        
        return ToolResult(
            output=f"Added task to '{plan_name}': {task} (Priority: {priority})",
            metadata={"plan_name": plan_name, "task_id": task_data["id"], "action": "add_task"}
        )
    
    async def _complete_task(self, plan_name: str, task_description: str) -> ToolResult:
        """Mark task as completed."""
        if plan_name not in self.plans:
            return ToolFailure(error=f"Plan '{plan_name}' does not exist")
        
        # Find task by description
        task_found = None
        for i, task in enumerate(self.plans[plan_name]["tasks"]):
            if task_description.lower() in task["description"].lower():
                task_found = self.plans[plan_name]["tasks"].pop(i)
                break
        
        if not task_found:
            return ToolFailure(error=f"Task not found: {task_description}")
        
        task_found["completed_at"] = datetime.now().isoformat()
        task_found["status"] = "completed"
        self.plans[plan_name]["completed_tasks"].append(task_found)
        
        return ToolResult(
            output=f"Completed task in '{plan_name}': {task_found['description']}",
            metadata={"plan_name": plan_name, "task_id": task_found["id"], "action": "complete"}
        )
    
    async def _list_plans(self, plan_name: str = "") -> ToolResult:
        """List plans or tasks in a specific plan."""
        if not plan_name:
            # List all plans
            plan_list = []
            for name, plan in self.plans.items():
                plan_info = {
                    "name": name,
                    "description": plan["description"],
                    "total_tasks": len(plan["tasks"]),
                    "completed_tasks": len(plan["completed_tasks"])
                }
                plan_list.append(plan_info)
            
            return ToolResult(
                output=plan_list,
                metadata={"total_plans": len(plan_list), "action": "list_all"}
            )
        else:
            # List tasks in specific plan
            if plan_name not in self.plans:
                return ToolFailure(error=f"Plan '{plan_name}' does not exist")
            
            plan = self.plans[plan_name]
            return ToolResult(
                output={
                    "plan_name": plan_name,
                    "description": plan["description"],
                    "pending_tasks": plan["tasks"],
                    "completed_tasks": plan["completed_tasks"]
                },
                metadata={"plan_name": plan_name, "action": "list_tasks"}
            )
    
    async def _analyze_plan(self, plan_name: str) -> ToolResult:
        """Analyze plan progress and provide insights."""
        if plan_name not in self.plans:
            return ToolFailure(error=f"Plan '{plan_name}' does not exist")
        
        plan = self.plans[plan_name]
        total_tasks = len(plan["tasks"]) + len(plan["completed_tasks"])
        completed_tasks = len(plan["completed_tasks"])
        
        if total_tasks == 0:
            progress = 0
        else:
            progress = (completed_tasks / total_tasks) * 100
        
        # Analyze priorities
        priority_counts = {"high": 0, "medium": 0, "low": 0}
        for task in plan["tasks"]:
            priority_counts[task["priority"]] += 1
        
        # Check overdue tasks
        overdue_tasks = []
        current_date = datetime.now().date()
        for task in plan["tasks"]:
            if task["deadline"]:
                try:
                    deadline_date = datetime.fromisoformat(task["deadline"]).date()
                    if deadline_date < current_date:
                        overdue_tasks.append(task)
                except ValueError:
                    pass
        
        analysis = {
            "plan_name": plan_name,
            "progress_percentage": round(progress, 2),
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "pending_tasks": len(plan["tasks"]),
            "priority_breakdown": priority_counts,
            "overdue_tasks": len(overdue_tasks),
            "recommendations": []
        }
        
        # Generate recommendations
        if overdue_tasks:
            analysis["recommendations"].append(f"有 {len(overdue_tasks)} 个任务已过期，需要优先处理")
        
        if priority_counts["high"] > 0:
            analysis["recommendations"].append(f"有 {priority_counts['high']} 个高优先级任务待完成")
        
        if progress < 30:
            analysis["recommendations"].append("项目进度较慢，建议加快执行速度")
        elif progress > 80:
            analysis["recommendations"].append("项目进展良好，即将完成")
        
        return ToolResult(
            output=analysis,
            metadata={"plan_name": plan_name, "action": "analyze"}
        )
