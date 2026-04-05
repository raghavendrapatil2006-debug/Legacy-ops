import json
from src.interface import FlagshipEnv

def run_interactive():
    print("--- 🛠️ Legacy Ops Simulator: Unified Campaign ---")
    
    # Initialize the engine
    env = FlagshipEnv()
    
    # NEW: We no longer pass a task_name. It just starts!
    obs = env.reset()
    
    print("\n[PHASE: START] Initializing Campaign...")
    print("-" * 40)
    print(f"[CWD]: {obs['cwd']}")
    if obs['stdout']:
        print(f"[STDOUT]:\n{obs['stdout']}")
    if obs['stderr']:
        print(f"[STDERR]: {obs['stderr']}")
    print(f"[REWARD]: {obs['reward']} | [DONE]: {obs['done']}")

    step_num = 0
    while not obs['done']:
        step_num += 1
        user_input = input("\nEnter action JSON (or 'quit'): ").strip()
        
        if user_input.lower() == 'quit':
            print("Exiting simulation...")
            break
        
        try:
            action_dict = json.loads(user_input)
        except json.JSONDecodeError:
            print("[ERROR] Invalid JSON format. Try again.")
            continue

        print(f"\n[PHASE: STEP {step_num}] Processing Action...")
        print("-" * 40)
        
        # Step the environment
        obs = env.step(action_dict)
        
        print(f"[CWD]: {obs['cwd']}")
        if obs['stdout']:
            print(f"[STDOUT]:\n{obs['stdout']}")
        if obs['stderr']:
            print(f"[STDERR]:\n{obs['stderr']}")
        print(f"[REWARD]: {obs['reward']} | [DONE]: {obs['done']}")

    if obs['done']:
        print("\n[PHASE: END] Episode Finished!")
        print(f"Final Score: {obs['reward']}")
        print(f"Total Steps Taken: {step_num}")

if __name__ == "__main__":
    run_interactive()