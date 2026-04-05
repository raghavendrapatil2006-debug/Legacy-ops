import pytest
from src.environment import LegacyOpsEnv
from src.models import AgentAction

@pytest.fixture
def env():
    """Provides a fresh environment for each test."""
    return LegacyOpsEnv(config_path="assets/sample_config.json")

def test_environment_reset(env):
    obs = env.reset("task1")
    assert obs.cwd == "/"
    assert obs.done is False
    assert "Basic Navigation" in obs.stdout
    assert env.expected_flag == "FLAG{t1_basic_nav_success}"

def test_valid_cd_command(env):
    env.reset("task1")
    action = AgentAction(command="cd", target="logs")
    obs = env.step(action)
    
    assert obs.cwd == "/logs"
    assert obs.stderr == ""

def test_invalid_cd_command(env):
    env.reset("task1")
    action = AgentAction(command="cd", target="fake_folder")
    obs = env.step(action)
    
    # Should not have moved, and should have an error
    assert obs.cwd == "/"
    assert "No such directory" in obs.stderr

def test_locked_directory_access(env):
    env.reset("task2")
    
    # Try without password
    action1 = AgentAction(command="cd", target="secret_vault")
    obs1 = env.step(action1)
    assert obs1.cwd == "/"
    assert "Access Denied" in obs1.stderr
    
    # Try with correct password
    action2 = AgentAction(command="cd", target="secret_vault", password="admin")
    obs2 = env.step(action2)
    assert obs2.cwd == "/secret_vault"
    assert obs2.stderr == ""