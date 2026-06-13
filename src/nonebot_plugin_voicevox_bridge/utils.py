import base64

import aiofiles
import nonebot_plugin_localstore as store
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import MessageSegment

CACHE_DIR = store.get_plugin_cache_dir()


async def save_and_send_audio(matcher, wav_data: bytes, speaker_id: int):
    """保存音频文件并尝试发送。"""
    cache_file = CACHE_DIR / f"voicevox_tts_{speaker_id}.wav"
    async with aiofiles.open(cache_file, "wb") as f:
        await f.write(wav_data)
    try:
        await matcher.send(MessageSegment.record(file=cache_file.as_uri()))
    except Exception:
        logger.warning("通过 URI 发送语音失败，尝试 base64 降级...")
        try:
            b64 = base64.b64encode(wav_data).decode()
            await matcher.send(MessageSegment.record(file=f"base64://{b64}"))
        except Exception:
            logger.warning("当前平台不支持 OneBot 语音段，降级为文本提示")
            await matcher.send(
                f"[本地测试提示] 语音合成成功！\n"
                f"音频大小: {len(wav_data) / 1024:.1f} KB\n"
                f"暂存路径: {cache_file}"
            )
