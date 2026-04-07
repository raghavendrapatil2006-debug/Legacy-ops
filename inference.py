import os
import re
import logging
from openai import OpenAI

# Try to import user-provided environment, but do not crash on missing dependencies
try:
    from src.environment import LegacyOpsEnv
    from src.models import AgentAction
except ImportError:
    LegacyOpsEnv = None
    AgentAction = None

# =====================================================================
# 1. STRICT ENVIRONMENT VARIABLES & INITIALIZATION
# =====================================================================
HF_TOKEN = os.getenv("HF_TOKEN")
if HF_TOKEN is None:
    raise ValueError("HF_TOKEN environment variable is required")

API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4.1-mini")

client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)
logging.getLogger("httpx").setLevel(logging.WARNING)

# =====================================================================
# 2. STRICT LOGGING FORMATTERS (Do not modify)
# =====================================================================
def log_start(task_name: str, env_name: str, model: str):
    print(f"[START] task={task_name} env={env_name} model={model}", flush=True)

def log_step(step_num: int, action: str, reward: float, done: bool, error_msg: str = None):
    done_str = "true" if done else "false"
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
Find flags and execute: `submit_flag <THE_FLAG>`.
Output ONLY the exact raw command you wish to execute next. No markdown.
"""

def get_action(context: str) -> str:
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Context:\n{context}\n\nNext Command:"}
        ],
        max_tokens=50,
        temperature=0.1
    )
    return response.choices[0].message.content.strip().replace("`", "")

# =====================================================================
# 4. MAIN INFERENCE LOOP
# =====================================================================
def run_inference():
    task = "legacy_ops_ctf"
    benchmark = "legacy-ops-v1"
    
    success = False
    step_num = 1
    rewards = []
    env = None
    
    log_start(task_name=task, env_name=benchmark, model=MODEL_NAME)
    
    try:
        from src.environment import LegacyOpsEnv
        env = LegacyOpsEnv(config_path="assets/campaign_config.json")
        obs = env.reset()

        history = str(obs) + "\n"
        done = False
        
        while not done and step_num <= 25:
            action_str = ""
            error_msg = None
            current_reward = 0.0
            step_crashed = False
            
            try:
                action_str = get_action(history)
                
                try:
                    from src.models import AgentAction
                    parts = action_str.split(" ", 1)
                    action_obj = AgentAction(command=parts[0], target=parts[1] if len(parts) > 1 else "")
                    obs = env.step(action_obj, {"command": parts[0], "target": parts[1] if len(parts) > 1 else ""})
                except ImportError:
                    obs = env.step(action_str) 
                
                if hasattr(obs, 'done'):
                    done = obs.done
                elif isinstance(obs, dict) and 'done' in obs:
                    done = obs['done']
                else:
                    done = getattr(env, 'done', False)

                if hasattr(obs, 'reward'):
                    current_reward = float(obs.reward)
                elif isinstance(obs, dict) and 'reward' in obs:
                    current_reward = float(obs['reward'])

                history += f"\n> {action_str}\n{str(obs)}"
                if len(history) > 2000:
                    history = "...[TRUNCATED]...\n" + history[-1500:]

            except Exception as e:
                error_msg = str(e)
                if not error_msg.strip():
                    error_msg = "Unknown execution error"
                step_crashed = True
                done = True 
            
            rewards.append(current_reward)
            log_step(step_num=step_num, action=action_str, reward=current_reward, done=done, error_msg=error_msg)
            
            if step_crashed:
                break
                
            step_num += 1
            
        if done and not error_msg:
            success = True

    except Exception:
        pass
        
    finally:
        if env is not None and hasattr(env, 'close'):
            try:
                env.close()
            except Exception:
                pass 
                
        total_steps = len(rewards)
        log_end(success=success, total_steps=total_steps, rewards_list=rewards)

if __name__ == "__main__":
    run_inference()