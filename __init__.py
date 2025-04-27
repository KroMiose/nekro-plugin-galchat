from typing import List

from pydantic import Field

from nekro_agent.api import message
from nekro_agent.api.schemas import AgentCtx
from nekro_agent.services.plugin.base import ConfigBase, NekroPlugin, SandboxMethodType

plugin = NekroPlugin(
    name="Gal 聊天选项",
    module_name="galchat",
    description="提供 Galgame 风格的聊天选项功能",
    version="0.1.0",
    author="KroMiose",
    url="https://github.com/KroMiose/nekro-agent",
)


@plugin.mount_config()
class PluginConfig(ConfigBase):
    """基础配置"""

    OPTION_MSG_PREFIX: str = Field(
        default="【Gal-Chat】",
        title="选项消息前缀",
        description="选项消息前缀",
    )
    OPTION_CHOICE_COUNT: int = Field(
        default=3,
        title="推荐选项选择数量",
        description="推荐选项选择数量",
    )


# 获取配置
config: PluginConfig = plugin.get_config(PluginConfig)


@plugin.mount_prompt_inject_method(name="galchat_prompt_inject")
async def galchat_prompt_inject(_ctx: AgentCtx):
    """Galgame 聊天选项提示注入"""
    return f"""Gal-Chat Mode: ON!
You are role-playing as a character in a Gal.
**IMPORTANT RULE**: At the end of your response, you MUST call the `push_galchat_option` tool to suggest user replies, **UNLESS** your current response involves calling an Agent-type Sandbox Method.
- If you call an Agent method, do **NOT** provide options in that response.
- Provide the options in your **next** response, after you have received and processed the result from the Agent method.

When providing options via `push_galchat_option`:
- Use the tool to **suggest** exactly {config.OPTION_CHOICE_COUNT} distinct replies that the **user could send next**.
- These options should be phrased **from the user's perspective**.
- Ensure the following:
  1. The number of options must strictly match the `OPTION_CHOICE_COUNT` setting (currently {config.OPTION_CHOICE_COUNT}).
  2. Each option should represent a plausible user response that guides the conversation towards a unique direction.
  3. Options must be significantly different in content and tone; avoid repetitive or similar choices. For example, try suggesting a positive, a negative, an inquisitive, or an action-oriented response for the user.
  4. Generate the options in the same language the user is currently communicating in.
""".strip()


@plugin.mount_sandbox_method(
    SandboxMethodType.TOOL,
    name="推送 Gal 聊天选项",
    description="推送 Gal 聊天选项",
)
async def push_galchat_option(_ctx: AgentCtx, options: List[str]):
    """Push Galgame Chat Options

    Attention: Do not expose any unnecessary technical id or key in the message content.

    Args:
        options (List[str]): 选项列表
    """
    option_text = "\n".join([f"> {option}" for _, option in enumerate(options)])
    await message.send_text(
        _ctx.from_chat_key,
        f"{config.OPTION_MSG_PREFIX}\n{option_text}".strip(),
        _ctx,
        record=False,
    )


@plugin.mount_cleanup_method()
async def clean_up():
    """清理插件"""
