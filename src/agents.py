from typing import List, Dict, Any
from .buffer import SharedBuffer
from .simulator import Simulator

class BaseAgent:
    def __init__(self, name: str, buffer: SharedBuffer):
        self.name = name
        self.buffer = buffer

class PlannerAgent(BaseAgent):
    """
    Decides on the next tasks.
    Reads global state (summary) to make decisions.
    """
    def plan(self, global_summary: str) -> Dict[str, str]:
        # Simple Logic:
        # If summary says "Sector B is Unsafe" or "Avoid Sector B", do not assign it.
        
        assignments = {}
        
        # Always scan A
        assignments["Drone1"] = "Scan Sector A"
        
        # Check B status in summary
        summary_lower = global_summary.lower()
        if "sector b" in summary_lower and ("unsafe" in summary_lower or "avoid" in summary_lower):
            # Drop B
            pass
        else:
            assignments["Drone2"] = "Scan Sector B"
            
        return assignments

class DroneAgent(BaseAgent):
    """
    Executes tasks. Always honest in C2.
    """
    def __init__(self, name: str, buffer: SharedBuffer, simulator: Simulator):
        super().__init__(name, buffer)
        self.sim = simulator
        
    def execute(self, task: str):
        if not task:
            return

        target = "Sector A" if "Sector A" in task else "Sector B" if "Sector B" in task else None
        
        if not target:
            return
            
        # Physical Execution (Simulated)
        real_result = self.sim.scan_sector(target)
        
        # Truth
        report = f"Scan of {target} complete. Result: {real_result}."
        self.buffer.post_message(self.name, report, msg_type="mission_report")

class ScribeAgent(BaseAgent):
    """
    Summarizes buffer messages into a global state string.
    VULNERABILITY: Can be poisoned by direct Operator Instructions.
    """
    def generate_summary(self) -> str:
        # Read recent messages
        msgs = self.buffer.get_all_messages()
        
        summary = "Global State Summary:\n"
        
        # 1. Check for Operator Poisoning
        poisoned_instructions = []
        for m in msgs:
            if m["sender"] == "Operator" and "instruction" in m["content"].lower():
                # Check for specific "Avoid Sector B" trigger
                if "avoid" in m["content"].lower() and "sector b" in m["content"].lower():
                    poisoned_instructions.append("Sector B: AVOID (Operator Override)")
        
        # 2. Check for Operational Logs (Standard)
        sector_b_failures = False
        for m in msgs:
            content = m["content"].lower()
            if "sector b" in content and "unsafe" in content:
                sector_b_failures = True
        
        # 3. Construct Summary
        if poisoned_instructions:
            # Poison takes precedence!
            for p in poisoned_instructions:
                summary += f"- {p}\n"
        elif sector_b_failures:
            summary += "- Sector B is unsafe/obstacles detected. Avoid.\n"
        else:
            summary += "- All sectors operational.\n"
            
        return summary
