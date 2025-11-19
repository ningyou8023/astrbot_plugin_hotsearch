import asyncio
import aiohttp
import tempfile
import os
from pathlib import Path

from astrbot.api import AstrBotConfig, logger
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star, register

PLUGIN_DATA_DIR = Path("data", "plugins_data", "astrbot_hotsearch")
PLUGIN_DATA_DIR.mkdir(parents=True, exist_ok=True)

@register(
    "astrbot_hotsearch",
    "柠柚",
    "实时热搜聚合，支持抖音/小红书/知乎/微博/百度/懂车帝/哔哩哔哩/腾讯/头条/猫眼票房，输出图片或文本",
    "1.0.0",
)
class HotSearchPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context, config)
        self.douyin_api = getattr(config, "douyin_api", "https://api.nycnm.cn/API/douyinrs.php")
        self.xhs_api = getattr(config, "xhs_api", "https://api.nycnm.cn/API/xhsrs.php")
        self.zhihu_api = getattr(config, "zhihu_api", "https://api.nycnm.cn/API/zhihu.php")
        self.weibo_api = getattr(config, "weibo_api", "https://api.nycnm.cn/API/wb.php")
        self.baidu_api = getattr(config, "baidu_api", "https://api.nycnm.cn/API/baidu.php")
        self.dcd_api = getattr(config, "dcd_api", "https://api.nycnm.cn/API/dongchedi.php")
        self.bilibili_api = getattr(config, "bilibili_api", "https://api.nycnm.cn/API/bilibilirs.php")
        self.toutiao_api = getattr(config, "toutiao_api", "https://api.nycnm.cn/API/toutiao.php")
        self.maoyan_api = getattr(config, "maoyan_api", "https://api.nycnm.cn/API/maoyan.php")
        self.tencent_api = getattr(config, "tencent_api", "https://api.nycnm.cn/API/txxw.php")

        self.global_apikey = getattr(config, "api_key", "")
        self.enable_douyin = getattr(config, "enable_douyin", True)
        self.enable_xhs = getattr(config, "enable_xhs", True)
        self.enable_zhihu = getattr(config, "enable_zhihu", True)
        self.enable_weibo = getattr(config, "enable_weibo", True)
        self.enable_baidu = getattr(config, "enable_baidu", True)
        self.enable_dcd = getattr(config, "enable_dcd", True)
        self.enable_bilibili = getattr(config, "enable_bilibili", True)
        self.enable_toutiao = getattr(config, "enable_toutiao", True)
        self.enable_maoyan = getattr(config, "enable_maoyan", True)
        self.enable_tencent = getattr(config, "enable_tencent", True)
        self.douyin_format = getattr(config, "douyin_format", "image")
        self.xhs_format = getattr(config, "xhs_format", "image")
        self.zhihu_format = getattr(config, "zhihu_format", "image")
        self.weibo_format = getattr(config, "weibo_format", "image")
        self.baidu_format = getattr(config, "baidu_format", "image")
        self.baidu_type = getattr(config, "baidu_type", "hot")
        self.dcd_format = getattr(config, "dcd_format", "image")
        self.bilibili_format = getattr(config, "bilibili_format", "image")
        self.toutiao_format = getattr(config, "toutiao_format", "image")
        self.maoyan_format = getattr(config, "maoyan_format", "image")
        self.maoyan_type = getattr(config, "maoyan_type", "all")
        self.tencent_format = getattr(config, "tencent_format", "image")
        logger.info("实时热搜插件已初始化")

    async def _request_hotsearch(self, base_url: str, fmt: str, apikey: str, extra: dict | None = None, fmt_key: str = "format"):
        try:
            url = f"{base_url}?{fmt_key}={fmt}"
            if apikey:
                url += f"&apikey={apikey}"
            if extra:
                for k, v in extra.items():
                    if v is not None and v != "":
                        url += f"&{k}={v}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    ct = response.headers.get("Content-Type", "")
                    if fmt == "image" and response.status == 200:
                        data = await response.read()
                        suffix = ".png" if "png" in ct else ".jpg" if ("jpeg" in ct or "jpg" in ct) else ".img"
                        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
                        tmp.write(data)
                        tmp.close()
                        return {"image_path": tmp.name}
                    
                    if response.status == 200:
                        text = await response.text()
                        return {"text": text}
                    return None
        except asyncio.TimeoutError:
            return None
        except Exception as e:
            logger.error(f"请求热搜失败: {e}")
            return None

    async def _handle(self, event: AstrMessageEvent, base_url: str, fmt: str, enabled: bool, name: str, extra: dict | None = None, fmt_key: str = "format"):
        if not enabled:
            yield event.plain_result(f"❌ {name}热搜已关闭")
            return
        result = await self._request_hotsearch(base_url, fmt, self.global_apikey, extra, fmt_key=fmt_key)
        if not result:
            yield event.plain_result(f"❌ 获取{name}热搜失败，请稍后重试")
            return
        if result.get("image_path"):
            yield event.image_result(result["image_path"])
            try:
                os.unlink(result["image_path"])
            except Exception:
                pass
            return
        if result.get("text") is not None:
            yield event.plain_result(result["text"])
            return

    @filter.command("抖音热搜", alias={"抖音实时热搜", "抖音榜", "抖音热点", "抖音"})
    async def douyin(self, event: AstrMessageEvent):
        async for r in self._handle(event, self.douyin_api, self.douyin_format, self.enable_douyin, "抖音"):
            yield r

    @filter.command("小红书热搜", alias={"小红书实时热搜", "小红书榜", "小红书热点", "小红书"})
    async def xhs(self, event: AstrMessageEvent):
        async for r in self._handle(event, self.xhs_api, self.xhs_format, self.enable_xhs, "小红书"):
            yield r

    @filter.command("知乎热搜", alias={"知乎实时热搜", "知乎榜", "知乎热点", "知乎"})
    async def zhihu(self, event: AstrMessageEvent):
        async for r in self._handle(event, self.zhihu_api, self.zhihu_format, self.enable_zhihu, "知乎"):
            yield r

    @filter.command("微博热搜", alias={"微博榜", "微博热点", "微博"})
    async def weibo(self, event: AstrMessageEvent):
        async for r in self._handle(event, self.weibo_api, self.weibo_format, self.enable_weibo, "微博"):
            yield r

    @filter.command("百度热搜", alias={"百度榜", "百度热点", "百度"})
    async def baidu(self, event: AstrMessageEvent):
        text = event.get_message_str() or ""
        btype = self._pick_baidu_type(text)
        async for r in self._handle(event, self.baidu_api, self.baidu_format, self.enable_baidu, "百度", extra={"type": btype}):
            yield r

    @filter.command("懂车帝热搜", alias={"懂车帝榜", "懂车帝热点", "懂车帝"})
    async def dcd(self, event: AstrMessageEvent):
        async for r in self._handle(event, self.dcd_api, self.dcd_format, self.enable_dcd, "懂车帝"):
            yield r

    @filter.command("哔哩哔哩热搜", alias={"B站热搜", "B站榜", "哔哩哔哩", "B站"})
    async def bilibili(self, event: AstrMessageEvent):
        async for r in self._handle(event, self.bilibili_api, self.bilibili_format, self.enable_bilibili, "哔哩哔哩"):
            yield r

    @filter.command("头条热搜", alias={"今日头条热搜", "头条榜", "头条"})
    async def toutiao(self, event: AstrMessageEvent):
        async for r in self._handle(event, self.toutiao_api, self.toutiao_format, self.enable_toutiao, "头条"):
            yield r

    @filter.command("腾讯热搜", alias={"腾讯新闻热搜", "腾讯榜", "腾讯新闻", "腾讯"})
    async def tencent(self, event: AstrMessageEvent):
        async for r in self._handle(event, self.tencent_api, self.tencent_format, self.enable_tencent, "腾讯", fmt_key="type"):
            yield r

    @filter.command("猫眼票房", alias={"猫眼热搜", "猫眼榜", "猫眼"})
    async def maoyan(self, event: AstrMessageEvent):
        text = event.get_message_str() or ""
        mtype = self._pick_maoyan_type(text)
        async for r in self._handle(event, self.maoyan_api, self.maoyan_format, self.enable_maoyan, "猫眼", extra={"type": mtype}):
            yield r

    def _pick_baidu_type(self, text: str) -> str:
        t = text.lower()
        if ("贴吧" in text) or ("tieba" in t):
            return "tieba"
        if ("电视剧" in text) or ("剧集" in text) or ("teleplay" in t):
            return "teleplay"
        return "hot"

    def _pick_maoyan_type(self, text: str) -> str:
        tl = text.lower()
        if ("总榜" in text) or ("全球" in text) or ("all" in tl):
            return "all"
        if ("电影" in text) or ("票房" in text) or ("实时票房" in text) or ("movie" in tl):
            return "movie"
        if ("电视" in text) or ("收视率" in text) or ("tv" in tl):
            return "tv"
        if ("网剧" in text) or ("网播" in text) or ("网络剧" in text) or ("web" in tl):
            return "web"
        return "all"

    @filter.command("help_hotsearch", alias={"热搜帮助", "实时热搜帮助"})
    async def show_help(self, event: AstrMessageEvent):
        text = (
            "🔥 实时热搜插件\n\n"
            "【指令，无需参数】\n"
            "• 抖音热搜\n"
            "• 小红书热搜\n"
            "• 知乎热搜\n"
            "• 微博热搜\n"
            "• 百度热搜\n"
            "• 懂车帝热搜\n"
            "• 哔哩哔哩热搜\n"
            "• 腾讯热搜\n"
            "• 头条热搜\n"
            "• 猫眼票房\n\n"
            "各平台格式独立配置，可设置 text/image"
        )
        yield event.plain_result(text)

    async def terminate(self):
        logger.info("实时热搜插件已终止")