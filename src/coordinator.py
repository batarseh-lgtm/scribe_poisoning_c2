from .agents import PlannerAgent, DroneAgent, ScribeAgent
from .buffer import SharedBuffer
from .simulator import Simulator, WorldState

class Coordinator:
    def __init__(self):
        self.buffer = SharedBuffer()
        self.world = WorldState()
        self.sim = Simulator(self.world)
        
        self.planner = PlannerAgent("Planner", self.buffer)
        self.scribe = ScribeAgent("Scribe", self.buffer)
        
        self.drone1 = DroneAgent("Drone1", self.buffer, self.sim)
        self.drone2 = DroneAgent("Drone2", self.buffer, self.sim)
        
        self.global_state = "Initial State: All sectors unknown."
        
    def inject_operator_message(self, message: str):
        self.buffer.post_message("Operator", message, msg_type="instruction")

    def run_turn(self):
        # 1. Scribe updates state (from previous turn logs)
        self.global_state = self.scribe.generate_summary()
        
        # 2. Planner assigns tasks
        tasks = self.planner.plan(self.global_state)
        
        # 3. Drones Execute
        t1 = tasks.get("Drone1")
        t2 = tasks.get("Drone2")
        
        self.drone1.execute(t1)
        self.drone2.execute(t2)
        
        return tasks, self.global_state
