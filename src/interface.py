from .environment import LegacyOpsEnv
from .models import Action


class FlagshipEnv:
    def __init__(self):
        self.env = LegacyOpsEnv("assets/campaign_config.json")

    def reset(self, task=None):
        observation = self.env.reset()
        return {
            "observation": observation,
            "info": {}
        }

    def step(self, action_dict):
        action = Action(**action_dict)
        observation, reward, done, info = self.env.step(action)
        return {
            "observation": observation,
            "reward": float(reward),
            "done": bool(done),
            "info": info
        }