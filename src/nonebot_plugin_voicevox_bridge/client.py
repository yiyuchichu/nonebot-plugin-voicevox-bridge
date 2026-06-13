from typing import Any

import httpx


class VoiceVoxError(Exception):
    """VOICEVOX Engine API error."""


class VoiceVoxClient:
    """Async HTTP client supporting both local VOICEVOX Engine and tts.quest Web API.

    Default engine address: http://127.0.0.1:50021
    tts.quest address: https://deprecatedapis.tts.quest/v2/voicevox
    """

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:50021",
        timeout: float = 30.0,
        api_key: str | None = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.api_key = api_key
        self.is_tts_quest = "tts.quest" in self.base_url

        # 实例化一个持久的客户端供全局复用
        self.http_client = httpx.AsyncClient(timeout=self.timeout)

    async def close(self):
        """关闭 HTTP 客户端，建议在 on_shutdown 钩子中调用"""
        await self.http_client.aclose()

    # ------------------------------------------------------------------
    # internal helpers
    # ------------------------------------------------------------------

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        url = f"{self.base_url}{path}"

        if self.is_tts_quest:
            if params is None:
                params = {}
            if self.api_key:
                params["key"] = self.api_key

        # 【核心修改】复用 self.http_client，移除 async with 新建实例的逻辑
        resp = await self.http_client.request(
            method, url, params=params, json=json, headers=headers
        )

        if self.is_tts_quest:
            if resp.status_code != 200:
                raise VoiceVoxError(f"HTTP Error ({resp.status_code}): {resp.text}")
            if resp.text in ["invalidApiKey", "failed", "notEnoughPoints"]:
                raise VoiceVoxError(f"tts.quest API Error: {resp.text}")
            return resp

        try:
            resp.raise_for_status()
        except httpx.HTTPStatusError as e:
            detail = resp.text
            raise VoiceVoxError(
                f"VOICEVOX API error ({resp.status_code}): {detail}"
            ) from e
        return resp

    # ------------------------------------------------------------------
    # core API – query creation
    # ------------------------------------------------------------------

    async def audio_query(
        self, text: str, speaker: int, *, core_version: str | None = None
    ) -> dict[str, Any]:
        """Create a synthesis query from text."""
        if self.is_tts_quest:
            return {"text": text, "speaker": speaker, "_is_tts_quest": True}

        params: dict[str, Any] = {"text": text, "speaker": speaker}
        if core_version is not None:
            params["core_version"] = core_version
        resp = await self._request("POST", "/audio_query", params=params)
        return resp.json()

    # ------------------------------------------------------------------
    # core API – synthesis
    # ------------------------------------------------------------------

    async def synthesis(self, speaker: int, query: dict[str, Any]) -> bytes:
        """Synthesise WAV audio from a query JSON."""
        if self.is_tts_quest and query.get("_is_tts_quest"):
            return await self.tts(query.get("text", ""), speaker)
        elif self.is_tts_quest:
            raise VoiceVoxError(
                "tts.quest Web API 无法直接处理本地化的 Query JSON 数据"
            )

        resp = await self._request(
            "POST",
            "/synthesis",
            params={"speaker": speaker},
            json=query,
            headers={"Accept": "audio/wav"},
        )
        return resp.content

    # ------------------------------------------------------------------
    # utility
    # ------------------------------------------------------------------

    async def get_version(self) -> str:
        if self.is_tts_quest:
            return "tts.quest v2 (Remote)"

        resp = await self._request("GET", "/version")
        return resp.json()

    async def get_speakers(self) -> list[dict[str, Any]]:
        path = "/speakers/" if self.is_tts_quest else "/speakers"
        resp = await self._request("GET", path)
        return resp.json()

    async def is_ready(self) -> bool:
        """Return True if the engine is reachable."""
        try:
            if self.is_tts_quest:
                await self.get_speakers()
            else:
                await self.get_version()
            return True
        except Exception:
            return False

    # ------------------------------------------------------------------
    # high-level convenience
    # ------------------------------------------------------------------

    async def tts(self, text: str, speaker: int) -> bytes:
        """Full TTS pipeline: text -> audio_query -> synthesis -> WAV bytes."""
        if self.is_tts_quest:
            params = {
                "text": text,
                "speaker": speaker,
            }
            resp = await self._request("GET", "/audio/", params=params)
            return resp.content
        else:
            query = await self.audio_query(text, speaker)
            return await self.synthesis(speaker, query)

    async def get_api_points(self) -> dict[str, Any]:
        """[仅用于tts.quest] 获取云端高效率 API 的剩余积分"""
        if not self.is_tts_quest:
            raise VoiceVoxError("积分查询功能仅在启用 tts.quest 模式时可用。")

        url = "https://deprecatedapis.tts.quest/v2/api/"
        params = {"key": self.api_key} if self.api_key else {}
        resp = await self.http_client.request("GET", url, params=params)

        if resp.status_code != 200:
            raise VoiceVoxError(f"无法获取积分数据 ({resp.status_code}): {resp.text}")
        return resp.json()
