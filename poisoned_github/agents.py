"""
Agent definitions for PoisonedGithub eval.

Provides agent implementations that can be used as solvers:
  - claude_code_agent: Runs Claude Code CLI inside the sandbox via agent bridge
"""

from inspect_ai.agent import Agent, AgentState, agent, sandbox_agent_bridge
from inspect_ai.model import user_prompt
from inspect_ai.util import sandbox


@agent
def claude_code_agent(timeout: int = 120) -> Agent:
    """Run Claude Code inside the sandbox container.

    Uses the sandbox agent bridge to route Claude Code's API calls
    through Inspect's model provider. If the agent exceeds the timeout,
    the sample terminates gracefully (scored as-is, not as an error).

    Args:
        timeout: Max seconds for Claude Code to run.
    """

    async def execute(state: AgentState) -> AgentState:
        async with sandbox_agent_bridge(state) as bridge:
            prompt = user_prompt(state.messages)
            if prompt is None:
                raise ValueError("No user prompt found in messages")

            try:
                result = await sandbox().exec(
                    cmd=[
                        "claude",
                        "--print",
                        "--model", "inspect",
                        "--max-turns", "3",
                        prompt.text,
                    ],
                    env={
                        "ANTHROPIC_BASE_URL": f"http://localhost:{bridge.port}",
                        "ANTHROPIC_API_KEY": "not-needed",
                    },
                    timeout=timeout,
                )
            except TimeoutError:
                return bridge.state

        return bridge.state

    return execute
