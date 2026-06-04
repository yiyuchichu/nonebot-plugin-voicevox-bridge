import base64
import os
import tempfile
from pathlib import Path

from nonebot import on_command, get_plugin_config
from nonebot.adapters.onebot.v11 import MessageSegment, Message
from nonebot.exception import MatcherException
from nonebot.log import logger
from nonebot.params import CommandArg

from .client import VoiceVoxClient, VoiceVoxError
from .config import Config, plugin_config
from .utils import save_and_send_audio


# ------------------------------------------------------------------
# configuration
# ------------------------------------------------------------------

# 配置依然可以在这里获取，或者通过依赖注入
plugin_config = get_plugin_config(Config)

client = VoiceVoxClient(
    base_url=plugin_config.voicevox_api_url,
    timeout=plugin_config.voicevox_timeout,
    api_key=plugin_config.voicevox_api_key,
)

# ------------------------------------------------------------------
# 1.    /speakers  —  list available speakers
# ------------------------------------------------------------------

speakers_cmd = on_command("speakers", aliases={"声源列表", "voicevox_speakers"}, priority=5)

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
            "用法: tts <speaker_id> <文本>\n"
            "示例: tts 1 こんにちは\n"
            "先用 /speakers 查看可用声源 ID"
        )

    parts = text.split(maxsplit=1)
    if len(parts) < 2:
        await tts_cmd.finish(
            "用法: tts <speaker_id> <文本>\n示例: tts 1 こんにちは"
        )

    try:
        speaker_id = int(parts[0])
    except ValueError:
        await tts_cmd.finish("speaker_id 必须是数字，请用 /speakers 查看可用 ID")

    text_to_speak = parts[1]

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
        msg = f"VOICEVOX 引擎运行中\n版本: {version}\n地址: {plugin_config.voicevox_api_url}"
    except VoiceVoxError as e:
        msg = f"VOICEVOX 引擎返回错误: {e}"
    except Exception:
        msg = f"VOICEVOX 引擎未连接\n地址: {plugin_config.voicevox_api_url}\n请确认引擎已启动"
    await status_cmd.finish(msg)

# ------------------------------------------------------------------
# 4.    /voicevox_points  —  [tts.quest专用] 查看剩余API积分
# ------------------------------------------------------------------

points_cmd = on_command(
    "voicevox_points",
    aliases={"apilimit", "voicevox_points"},
    priority=5
)

@points_cmd.handle()
async def handle_points():
    if not getattr(client, "is_tts_quest", False):
        await points_cmd.finish("当前正在使用本地 VOICEVOX 引擎，无需消耗积分。")

    msg = ""
    try:
        data = await client.get_api_points()
        points = data.get("points", "未知")
        await points_cmd.finish(
            f"tts.quest 剩余积分:\n"
            f"当前剩余 API 积分: {points} pt\n"
            f"积分计算公式: 1500 + 100 x (UTF-8文字数)\n"
            f"大约可合成 {points // 4500} 条语音(30字)"
        )
    except MatcherException:
        raise  # 让 NoneBot 正常结束事件
    except Exception as e:
        logger.error(f"获取 tts.quest API 积分失败: {e}")
        await points_cmd.finish(f"积分获取失败: {e}")