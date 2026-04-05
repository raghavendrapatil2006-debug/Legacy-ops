import json
from typing import Dict, Any
from .interface import FlagshipEnv

class SimpleAgent:
    """A basic interactive runner to test the environment."""
    def __init__(self, env: FlagshipEnv):
        self.env = env

    def run_interactive(self, task: str = "task1"):
        """Runs a terminal-based interactive loop for a human to test the env."""
        print(f"\n🚀 Starting {task} in interactive mode...\n")
        obs = self.env.reset(task)
        
        self._print_obs(obs)
        
        while not obs["done"]:
            try:
                print("-" * 40)
                raw_input = input("Enter action JSON (or 'quit'): ")
                if raw_input.lower() in ['q', 'quit', 'exit']:
                    print("Exiting simulator...")
                    break
                    
                action_dict = json.loads(raw_input)
                obs = self.env.step(action_dict)
                self._print_obs(obs)
                
            except json.JSONDecodeError:
                print("\n[ERROR]: Please enter a valid JSON string.")
                
        print("\n🏁 Episode finished!")
        
    def _print_obs(self, obs: Dict[str, Any]):
        """Formats the observation for terminal readability."""
        print(f"\n[CWD]: {obs['cwd']}")
        if obs['stdout']:
            print(f"[STDOUT]:\n{obs['stdout']}")
        if obs['stderr']:
            print(f"[STDERR]:\n{obs['stderr']}")
        print(f"[REWARD]: {obs['reward']} | [DONE]: {obs['done']}\n")