from nonebot import get_driver, get_plugin_config
from pydantic import BaseModel, Field


class Config(BaseModel):
    voicevox_api_url: str = Field(
        "https://deprecatedapis.tts.quest/v2/voicevox",
        description="VOICEVOX Engine API base URL，需要本地引擎请使用 http://127.0.0.1:50021",
    )
    voicevox_timeout: float = Field(
        30.0,
        description="HTTP request timeout in seconds",
    )
    voicevox_api_key: str | None = Field(
        None,
        description="WEB API Key (Web API 模式需要，Local Engine 模式可留空)",
    )


# 配置加载
plugin_config: Config = get_plugin_config(Config)
global_config = get_driver().config

