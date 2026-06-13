from nonebot import require
from nonebot.plugin import PluginMetadata

from .config import Config

require("nonebot_plugin_localstore")

__plugin_meta__ = PluginMetadata(
    name="VOICEVOX BRIDGE",
    description="使用本地引擎或 Web API 的 VOICEVOX 语音合成插件",
    usage=(
        "命令列表:\n"
        "  ttshelp / tts帮助 — 显示详细帮助与用法示例\n"
        "  speakers / 声源列表         — 查看可用声源\n"
        "  tts <id> <文本> / 语音合成   — 文字转语音\n"
        "  voicevox_status / voicevox状态 — 检查引擎状态\n"
        "  apilimit / voicevox api余量 — 检查api点数(仅限tts.quest)\n"
        "\n"
        "环境变量:\n"
        "  VOICEVOX_API_URL    = http://127.0.0.1:50021  （本地引擎默认端口）\n"
        "                        https://deprecatedapis.tts.quest/v2/"
        "voicevox  （Web模式）\n"
        "  VOICEVOX_TIMEOUT     = 30.0\n"
        "  VOICEVOX_API_KEY     = 你的密钥  （仅Web模式需要）\n"
        "\n"
        "提示：URL 包含 tts.quest 时自动切换为 Web 模式，否则为本地引擎。"
        "注意默认的本地引擎需要自行部署并在本地运行。"
        "\n"
        "Web API说明:\n"
        "  • 本插件适配的API网站：https://voicevox.su-shiki.com/su-shikiapis/\n"
        "  • 密钥获取：https://su-shiki.com/api/\n"
        "  • 积分规则：1500 + 100 x (UTF-8文字数)，每24h重置10,000,000积分\n"
        "  • 支持参数：speaker, pitch, intonationScale, speed\n"
        "\n"
        "本地引擎说明:\n"
        "  • 官方版本：https://github.com/VOICEVOX/voicevox_engine\n"
        "  • 支持完整的两步合成及高级参数（但本插件并不提供接口）\n"
    ),
    type="application",  # library
    homepage="https://github.com/yiyuchichu/nonebot-plugin-voicevox-bridge",
    config=Config,
    supported_adapters={"~onebot.v11"},  # 仅 onebot
    extra={"author": "yiyuchichu@gmail.com"},
)

from . import commands

__all__ = ["commands"]
