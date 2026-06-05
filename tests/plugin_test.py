"""
VOICEVOX 插件命令测试
"""

from unittest.mock import AsyncMock, patch

import pytest
import nonebot
from nonebug import App
from nonebot.adapters.onebot.v11 import Bot, Message
from nonebot.adapters.onebot.v11 import Adapter as OneBotV11Adapter


@pytest.fixture(scope="module", autouse=True)
def load_adapters():
    """确保在测试开始前加载 OneBot V11 适配器"""
    driver = nonebot.get_driver()
    driver.register_adapter(OneBotV11Adapter)
    # 从 pyproject.toml 加载插件（你的插件应该已经配置在 tool.nonebot.plugins 中）
    nonebot.load_from_toml("pyproject.toml")


@pytest.fixture
def mock_voicevox_client():
    """
    模拟 VoiceVoxClient，避免真实网络请求
    注意：需要在命令处理器导入 client 之前替换
    """
    with patch("nonebot_plugin_voicevox_bridge.commands.VoiceVoxClient") as MockClient:
        mock_instance = AsyncMock()

        # 模拟 get_speakers 返回值
        mock_instance.get_speakers.return_value = [
            {
                "name": "测试声源A",
                "styles": [
                    {"id": 1, "name": "风格1"},
                    {"id": 2, "name": "风格2"},
                ],
            },
            {
                "name": "测试声源B",
                "styles": [
                    {"id": 3, "name": "风格3"},
                ],
            },
        ]

        # 模拟 tts 返回假音频数据
        mock_instance.tts.return_value = b"fake_wav_data"

        # 模拟 get_version 返回值
        mock_instance.get_version.return_value = "test-version-0.0.1"

        # 模拟 get_api_points 返回值
        mock_instance.get_api_points.return_value = {"points": 12345}

        # 模拟 is_tts_quest 属性（用于 points 命令）
        mock_instance.is_tts_quest = True  # 默认 Web 模式，用于测试 points

        MockClient.return_value = mock_instance
        yield mock_instance


# ------------------------------------------------------------
# 测试 /speakers 命令
# ------------------------------------------------------------
@pytest.mark.asyncio
async def test_speakers_command(app: App, mock_voicevox_client):
    """测试 speakers 命令能正确返回声源列表"""
    from nonebot_plugin_voicevox_bridge.commands import speakers_cmd

    async with app.test_matcher(speakers_cmd) as ctx:
        bot = ctx.create_bot(base=Bot, adapter=OneBotV11Adapter)
        event = ctx.create_group_message_event(message="/speakers")
        ctx.receive_event(bot, event)

        # 预期回复内容
        expected_lines = [
            "可用声源:",
            "\n【测试声源A】",
            "  1 — 风格1",
            "  2 — 风格2",
            "\n【测试声源B】",
            "  3 — 风格3",
        ]
        expected_text = "\n".join(expected_lines)

        ctx.should_finished(Message(expected_text))


# ------------------------------------------------------------
# 测试 /tts 命令
# ------------------------------------------------------------
@pytest.mark.asyncio
async def test_tts_command_success(app: App, mock_voicevox_client):
    """测试 tts 命令能正确合成语音并调用保存函数"""
    from nonebot_plugin_voicevox_bridge.commands import tts_cmd

    # 模拟 save_and_send_audio 函数，避免文件操作
    with patch(
        "nonebot_plugin_voicevox_bridge.commands.save_and_send_audio", new=AsyncMock()
    ) as mock_save:
        async with app.test_matcher(tts_cmd) as ctx:
            bot = ctx.create_bot(base=Bot, adapter=OneBotV11Adapter)
            # 发送正确格式的命令：/tts 1 こんにちは
            event = ctx.create_group_message_event(message="/tts 1 こんにちは")
            ctx.receive_event(bot, event)

            # 验证 client.tts 被正确调用
            mock_voicevox_client.return_value.tts.assert_awaited_with("こんにちは", 1)

            # 验证 save_and_send_audio 被调用了一次，并且传入了正确的参数
            mock_save.assert_awaited_once()
            # 检查第一个参数是 matcher（tts_cmd 实例），
            # 第二个是音频数据，第三个是 speaker_id
            args, _ = mock_save.await_args
            assert args[0] is tts_cmd
            assert args[1] == b"fake_wav_data"
            assert args[2] == 1

            ctx.should_finished()


@pytest.mark.asyncio
async def test_tts_command_invalid_speaker_id(app: App, mock_voicevox_client):
    """测试 tts 命令传入非数字 speaker_id 时应报错"""
    from nonebot_plugin_voicevox_bridge.commands import tts_cmd

    async with app.test_matcher(tts_cmd) as ctx:
        bot = ctx.create_bot(base=Bot, adapter=OneBotV11Adapter)
        event = ctx.create_group_message_event(message="/tts abc こんにちは")
        ctx.receive_event(bot, event)

        ctx.should_finished(
            Message("speaker_id 必须是数字，请用 /speakers 查看可用 ID")
        )


@pytest.mark.asyncio
async def test_tts_command_missing_text(app: App, mock_voicevox_client):
    """测试 tts 命令缺少文本参数时应报错"""
    from nonebot_plugin_voicevox_bridge.commands import tts_cmd

    async with app.test_matcher(tts_cmd) as ctx:
        bot = ctx.create_bot(base=Bot, adapter=OneBotV11Adapter)
        event = ctx.create_group_message_event(message="/tts 1")
        ctx.receive_event(bot, event)

        expected_msg = "用法: tts <speaker_id> <文本>\n示例: tts 1 こんにちは"
        ctx.should_finished(Message(expected_msg))


# ------------------------------------------------------------
# 测试 /voicevox_status 命令
# ------------------------------------------------------------
@pytest.mark.asyncio
async def test_status_command(app: App, mock_voicevox_client):
    """测试 status 命令能正确返回引擎版本和地址"""
    from nonebot_plugin_voicevox_bridge.config import plugin_config
    from nonebot_plugin_voicevox_bridge.commands import status_cmd

    async with app.test_matcher(status_cmd) as ctx:
        bot = ctx.create_bot(base=Bot, adapter=OneBotV11Adapter)
        event = ctx.create_group_message_event(message="/voicevox_status")
        ctx.receive_event(bot, event)

        expected_msg = (
            f"VOICEVOX 引擎运行中\n"
            f"版本: test-version-0.0.1\n"
            f"地址: {plugin_config.voicevox_api_url}"
        )
        ctx.should_finished(Message(expected_msg))


# ------------------------------------------------------------
# 测试 /voicevox_points 命令（Web 模式）
# ------------------------------------------------------------
@pytest.mark.asyncio
async def test_points_command_web_mode(app: App, mock_voicevox_client):
    """测试 points 命令在 Web 模式下能返回积分信息"""
    from nonebot_plugin_voicevox_bridge.commands import points_cmd

    # 确保模拟的 client 被认为是 tts.quest 模式
    mock_voicevox_client.return_value.is_tts_quest = True

    async with app.test_matcher(points_cmd) as ctx:
        bot = ctx.create_bot(base=Bot, adapter=OneBotV11Adapter)
        event = ctx.create_group_message_event(message="/apilimit")
        ctx.receive_event(bot, event)

        expected_msg = (
            "tts.quest 剩余积分:\n"
            "当前剩余 API 积分: 12345 pt\n"
            "积分计算公式: 1500 + 100 x (UTF-8文字数)"
        )
        ctx.should_finished(Message(expected_msg))


@pytest.mark.asyncio
async def test_points_command_local_mode(app: App, mock_voicevox_client):
    """测试 points 命令在本地引擎模式下应提示无需积分"""
    from nonebot_plugin_voicevox_bridge.commands import points_cmd

    # 设置模拟的 client 为本地模式
    mock_voicevox_client.return_value.is_tts_quest = False

    async with app.test_matcher(points_cmd) as ctx:
        bot = ctx.create_bot(base=Bot, adapter=OneBotV11Adapter)
        event = ctx.create_group_message_event(message="/apilimit")
        ctx.receive_event(bot, event)

        ctx.should_finished(Message("当前正在使用本地 VOICEVOX 引擎，无需消耗积分。"))
