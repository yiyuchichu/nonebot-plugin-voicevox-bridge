"""
VOICEVOX 插件命令测试
"""

from unittest.mock import AsyncMock, patch

import pytest
from fake import fake_group_message_event_v11
from nonebug import App
from nonebot.adapters.onebot.v11 import Bot


@pytest.fixture
def mock_client():
    """模拟 commands 模块中的全局 client 实例"""
    import nonebot_plugin_voicevox_bridge.commands as commands

    with patch.object(commands, "client", autospec=True) as mock_client:
        mock_client.is_tts_quest = True
        mock_client.get_speakers = AsyncMock(
            return_value=[
                {
                    "name": "测试声源A",
                    "styles": [{"id": 1, "name": "风格1"}, {"id": 2, "name": "风格2"}],
                },
                {"name": "测试声源B", "styles": [{"id": 3, "name": "风格3"}]},
            ]
        )
        mock_client.tts = AsyncMock(return_value=b"fake_wav_data")
        mock_client.get_version = AsyncMock(return_value="test-version-0.0.1")
        mock_client.get_api_points = AsyncMock(return_value={"points": 12345})
        yield mock_client


# ------------------------------------------------------------
# 测试 /speakers 命令
# ------------------------------------------------------------
@pytest.mark.asyncio
async def test_speakers_command(app: App, mock_client):
    from nonebot_plugin_voicevox_bridge.commands import speakers_cmd

    async with app.test_matcher(speakers_cmd) as ctx:
        bot = ctx.create_bot(base=Bot)
        event = fake_group_message_event_v11(message="/speakers")
        ctx.receive_event(bot, event)

        expected_lines = [
            "可用声源:",
            "\n【测试声源A】",
            "  1 — 风格1",
            "  2 — 风格2",
            "\n【测试声源B】",
            "  3 — 风格3",
        ]
        expected_text = "\n".join(expected_lines)
        ctx.should_call_send(event, expected_text, result=None, bot=bot)
        ctx.should_finished()


# ------------------------------------------------------------
# 测试 /tts 命令
# ------------------------------------------------------------
@pytest.mark.asyncio
async def test_tts_command_invalid_speaker_id(app: App, mock_client):
    from nonebot_plugin_voicevox_bridge.commands import tts_cmd

    async with app.test_matcher(tts_cmd) as ctx:
        bot = ctx.create_bot(base=Bot)
        event = fake_group_message_event_v11(message="/tts abc こんにちは")
        ctx.receive_event(bot, event)

        expected_msg = (
            "格式错误！\n用法: /tts <speaker_id> <文本>\n示例: /tts 1 こんにちは"
        )
        ctx.should_call_send(event, expected_msg, result=None, bot=bot)
        ctx.should_finished()


@pytest.mark.asyncio
async def test_tts_command_missing_text(app: App, mock_client):
    from nonebot_plugin_voicevox_bridge.commands import tts_cmd

    async with app.test_matcher(tts_cmd) as ctx:
        bot = ctx.create_bot(base=Bot)
        event = fake_group_message_event_v11(message="/tts 1")
        ctx.receive_event(bot, event)

        # 适配实际代码输出
        expected_msg = (
            "格式错误！\n用法: /tts <speaker_id> <文本>\n示例: /tts 1 こんにちは"
        )
        ctx.should_call_send(event, expected_msg, result=None, bot=bot)
        ctx.should_finished()


@pytest.mark.asyncio
async def test_tts_command_empty_args(app: App, mock_client):
    from nonebot_plugin_voicevox_bridge.commands import tts_cmd

    async with app.test_matcher(tts_cmd) as ctx:
        bot = ctx.create_bot(base=Bot)
        event = fake_group_message_event_v11(message="/tts")
        ctx.receive_event(bot, event)

        # 适配实际代码输出（此处没有“格式错误！”前缀）
        expected_msg = (
            "用法: /tts <speaker_id> <文本>\n"
            "示例: /tts 1 こんにちは\n"
            "先用 /speakers 查看可用声源 ID"
        )
        ctx.should_call_send(event, expected_msg, result=None, bot=bot)
        ctx.should_finished()


# ------------------------------------------------------------
# 测试 /voicevox_status 命令
# ------------------------------------------------------------
@pytest.mark.asyncio
async def test_status_command(app: App, mock_client):
    from nonebot_plugin_voicevox_bridge.commands import status_cmd, plugin_config

    async with app.test_matcher(status_cmd) as ctx:
        bot = ctx.create_bot(base=Bot)
        event = fake_group_message_event_v11(message="/voicevox_status")
        ctx.receive_event(bot, event)

        expected_msg = (
            f"VOICEVOX 引擎运行中\n"
            f"版本: test-version-0.0.1\n"
            f"地址: {plugin_config.voicevox_api_url}"
        )
        ctx.should_call_send(event, expected_msg, result=None, bot=bot)
        ctx.should_finished()


# ------------------------------------------------------------
# 测试 /voicevox_points 命令
# ------------------------------------------------------------
@pytest.mark.asyncio
async def test_points_command_web_mode(app: App, mock_client):
    from nonebot_plugin_voicevox_bridge.commands import points_cmd

    mock_client.is_tts_quest = True

    async with app.test_matcher(points_cmd) as ctx:
        bot = ctx.create_bot(base=Bot)
        event = fake_group_message_event_v11(message="/apilimit")
        ctx.receive_event(bot, event)

        expected_msg = (
            "tts.quest 剩余积分:\n"
            "当前剩余 API 积分: 12345 pt\n"
            "积分计算公式: 1500 + 100 x (UTF-8文字数)\n"
            "大约可合成 2 条语音(30字)"
        )
        ctx.should_call_send(event, expected_msg, result=None, bot=bot)
        ctx.should_finished()


@pytest.mark.asyncio
async def test_points_command_local_mode(app: App, mock_client):
    from nonebot_plugin_voicevox_bridge.commands import points_cmd

    mock_client.is_tts_quest = False

    async with app.test_matcher(points_cmd) as ctx:
        bot = ctx.create_bot(base=Bot)
        event = fake_group_message_event_v11(message="/apilimit")
        ctx.receive_event(bot, event)

        ctx.should_call_send(
            event,
            "当前正在使用本地 VOICEVOX 引擎，无需消耗积分。",
            result=None,
            bot=bot,
        )
        ctx.should_finished()
