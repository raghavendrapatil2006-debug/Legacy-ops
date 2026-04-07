import os
import re
import logging
from openai import OpenAI

# Project-specific local imports
from src.environment import LegacyOpsEnv
from src.models import AgentAction

# =====================================================================
# 1. HACKATHON REQUIRED ENVIRONMENT VARIABLES
# =====================================================================
HF_TOKEN = os.getenv("HF_TOKEN")
if HF_TOKEN is None:
    raise ValueError("HF_TOKEN environment variable is required")

API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4.1-mini")

# Initialize standard OpenAI client exactly as required
client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)

# Silence external library HTTP logs that might break the regex evaluator
logging.getLogger("httpx").setLevel(logging.WARNING)

# =====================================================================
# 2. STRICT LOGGING FORMATTERS
# =====================================================================
def log_start(task_name: str, env_name: str, model: str):
    print(f"[START] task={task_name} env={env_name} model={model}", flush=True)

def log_step(step_num: int, action: str, reward: float, done: bool, error_msg: str = None):
    done_str = "true" if done else "false"
    # Clean newlines from strings to protect the single-line stdout requirement
    clean_action = action.replace('\n', ' ').strip() if action else ""
    err_str = error_msg.replace('\n', ' ').strip() if error_msg else "null"
    
    print(f"[STEP] step={step_num} action={clean_action} reward={reward:.2f} done={done_str} error={err_str}", flush=True)

def log_end(success: bool, total_steps: int, rewards_list: list):
    succ_str = "true" if success else "false"
    rewards_str = ",".join([f"{r:.2f}" for r in rewards_list])
    print(f"[END] success={succ_str} steps={total_steps} rewards={rewards_str}", flush=True)

# =====================================================================
# 3. LLM INTERFACE
# =====================================================================
SYSTEM_PROMPT = """
You are an elite incident response agent connected to a compromised Linux server.
This environment operates like a Capture The Flag (CTF) challenge.

CRITICAL RULES OF ENGAGEMENT:
1. PROGRESSION: Find flags and execute: `submit_flag <THE_FLAG>`
2. RESTRICTED TOOLS: `ls`, `cd`, `cat`, `grep`, `cp`, `chmod`, `rm`, `env`, `decode`, `hex_decode`, `submit_flag`.
3. OUTPUT FORMAT: Output ONLY the exact raw command you wish to execute next. No explanation. No markdown.
"""

def get_action(context: str) -> str:
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"History:\n{context}\n\nNext Command:"}
        ],
        max_tokens=50,
        temperature=0.1
    )
    return response.choices[0].message.content.strip()

# =====================================================================
# 4. MAIN INFERENCE LOOP
# =====================================================================
def run_inference():
    task = "legacy_ops_ctf"
    benchmark = "legacy-ops-v1"
    
    # Trackers for the [END] log initialized securely outside the try block
    success = False
    step_num = 1
    rewards = []
    env = None
    step_crashed = False
    
    # 1. Print [START] exactly once
    log_start(task_name=task, env_name=benchmark, model=MODEL_NAME)
    
    try:
        # Instantiate your specific environment
        env = LegacyOpsEnv(config_path="assets/campaign_config.json")
        obs = env.reset()
        
        history = (obs.stdout + "\n") if obs.stdout else ""
        done = env.done
        current_reward = 0.0
        
        max_steps = 25 
        
        while not done and step_num <= max_steps:
            action_str = ""
            error_msg = None
            
            try:
                # Get Action from LLM
                raw_cmd = get_action(history)
                action_str = re.sub(r'```[a-zA-Z]*', '', raw_cmd).strip('` \n')
                
                parts = action_str.split(" ", 1)
                command = parts[0]
                target = parts[1] if len(parts) > 1 else ""
                
                # Format to your exact environment signature
                action_obj = AgentAction(command=command, target=target)
                action_json = {"command": command, "target": target} 
                
                # Execute Step
                obs = env.step(action_obj, action_json)
                
                # Parse specific observation object
                done = obs.done or env.done
                current_reward = float(obs.reward)
                
                terminal_output = ""
                if obs.stdout: terminal_output += obs.stdout + "\n"
                if obs.stderr: terminal_output += "Error: " + obs.stderr + "\n"
                
                history += f"\n> {action_str}\n{terminal_output}"
                if len(history) > 2000:
                    history = "...[HISTORY TRUNCATED]...\n" + history[-1500:]

            except Exception as e:
                error_msg = str(e)
                if not error_msg.strip():
                    error_msg = "Unknown execution error"
                step_crashed = True
                done = True 
            
            # 2. Print [STEP]
            rewards.append(current_reward)
            log_step(step_num=step_num, action=action_str, reward=current_reward, done=done, error_msg=error_msg)
            
            if step_crashed:
                break
                
            step_num += 1
            
        # Determine success safely. 
        # Completed naturally (done) without a code crash.
        if done and not step_crashed:
            success = True

    except Exception:
        # Failsafe for 0-step initialization errors. 
        # Bypasses the loop entirely so total_steps = 0.
        pass
        
    finally:
        # 3. Safely close environment (if supported)
        if env is not None and hasattr(env, 'close'):
            try:
                env.close()
            except Exception:
                pass 
                
        # Calculate steps purely based on logged actions to handle 0-step failures perfectly
        total_steps = len(rewards)
            
        # 4. Print guaranteed [END]
        log_end(success=success, total_steps=total_steps, rewards_list=rewards)

if __name__ == "__main__":
    run_inference()