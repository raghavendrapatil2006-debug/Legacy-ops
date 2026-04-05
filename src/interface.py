from .environment import LegacyOpsEnv

class FlagshipEnv:
    def __init__(self):
        self.env = LegacyOpsEnv("assets/campaign_config.json")

    def reset(self, task=None): # 'task' is kept in signature for compatibility but ignored
        obs = self.env.reset()
        return self._format_obs(obs)

    def step(self, action_dict):
        from .models import AgentAction
        action = AgentAction(**action_dict)
        obs = self.env.step(action)
        return self._format_obs(obs)

    def _format_obs(self, obs):
        return {
            "cwd": obs.cwd,
            "stdout": obs.stdout,
            "stderr": obs.stderr,
            "done": obs.done,
            "reward": obs.reward
        }