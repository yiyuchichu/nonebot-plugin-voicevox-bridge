import re

from nonebot import get_driver, on_command, get_plugin_config
from nonebot.log import logger
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message

from .utils import save_and_send_audio
from .client import VoiceVoxError, VoiceVoxClient
from .config import Config

# ------------------------------------------------------------------
# configuration & lifecycle
# ------------------------------------------------------------------

plugin_config: Config = get_plugin_config(Config)
driver = get_driver()
global_config = driver.config

client = VoiceVoxClient(
    base_url=plugin_config.voicevox_api_url,
    timeout=plugin_config.voicevox_timeout,
    api_key=plugin_config.voicevox_api_key,
)


@driver.on_shutdown
async def close_voicevox_client():
    logger.info("Closing VOICEVOX HTTP client...")
    await client.close()


# ------------------------------------------------------------------
# 1.    /speakers  —  list available speakers
# ------------------------------------------------------------------

speakers_cmd = on_command(
    "speakers", aliases={"声源列表", "voicevox_speakers"}, priority=5
)


@speakers_cmd.handle()
async def handle_speakers():
    try:
        data = await client.get_speakers()
    except VoiceVoxError as e:
        await speakers_cmd.finish(f"获取声源失败: {e}")
    except Exception:
        logger.exception("Failed to reach VOICEVOX engine")
        await speakers_cmd.finish(
            f"无法连接到 VOICEVOX 引擎，请确认引擎已启动 "
            f"({plugin_config.voicevox_api_url})"
        )

    if not data:
        await speakers_cmd.finish("未找到可用声源")

    lines = ["可用声源:"]
    for spk in data:
        name = spk.get("name", "unknown")
        lines.append(f"\n【{name}】")
        for style in spk.get("styles", []):
            style_name = style.get("name", "unknown")
            style_id = style.get("id", "?")
            lines.append(f"  {style_id} — {style_name}")

    await speakers_cmd.finish("\n".join(lines))


# ------------------------------------------------------------------
# 2.    /tts  —  text to speech
# ------------------------------------------------------------------
tts_cmd = on_command("tts", aliases={"语音合成"}, priority=5)


@tts_cmd.handle()
async def handle_tts(args: Message = CommandArg()):
    text = args.extract_plain_text().strip()
    if not text:
        await tts_cmd.finish(
            "用法: /tts <speaker_id> <文本>\n"
            "示例: /tts 1 こんにちは\n"
            "先用 /speakers 查看可用声源 ID"
        )

    match = re.match(r"^(\d+)\s+(.+)$", text, re.DOTALL)
    if not match:
        await tts_cmd.finish(
            "格式错误！\n用法: /tts <speaker_id> <文本>\n示例: /tts 1 こんにちは"
        )

    speaker_id = int(match.group(1))
    text_to_speak = match.group(2).strip()

    await tts_cmd.send(f"正在用声源 {speaker_id} 合成语音...")

    try:
        wav = await client.tts(text_to_speak, speaker_id)
    except VoiceVoxError as e:
        await tts_cmd.finish(f"语音合成失败: {e}")
    except Exception:
        logger.exception("TTS failed")
        await tts_cmd.finish(
            f"语音合成失败，请确认 VOICEVOX 引擎已启动 "
            f"({plugin_config.voicevox_api_url})"
        )

    if not wav:
        await tts_cmd.finish("引擎返回了空的音频数据")

    # 调用我们的工具函数来处理音频发送
    await save_and_send_audio(tts_cmd, wav, speaker_id)


# ------------------------------------------------------------------
# 3.    /voicevox_status  —  check engine health
# ------------------------------------------------------------------
status_cmd = on_command("voicevox_status", aliases={"voicevox状态", "vvs"}, priority=5)


@status_cmd.handle()
async def handle_status():
    try:
        version = await client.get_version()
        msg = (
            f"VOICEVOX 引擎运行中\n"
            f"版本: {version}\n"
            f"地址: {plugin_config.voicevox_api_url}"
        )
    except VoiceVoxError as e:
        msg = f"VOICEVOX 引擎返回错误: {e}"
    except Exception:
        msg = (
            f"VOICEVOX 引擎未连接\n"
            f"地址: {plugin_config.voicevox_api_url}\n"
            "请确认引擎已启动"
        )
    await status_cmd.finish(msg)


# ------------------------------------------------------------------
# 4.    /voicevox_points  —  [tts.quest专用] 查看剩余API积分
# ------------------------------------------------------------------

points_cmd = on_command(
    "voicevox_points", aliases={"apilimit", "voicevox_points"}, priority=5
)


@points_cmd.handle()
async def handle_points():
    if not getattr(client, "is_tts_quest", False):
        await points_cmd.finish("当前正在使用本地 VOICEVOX 引擎，无需消耗积分。")

    try:
        data = await client.get_api_points()
    except Exception as e:
        logger.error(f"获取 tts.quest API 积分失败: {e}")
        await points_cmd.finish(f"积分获取失败: {e}")

    points = data.get("points", "未知")
    await points_cmd.finish(
        f"tts.quest 剩余积分:\n"
        f"当前剩余 API 积分: {points} pt\n"
        f"积分计算公式: 1500 + 100 x (UTF-8文字数)\n"
        f"大约可合成 {points // 4500 if isinstance(points, int) else '未知'} "
        f"条语音(30字)"
    )


# ------------------------------------------------------------------
# 5.    /ttshelp  —  显示详细帮助与用法示例
# ------------------------------------------------------------------

tts_help_cmd = on_command("ttshelp", aliases={"tts帮助", "voicevox_help"}, priority=5)


@tts_help_cmd.handle()
async def handle_tts_help():
    help_text = (
        "===== VOICEVOX BRIDGE 使用帮助 =====\n\n"
        "查看声源：/speakers (或 /声源列表)\n"
        "   获取所有可用角色的数字 ID 和音色风格。\n\n"
        "语音合成：/tts <声源ID> <文本> (或 /语音合成)\n"
        "   示例：/tts 1 こんにちは\n"
        "   示例：/tts 2 hello\n\n"
        "状态检查：/voicevox_status (或 /vvs)\n"
        "   检查后端本地引擎或 Web API 是否正常连通。\n\n"
        "点数查询：/apilimit (或 /voicevox_points)\n"
        "   仅在 Web API (tts.quest) 模式下有效，查看今日剩余额度。\n\n"
        "【使用提示】\n"
        "• 请确保 /tts 后的第一个参数是【数字ID】，且与后面的文本之间有【空格】隔开。\n"
        "• 如果合成失败，请联系管理员确认后台引擎是否已正常启动。"
    )
    await tts_help_cmd.finish(help_text)
