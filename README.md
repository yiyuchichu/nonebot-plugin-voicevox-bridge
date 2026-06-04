<div align="center">
    <a href="https://v2.nonebot.dev/store">
    <img src="https://raw.githubusercontent.com/fllesser/nonebot-plugin-template/refs/heads/resource/.docs/NoneBotPlugin.svg" width="310" alt="logo"></a>

## ✨ nonebot-plugin-voicevox-bridge ✨
[![LICENSE](https://img.shields.io/github/license/yiyuchichu/nonebot-plugin-voicevox-bridge.svg)](./LICENSE)
[![pypi](https://img.shields.io/pypi/v/nonebot-plugin-voicevox-bridge.svg)](https://pypi.python.org/pypi/nonebot-plugin-voicevox-bridge)
[![python](https://img.shields.io/badge/python-3.10|3.11|3.12|3.13-blue.svg)](https://www.python.org)
[![uv](https://img.shields.io/badge/package%20manager-uv-black?style=flat-square&logo=uv)](https://github.com/astral-sh/uv)
<br/>
[![ruff](https://img.shields.io/badge/code%20style-ruff-black?style=flat-square&logo=ruff)](https://github.com/astral-sh/ruff)
[![pre-commit](https://results.pre-commit.ci/badge/github/yiyuchichu/nonebot-plugin-voicevox-bridge/master.svg)](https://results.pre-commit.ci/latest/github/yiyuchichu/nonebot-plugin-voicevox-bridge/master)

</div>

## 📖 介绍

本插件基于VOICEVOX的API进行语音合成并通过OneBot v11协议进行通讯。本插件可以通过本地部署[VOICEVOX ENGINE](https://github.com/VOICEVOX/voicevox_engine)并监听其端口实现本地合成语音并转发，也可以通过[WEB版VOICEVOX API（高速）](https://voicevox.su-shiki.com/su-shikiapis/)提供的API进行语音的转发。一般来说VOICEVOX可以处理日语和英语的文本。

## 💿 安装

<details open>
<summary>使用 nb-cli 安装</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

    nb plugin install nonebot-plugin-voicevox-bridge --upgrade
使用 **pypi** 源安装

    nb plugin install nonebot-plugin-voicevox-bridge --upgrade -i "https://pypi.org/simple"
使用**清华源**安装

    nb plugin install nonebot-plugin-voicevox-bridge --upgrade -i "https://pypi.tuna.tsinghua.edu.cn/simple"


</details>

<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令

<details open>
<summary>uv</summary>

    uv add nonebot-plugin-voicevox-bridge
安装仓库 master 分支

    uv add git+https://github.com/yiyuchichu/nonebot-plugin-voicevox-bridge@master
</details>

<details>
<summary>pdm</summary>

    pdm add nonebot-plugin-voicevox-bridge
安装仓库 master 分支

    pdm add git+https://github.com/yiyuchichu/nonebot-plugin-voicevox-bridge@master
</details>
<details>
<summary>poetry</summary>

    poetry add nonebot-plugin-voicevox-bridge
安装仓库 master 分支

    poetry add git+https://github.com/yiyuchichu/nonebot-plugin-voicevox-bridge@master
</details>

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分追加写入

    plugins = ["nonebot_plugin_voicevox_bridge"]

</details>

<details>
<summary>使用 nbr 安装(使用 uv 管理依赖可用)</summary>

[nbr](https://github.com/fllesser/nbr) 是一个基于 uv 的 nb-cli，可以方便地管理 nonebot2

    nbr plugin install nonebot-plugin-voicevox-bridge
使用 **pypi** 源安装

    nbr plugin install nonebot-plugin-voicevox-bridge -i "https://pypi.org/simple"
使用**清华源**安装

    nbr plugin install nonebot-plugin-voicevox-bridge -i "https://pypi.tuna.tsinghua.edu.cn/simple"

</details>


## ⚙️ 配置

在 nonebot2 项目的`.env`文件中添加下表中的必填配置

| 配置项  | 必填  | 默认值 |   说明   |
| :-----: | :---: | :----: | :------: |
| VOICEVOX_API_URL |  是   |   https://deprecatedapis.tts.quest/v2/voicevox   | 需要本地引擎请使用 http://127.0.0.1:50021 |
| VOICEVOX_TIMEOUT |  是   |   30.0   | 可酌情修改 |
| VOICEVOX_API_KEY |  否   |   无   | 从[这里](https://voicevox.su-shiki.com/su-shikiapis/)获取，需要谷歌账号 | 

## 🎉 使用
### 指令表
| 指令  | 权限  | 需要@ | 范围  |   说明   |
| :---: | :---: | :---: | :---: | :------: |
| /tts <speaker_id> <text> | 群员  |  否   | 全部  | 进行语音合成，speaker_id可通过/speakers获取 |
| /speakers | 群员  |  否   | 全部  | 获取音源列表 |
| /voicevox_status | 群员  |  否   | 全部  | 检查引擎状态 |
| /apilimit | 群员  |  否   | 全部  | 检查api点数(仅限tts.quest) |

### 备注
- APIKEY获取：https://voicevox.su-shiki.com/su-shikiapis/ 以及 https://su-shiki.com/api/
- 积分规则：1500 + 100 x (UTF-8文字数)，每24h重置10,000,000积分。[该网站](https://voicevox.su-shiki.com/su-shikiapis/ttsquest/)也提供了不需要APIKEY的低速API，可按需取用（不过高速的限额其实也很高啦）
- 本插件是我一时兴起的成过，受[nonebot-plugin-just-enough-katakanas](https://github.com/p0rt39/nonebot-plugin-just-enough-katakanas)启发，~~认为片假名需要念出来才能发挥其威力~~，不过实际上配合效果不太好。这是我的第一个Nonebot插件(难说会不会有下一个)，作为计算机小白，代码撰写几乎全部由AI代劳，出发点是自用，功能较少，也难免会出现没有发现的bug，维护恐怕也很难持续，敬请谅解。

## VOICEVOX 声源列表（Web API 返回，供参考）

| 角色名 | Style ID | 风格名称 |
|--------|----------|----------|
| **四国めたん** | 2 | ノーマル |
| | 0 | あまあま |
| | 6 | ツンツン |
| | 4 | セクシー |
| | 36 | ささやき |
| | 37 | ヒソヒソ |
| **ずんだもん** | 3 | ノーマル |
| | 1 | あまあま |
| | 7 | ツンツン |
| | 5 | セクシー |
| | 22 | ささやき |
| | 38 | ヒソヒソ |
| | 75 | ヘロヘロ |
| | 76 | なみだめ |
| **春日部つむぎ** | 8 | ノーマル |
| **雨晴はう** | 10 | ノーマル |
| **波音リツ** | 9 | ノーマル |
| | 65 | クイーン |
| **玄野武宏** | 11 | ノーマル |
| | 39 | 喜び |
| | 40 | ツンギレ |
| | 41 | 悲しみ |
| **白上虎太郎** | 12 | ふつう |
| | 32 | わーい |
| | 33 | びくびく |
| | 34 | おこ |
| | 35 | びえーん |
| **青山龍星** | 13 | ノーマル |
| | 81 | 熱血 |
| | 82 | 不機嫌 |
| | 83 | 喜び |
| | 84 | しっとり |
| | 85 | かなしみ |
| | 86 | 囁き |
| **冥鳴ひまり** | 14 | ノーマル |
| **九州そら** | 16 | ノーマル |
| | 15 | あまあま |
| | 18 | ツンツン |
| | 17 | セクシー |
| | 19 | ささやき |
| **もち子さん** | 20 | ノーマル |
| | 66 | セクシー／あん子 |
| | 77 | 泣き |
| | 78 | 怒り |
| | 79 | 喜び |
| | 80 | のんびり |
| **剣崎雌雄** | 21 | ノーマル |
| **WhiteCUL** | 23 | ノーマル |
| | 24 | たのしい |
| | 25 | かなしい |
| | 26 | びえーん |
| **後鬼** | 27 | 人間ver. |
| | 28 | ぬいぐるみver. |
| | 87 | 人間（怒り）ver. |
| | 88 | 鬼ver. |
| **No.7** | 29 | ノーマル |
| | 30 | アナウンス |
| | 31 | 読み聞かせ |
| **ちび式じい** | 42 | ノーマル |
| **櫻歌ミコ** | 43 | ノーマル |
| | 44 | 第二形態 |
| | 45 | ロリ |
| **小夜/SAYO** | 46 | ノーマル |
| **ナースロボ＿タイプＴ** | 47 | ノーマル |
| | 48 | 楽々 |
| | 49 | 恐怖 |
| | 50 | 内緒話 |
| **†聖騎士 紅桜†** | 51 | ノーマル |
| **雀松朱司** | 52 | ノーマル |
| **麒ヶ島宗麟** | 53 | ノーマル |
| **春歌ナナ** | 54 | ノーマル |
| **猫使アル** | 55 | ノーマル |
| | 56 | おちつき |
| | 57 | うきうき |
| | 110 | つよつよ |
| | 111 | へろへろ |
| **猫使ビィ** | 58 | ノーマル |
| | 59 | おちつき |
| | 60 | 人見知り |
| | 112 | つよつよ |
| **中国うさぎ** | 61 | ノーマル |
| | 62 | おどろき |
| | 63 | こわがり |
| | 64 | へろへろ |
| **栗田まろん** | 67 | ノーマル |
| **あいえるたん** | 68 | ノーマル |
| **満別花丸** | 69 | ノーマル |
| | 70 | 元気 |
| | 71 | ささやき |
| | 72 | ぶりっ子 |
| | 73 | ボーイ |
| **琴詠ニア** | 74 | ノーマル |
| **Voidoll** | 89 | ノーマル |
| **ぞん子** | 90 | ノーマル |
| | 91 | 低血圧 |
| | 92 | 覚醒 |
| | 93 | 実況風 |
| **中部つるぎ** | 94 | ノーマル |
| | 95 | 怒り |
| | 96 | ヒソヒソ |
| | 97 | おどおど |
| | 98 | 絶望と敗北 |
| **離途** | 99 | ノーマル |
| | 101 | シリアス |
| **黒沢冴白** | 100 | ノーマル |
| **ユーレイちゃん** | 102 | ノーマル |
| | 103 | 甘々 |
| | 104 | 哀しみ |
| | 105 | ささやき |
| | 106 | ツクモちゃん |
| **東北ずん子** | 107 | ノーマル |
| **東北きりたん** | 108 | ノーマル |
| **東北イタコ** | 109 | ノーマル |
| **あんこもん** | 113 | ノーマル |
| | 114 | つよつよ |
| | 115 | よわよわ |
| | 116 | けだるげ |
| | 117 | ささやき |