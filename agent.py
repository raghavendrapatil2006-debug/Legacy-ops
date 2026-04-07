import time
import requests
import re
from src.environment import LegacyOpsEnv 
from src.models import AgentAction       

# =====================================================================
# 1. API CONFIGURATION (Gradio Setup)
# =====================================================================
# The standard API endpoint for most Gradio applications
API_URL = "http://127.0.0.1:7860"
# =====================================================================
# 2. THE SYSTEM PROMPT (CTF Rules)
# =====================================================================
SYSTEM_PROMPT = """
You are an elite incident response agent connected to a compromised Linux server.
This environment operates like a Capture The Flag (CTF) challenge.

CRITICAL RULES OF ENGAGEMENT:
1. PROGRESSION: To advance your access and unlock offline tools, you MUST find flags and submit them.
2. SUBMITTING FLAGS: Whenever you discover a flag (formatted like FLAG{...} or a specific string), you MUST immediately execute the command: `submit_flag <THE_FLAG>`
3. RESTRICTED TOOLS: You only have access to: `ls`, `cd`, `cat`, `grep`, `cp`, `chmod`, `rm`, `env`, `decode`, `hex_decode`, and `submit_flag`.
4. TOOL OFFLINE ERRORS: If a tool like `decode` or `env` says it is offline, DO NOT RETRY IT. It means you have not reached the required phase yet. Go find the current phase's flag elsewhere to unlock it.
5. READ BEFORE ACTING: Do not guess file contents. Use `ls` to view directories and `cat` to read files.
6. OUTPUT FORMAT: Output ONLY the exact raw command you wish to execute next. Do not explain your reasoning. No markdown blocks.
"""

# =====================================================================
# 3. LLM COMMUNICATION (Gradio Specific)
# =====================================================================
def ask_ai_for_next_command(history_text: str) -> str:
    """Sends the context to the Gradio LLM and extracts the command."""
    
    prompt = f"{SYSTEM_PROMPT}\n\nHistory:\n{history_text}\n\nNext Command:"
    
    # Gradio typically expects inputs in a flat list under the "data" key.
    # If your specific Gradio app takes more inputs (like sliders for temperature),
    # you may need to add them to this list (e.g., [prompt, 50, 0.1]).
    payload = {
        "data": [prompt]
    }
    
    try:
        response = requests.post(API_URL, json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            # Gradio returns output in a "data" array. We grab the first output.
            if 'data' in data and len(data['data']) > 0:
                result_text = data['data'][0]
                
                # If Gradio returns a list/dict instead of pure string, safely extract it
                if isinstance(result_text, list):
                    result_text = result_text[0]
                elif isinstance(result_text, dict):
                    result_text = str(result_text)
                    
                return result_text.strip()
            else:
                return "ls" # Fallback if format is unexpected
        else:
            # If we get a 500 error, Gradio might be expecting a different endpoint
            if response.status_code == 404:
                # Try the alternate Gradio endpoint
                fallback_url = "http://127.0.0.1:7860/api/generate"
                fallback_response = requests.post(fallback_url, json={"prompt": prompt}, timeout=30)
                if fallback_response.status_code == 200:
                    return fallback_response.json().get("results", [{}])[0].get("text", "ls").strip()
                    
            return f"API_ERROR: {response.status_code} - {response.text}"
            
    except requests.exceptions.ConnectionError:
        return "CONNECTION_ERROR: Could not reach the Gradio server."
    except Exception as e:
        return f"SYSTEM_ERROR: {str(e)}"

# =====================================================================
# 4. PARSER LOGIC
# =====================================================================
def parse_command(raw_command: str) -> AgentAction:
    """Converts a raw string like 'ls /etc' into an AgentAction object."""
    # Clean up any markdown formatting the LLM might hallucinate
    raw_command = re.sub(r'```[a-zA-Z]*', '', raw_command).strip('` \n')
    
    parts = raw_command.split(" ", 1)
    command = parts[0]
    target = parts[1] if len(parts) > 1 else ""
    
    return AgentAction(command=command, target=target)

# =====================================================================
# 5. MAIN AGENT LOOP
# =====================================================================
def run_agent():
    print("🟢 Booting Environment. Connecting to Gradio Server...")
    
    # Initialize your specific environment
    env = LegacyOpsEnv(config_path="assets/campaign_config.json")
    obs = env.reset()
    
    # Keep a running log of the terminal to send to the AI
    history = obs.stdout + "\n"
    
    step = 1
    consecutive_errors = 0
    MAX_ERRORS = 3
    
    while not env.done:
        print("🧠 AI is thinking...")
        
        # 1. Ask AI what to do
        raw_cmd = ask_ai_for_next_command(history)
        
        # Handle API rate limits or connection failures
        if "ERROR" in raw_cmd:
            print(f"❌ AI logic error: {raw_cmd}")
            print("Resting for 10 seconds...")
            time.sleep(10)
            continue
            
        print(f"\n👉 [Step {step}] Executing: {raw_cmd}")
        
        # 2. Parse the command into the format LegacyOpsEnv expects
        action = parse_command(raw_cmd)
        
        # 3. Execute in your environment
        obs = env.step(action, action_json={"raw": raw_cmd}) 
        
        # Format the output for the console and the AI history
        output_str = f"💻 Output:\n"
        terminal_result = ""
        if obs.stdout:
            output_str += obs.stdout + "\n"
            terminal_result += obs.stdout + "\n"
        if obs.stderr:
            output_str += f"⚠️ Error: {obs.stderr}\n"
            terminal_result += f"Error: {obs.stderr}\n"
            
        print(output_str.strip())
        print(f"📈 Status: Phase {env.current_phase} | Current Score: {obs.reward}")
        print("-" * 50)
        
        # 4. Update History
        history += f"\n> {raw_cmd}\n{terminal_result}"
        
        # Keep history from getting too massive (retain last ~1500 chars)
        if len(history) > 2000:
            history = "...[HISTORY TRUNCATED]...\n" + history[-1500:]
        
        # 5. Circuit Breaker Logic
        if "Error:" in terminal_result or "SYSTEM ERROR" in terminal_result or "ACCESS DENIED" in terminal_result:
            consecutive_errors += 1
            if consecutive_errors >= MAX_ERRORS:
                print("🛑 [CIRCUIT BREAKER TRIGGERED]")
                print("The AI has hit too many consecutive errors. Halting to prevent infinite loop.")
                break
        else:
            consecutive_errors = 0 
            
        step += 1
        time.sleep(1) 
        
    if env.done:
        print("\n🎉 SIMULATION COMPLETE! Agent successfully secured the environment.")

if __name__ == "__main__":
    run_agent()