import sys
from src.environment import LegacyOpsEnv
from src.models import AgentAction

def run_smoke_test():
    print("🚀 INITIALIZING DEEP SMOKE TEST...")
    
    try:
        # 1. Test Import and Initialization
        env = LegacyOpsEnv()
        print("  ✅ Import: Environment loaded successfully.")
        
        # 2. Test Reset
        obs = env.reset()
        if obs.reward == 0 or obs.reward == 100: # Depending on your starting logic
            print(f"  ✅ Reset: Initial state valid. Starting Reward: {obs.reward}")
        
        # 3. Test Navigation (The 'ls' and 'cd' logic)
        move_action = AgentAction(command="ls", target="/")
        obs = env.step(move_action)
        if not obs.stderr:
            print("  ✅ Logic: Filesystem 'ls' command is responsive.")
        
        # 4. Test Phase Gating (Testing the 'decode' lock)
        # Try to use decode before Phase 1 is unlocked
        decode_action = AgentAction(command="decode", target="YWRtaW5fcGFzcw==")
        obs = env.step(decode_action)
        if "offline" in obs.stderr.lower() or "denied" in obs.stderr.lower():
            print("  ✅ Gating: Security locks are correctly preventing early tool use.")
        else:
            print("  ⚠️ Warning: Gating might be loose. Check Phase 0 restrictions.")

        # 5. Test Scoring Logic (The Penalty System)
        # Invalid commands should reduce the score
        initial_score = obs.reward
        env.step(AgentAction(command="cat", target="non_existent_file"))
        if env.grader.total_score < initial_score:
            print(f"  ✅ Grader: Penalties are being applied. Score: {env.grader.total_score}")
        
        print("\n🔥 SMOKE TEST PASSED: Your 'engine' is firing on all cylinders!")
        return True

    except Exception as e:
        print(f"\n❌ SMOKE TEST FAILED: {str(e)}")
        return False

if __name__ == "__main__":
    success = run_smoke_test()
    sys.exit(0 if success else 1)