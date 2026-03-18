import asyncio
import aiohttp
import tempfile
import os
import datetime
import traceback
from pathlib import Path

from astrbot.api import AstrBotConfig, logger
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star, register
from astrbot.core.message.message_event_result import MessageChain

PLUGIN_DATA_DIR = Path("data", "plugins_data", "astrbot_hotsearch")
PLUGIN_DATA_DIR.mkdir(parents=True, exist_ok=True)

@register(
    "astrbot_hotsearch",
    "柠柚",
    "实时热搜聚合，支持抖音/小红书/知乎/微博/百度/懂车帝/哔哩哔哩/腾讯/头条/猫眼票房/夸克/豆瓣/36氪/51CTO/52破解/AcFun/CSDN/HelloGitHub/米游社/爱范儿/IT之家/掘金/网易新闻/新浪新闻/少数派/澎湃新闻/气象预警/微信读书/第一财经/游研社，输出图片或文本",
    "1.0.5",
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
        self.quark_api = getattr(config, "quark_api", "https://api.nycnm.cn/API/quark.php")
        self.douban_api = getattr(config, "douban_api", "https://api.nycnm.cn/API/douban.php")
        self.kr36_api = getattr(config, "kr36_api", "https://api.nycnm.cn/API/36kr.php")
        self.cto51_api = getattr(config, "cto51_api", "https://api.nycnm.cn/API/51cto.php")
        self.pojie52_api = getattr(config, "pojie52_api", "https://api.nycnm.cn/API/52pojie.php")
        self.acfun_api = getattr(config, "acfun_api", "https://api.nycnm.cn/API/acfun.php")
        self.csdn_api = getattr(config, "csdn_api", "https://api.nycnm.cn/API/csdn.php")
        self.hellogithub_api = getattr(config, "hellogithub_api", "https://api.nycnm.cn/API/hellogithub.php")
        self.miyoushe_api = getattr(config, "miyoushe_api", "https://api.nycnm.cn/API/miyoushe.php")
        self.ifanr_api = getattr(config, "ifanr_api", "https://api.nycnm.cn/API/ifanr.php")
        self.ithome_api = getattr(config, "ithome_api", "https://api.nycnm.cn/API/xijiayi.php")
        self.juejin_api = getattr(config, "juejin_api", "https://api.nycnm.cn/API/juejin.php")
        self.netease_api = getattr(config, "netease_api", "https://api.nycnm.cn/API/netease.php")
        self.sina_api = getattr(config, "sina_api", "https://api.nycnm.cn/API/sina.php")
        self.sspai_api = getattr(config, "sspai_api", "https://api.nycnm.cn/API/sspai.php")
        self.thepaper_api = getattr(config, "thepaper_api", "https://api.nycnm.cn/API/thepaper.php")
        self.weatheralarm_api = getattr(config, "weatheralarm_api", "https://api.nycnm.cn/API/weatheralarm.php")
        self.weread_api = getattr(config, "weread_api", "https://api.nycnm.cn/API/weread.php")
        self.yicai_api = getattr(config, "yicai_api", "https://api.nycnm.cn/API/yicai.php")
        self.yystv_api = getattr(config, "yystv_api", "https://api.nycnm.cn/API/yystv.php")

        self.global_apikey = getattr(config, "api_key", "")
        self.timeout = getattr(config, "timeout", 30)
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
        self.enable_quark = getattr(config, "enable_quark", True)
        self.enable_douban = getattr(config, "enable_douban", True)
        self.enable_kr36 = getattr(config, "enable_kr36", True)
        self.enable_cto51 = getattr(config, "enable_cto51", True)
        self.enable_pojie52 = getattr(config, "enable_pojie52", True)
        self.enable_acfun = getattr(config, "enable_acfun", True)
        self.enable_csdn = getattr(config, "enable_csdn", True)
        self.enable_hellogithub = getattr(config, "enable_hellogithub", True)
        self.enable_miyoushe = getattr(config, "enable_miyoushe", True)
        self.enable_ifanr = getattr(config, "enable_ifanr", True)
        self.enable_ithome = getattr(config, "enable_ithome", True)
        self.enable_juejin = getattr(config, "enable_juejin", True)
        self.enable_netease = getattr(config, "enable_netease", True)
        self.enable_sina = getattr(config, "enable_sina", True)
        self.enable_sspai = getattr(config, "enable_sspai", True)
        self.enable_thepaper = getattr(config, "enable_thepaper", True)
        self.enable_weatheralarm = getattr(config, "enable_weatheralarm", True)
        self.enable_weread = getattr(config, "enable_weread", True)
        self.enable_yicai = getattr(config, "enable_yicai", True)
        self.enable_yystv = getattr(config, "enable_yystv", True)
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
        self.quark_format = getattr(config, "quark_format", "image")
        self.douban_format = getattr(config, "douban_format", "image")
        self.kr36_format = getattr(config, "kr36_format", "image")
        self.cto51_format = getattr(config, "cto51_format", "image")
        self.pojie52_format = getattr(config, "pojie52_format", "image")
        self.acfun_format = getattr(config, "acfun_format", "image")
        self.csdn_format = getattr(config, "csdn_format", "image")
        self.hellogithub_format = getattr(config, "hellogithub_format", "image")
        self.miyoushe_format = getattr(config, "miyoushe_format", "image")
        self.ifanr_format = getattr(config, "ifanr_format", "image")
        self.ithome_format = getattr(config, "ithome_format", "image")
        self.juejin_format = getattr(config, "juejin_format", "image")
        self.netease_format = getattr(config, "netease_format", "image")
        self.sina_format = getattr(config, "sina_format", "image")
        self.sspai_format = getattr(config, "sspai_format", "image")
        self.thepaper_format = getattr(config, "thepaper_format", "image")
        self.weatheralarm_format = getattr(config, "weatheralarm_format", "image")
        self.weread_format = getattr(config, "weread_format", "image")
        self.yicai_format = getattr(config, "yicai_format", "image")
        self.yystv_format = getattr(config, "yystv_format", "image")
        
        # Scheduled Push Configs
        self.groups = getattr(config, "groups", []) or []
        self.push_time = getattr(config, "push_time", "")
        self.push_items = getattr(config, "push_items", []) or []

        logger.info("实时热搜插件已初始化")
        self._monitoring_task = asyncio.create_task(self._daily_task())

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
                async with session.get(url, timeout=self.timeout) as response:
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

    def _calculate_sleep_time(self) -> float:
        """
        计算距离下次推送的秒数
        """
        now = datetime.datetime.now()
        # 支持多个时间点，使用中文或英文逗号分隔
        time_strs = self.push_time.replace("，", ",").split(",")
        candidates = []
        
        for t_str in time_strs:
            parts = t_str.strip().split(":")
            if len(parts) != 2:
                continue
            try:
                h, m = map(int, parts)
                target = now.replace(hour=h, minute=m, second=0, microsecond=0)
                if target <= now:
                    target += datetime.timedelta(days=1)
                candidates.append(target)
            except ValueError:
                continue
        
        if not candidates:
            # 如果解析失败，返回 -1
            return -1.0
            
        next_push = min(candidates)
        return (next_push - now).total_seconds()

    async def _daily_task(self):
        while True:
            if not self.push_time:
                await asyncio.sleep(60)
                continue
            
            try:
                sleep_sec = self._calculate_sleep_time()
                if sleep_sec < 0:
                    # 配置无效，等待一分钟再次检查
                    await asyncio.sleep(60)
                    continue

                logger.info(f"[HotSearch] 下次推送将在 {sleep_sec} 秒后")
                await asyncio.sleep(sleep_sec)
                
                await self._push_to_groups()
                
                # 防止短时间内重复推送（确保跳过当前秒）
                await asyncio.sleep(60)
            except asyncio.CancelledError:
                break
            except Exception:
                traceback.print_exc()
                await asyncio.sleep(60)

    async def _push_to_groups(self):
        if not self.groups or not self.push_items:
            return
        
        logger.info(f"[HotSearch] 开始定时推送: {self.push_items}")
        
        # 中文名映射
        NAME_CN_MAP = {
            "douyin": "抖音", "xhs": "小红书", "zhihu": "知乎", "weibo": "微博",
            "baidu": "百度", "dcd": "懂车帝", "bilibili": "哔哩哔哩", "toutiao": "头条",
            "tencent": "腾讯", "quark": "夸克", "maoyan": "猫眼", "douban": "豆瓣",
            "kr36": "36氪", "cto51": "51CTO", "pojie52": "52破解", "acfun": "AcFun",
            "csdn": "CSDN", "hellogithub": "HelloGitHub", "miyoushe": "米游社",
            "ifanr": "爱范儿", "ithome": "IT之家", "juejin": "掘金", "netease": "网易新闻",
            "sina": "新浪新闻", "sspai": "少数派", "thepaper": "澎湃新闻",
            "weatheralarm": "气象预警", "weread": "微信读书", "yicai": "第一财经",
            "yystv": "游研社"
        }

        for item in self.push_items:
            # 1. Get API URL and Format
            api_url = getattr(self, f"{item}_api", None)
            fmt = getattr(self, f"{item}_format", "image")
            name_cn = NAME_CN_MAP.get(item, item)

            if not api_url:
                continue

            # 2. Handle Extra Params
            extra = {}
            if item == "baidu": extra = {"type": self.baidu_type}
            elif item == "maoyan": extra = {"type": self.maoyan_type}
            elif item == "douban": extra = {"category": "movie"} # 默认电影
            elif item == "kr36": extra = {"type": "hot"}
            elif item == "pojie52": extra = {"type": "hot"}
            elif item == "acfun": extra = {"type": "-1"} # 综合
            elif item == "hellogithub": extra = {"type": "featured"}
            elif item == "miyoushe": extra = {"game": "2", "type": "1"} # 原神公告
            elif item == "ithome": extra = {"type": "hot"}
            elif item == "juejin": extra = {"type": "1"} # 综合
            elif item == "sina": extra = {"type": "all"}
            elif item == "sspai": extra = {"type": "hot"}
            elif item == "weread": extra = {"type": "rising"}
            elif item == "weatheralarm": 
                # 气象预警需要省份，定时推送无法提供，暂不推送或推全国（如果API支持空）
                # 这里暂且跳过或传空
                continue 

            # 3. Handle Format Key
            fmt_key = "format"
            if item == "tencent": fmt_key = "type"

            # 4. Request
            try:
                result = await self._request_hotsearch(api_url, fmt, self.global_apikey, extra, fmt_key)
                if not result:
                    continue
                
                # 5. Send to Groups
                for group_id in self.groups:
                    try:
                        chain = MessageChain()
                        if result.get("image_path"):
                            chain = chain.file_image(result["image_path"])
                        elif result.get("text"):
                            chain = chain.message(result["text"])
                        
                        await self.context.send_message(group_id, chain)
                        await asyncio.sleep(1) # 避免刷屏
                    except Exception as e:
                        logger.error(f"推送 {item} 到 {group_id} 失败: {e}")

                # 6. Cleanup
                if result.get("image_path"):
                    try:
                        os.unlink(result["image_path"])
                    except:
                        pass
                
                # Platform interval
                await asyncio.sleep(3)

            except Exception as e:
                logger.error(f"定时推送 {item} 失败: {e}")

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

    @filter.command("夸克热搜", alias={"夸克实时热搜", "夸克榜", "夸克"})
    async def quark(self, event: AstrMessageEvent):
        async for r in self._handle(event, self.quark_api, self.quark_format, self.enable_quark, "夸克"):
            yield r

    @filter.command("猫眼票房", alias={"猫眼热搜", "猫眼榜", "猫眼"})
    async def maoyan(self, event: AstrMessageEvent):
        text = event.get_message_str() or ""
        mtype = self._pick_maoyan_type(text)
        async for r in self._handle(event, self.maoyan_api, self.maoyan_format, self.enable_maoyan, "猫眼", extra={"type": mtype}):
            yield r

    @filter.command("豆瓣热榜", alias={"豆瓣榜", "豆瓣热搜", "豆瓣"})
    async def douban(self, event: AstrMessageEvent):
        text = event.get_message_str() or ""
        category = self._pick_douban_category(text)
        async for r in self._handle(event, self.douban_api, self.douban_format, self.enable_douban, "豆瓣", extra={"category": category}):
            yield r

    @filter.command("36氪热搜", alias={"36kr", "36氪", "36kr热搜"})
    async def kr36(self, event: AstrMessageEvent):
        text = event.get_message_str() or ""
        ktype = self._pick_36kr_type(text)
        async for r in self._handle(event, self.kr36_api, self.kr36_format, self.enable_kr36, "36氪", extra={"type": ktype}):
            yield r

    @filter.command("51CTO热搜", alias={"51cto", "51CTO"})
    async def cto51(self, event: AstrMessageEvent):
        async for r in self._handle(event, self.cto51_api, self.cto51_format, self.enable_cto51, "51CTO"):
            yield r

    @filter.command("52破解热搜", alias={"52pojie", "52破解", "吾爱破解", "吾爱破解热搜"})
    async def pojie52(self, event: AstrMessageEvent):
        text = event.get_message_str() or ""
        ptype = self._pick_52pojie_type(text)
        async for r in self._handle(event, self.pojie52_api, self.pojie52_format, self.enable_pojie52, "52破解", extra={"type": ptype}):
            yield r

    @filter.command("AcFun热搜", alias={"acfun", "AcFun", "A站热搜", "A站"})
    async def acfun(self, event: AstrMessageEvent):
        text = event.get_message_str() or ""
        atype = self._pick_acfun_type(text)
        async for r in self._handle(event, self.acfun_api, self.acfun_format, self.enable_acfun, "AcFun", extra={"type": atype}):
            yield r

    @filter.command("CSDN热搜", alias={"csdn", "CSDN", "CSDN榜"})
    async def csdn(self, event: AstrMessageEvent):
        async for r in self._handle(event, self.csdn_api, self.csdn_format, self.enable_csdn, "CSDN"):
            yield r

    @filter.command("HelloGitHub热搜", alias={"hellogithub", "HelloGitHub", "GitHub热搜", "github"})
    async def hellogithub(self, event: AstrMessageEvent):
        text = event.get_message_str() or ""
        htype = self._pick_hellogithub_type(text)
        async for r in self._handle(event, self.hellogithub_api, self.hellogithub_format, self.enable_hellogithub, "HelloGitHub", extra={"type": htype}):
            yield r

    @filter.command("米游社热搜", alias={"miyoushe", "米游社", "米游社榜"})
    async def miyoushe(self, event: AstrMessageEvent):
        text = event.get_message_str() or ""
        game, mtype = self._pick_miyoushe_params(text)
        async for r in self._handle(event, self.miyoushe_api, self.miyoushe_format, self.enable_miyoushe, "米游社", extra={"game": game, "type": mtype}):
            yield r

    @filter.command("爱范儿热搜", alias={"ifanr", "爱范儿", "爱范儿快讯"})
    async def ifanr(self, event: AstrMessageEvent):
        async for r in self._handle(event, self.ifanr_api, self.ifanr_format, self.enable_ifanr, "爱范儿"):
            yield r

    @filter.command("IT之家热搜", alias={"ithome", "IT之家", "IT之家榜"})
    async def ithome(self, event: AstrMessageEvent):
        text = event.get_message_str() or ""
        itype = self._pick_ithome_type(text)
        async for r in self._handle(event, self.ithome_api, self.ithome_format, self.enable_ithome, "IT之家", extra={"type": itype}):
            yield r

    @filter.command("掘金热搜", alias={"juejin", "掘金", "掘金榜"})
    async def juejin(self, event: AstrMessageEvent):
        text = event.get_message_str() or ""
        jtype = self._pick_juejin_type(text)
        async for r in self._handle(event, self.juejin_api, self.juejin_format, self.enable_juejin, "掘金", extra={"type": jtype}):
            yield r

    @filter.command("网易新闻热搜", alias={"netease", "网易", "网易新闻", "网易新闻榜"})
    async def netease(self, event: AstrMessageEvent):
        async for r in self._handle(event, self.netease_api, self.netease_format, self.enable_netease, "网易新闻"):
            yield r

    @filter.command("新浪新闻热搜", alias={"sina", "新浪", "新浪新闻", "新浪新闻榜"})
    async def sina(self, event: AstrMessageEvent):
        text = event.get_message_str() or ""
        stype = self._pick_sina_type(text)
        async for r in self._handle(event, self.sina_api, self.sina_format, self.enable_sina, "新浪新闻", extra={"type": stype}):
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

    def _pick_douban_category(self, text: str) -> str:
        t = text.lower()
        if ("国内剧" in text) or ("国产剧" in text) or ("tv_chinese" in t):
            return "tv_chinese"
        if ("全球剧" in text) or ("美剧" in text) or ("tv_global" in t):
            return "tv_global"
        if ("国内综艺" in text) or ("国产综艺" in text) or ("show_chinese" in t):
            return "show_chinese"
        if ("全球综艺" in text) or ("国外综艺" in text) or ("show_global" in t):
            return "show_global"
        # 默认为电影
        return "movie"

    def _pick_36kr_type(self, text: str) -> str:
        t = text.lower()
        if ("视频" in text) or ("video" in t):
            return "video"
        if ("热议" in text) or ("评论" in text) or ("comment" in t):
            return "comment"
        if ("收藏" in text) or ("collect" in t):
            return "collect"
        return "hot"

    def _pick_52pojie_type(self, text: str) -> str:
        t = text.lower()
        if ("热门" in text) or ("hot" in t):
            return "hot"
        if ("回复" in text) or ("new" in t) and ("thread" not in t):
            return "new"
        if ("发表" in text) or ("newthread" in t):
            return "newthread"
        return "digest"

    def _pick_acfun_type(self, text: str) -> str:
        t = text.lower()
        if ("番剧" in text): return "155"
        if ("动画" in text): return "1"
        if ("娱乐" in text): return "60"
        if ("生活" in text): return "201"
        if ("音乐" in text): return "58"
        if ("舞蹈" in text) or ("偶像" in text): return "123"
        if ("游戏" in text): return "59"
        if ("科技" in text): return "70"
        if ("影视" in text): return "68"
        if ("体育" in text): return "69"
        if ("鱼塘" in text): return "125"
        return "-1"

    def _pick_hellogithub_type(self, text: str) -> str:
        t = text.lower()
        if ("全部" in text) or ("all" in t):
            return "all"
        return "featured"

    def _pick_miyoushe_params(self, text: str) -> tuple[str, str]:
        # game: 1(崩坏3) | 2(原神) | 3(崩坏学园2) | 4(未定事件簿) | 5(大别野) | 6(崩坏: 星穹铁道) | 8(绝区零)
        # type: 1(公告) | 2(活动) | 3(资讯)
        t = text.lower()
        
        # 默认值
        game = "2" # 原神
        mtype = "1" # 公告

        if ("崩坏3" in text) or ("崩3" in text): game = "1"
        elif ("崩坏学园" in text): game = "3"
        elif ("未定" in text): game = "4"
        elif ("大别野" in text): game = "5"
        elif ("星穹铁道" in text) or ("铁道" in text): game = "6"
        elif ("绝区零" in text) or ("zzz" in t): game = "8"
        elif ("原神" in text): game = "2"

        if ("活动" in text): mtype = "2"
        elif ("资讯" in text): mtype = "3"
        elif ("公告" in text): mtype = "1"
        
        return game, mtype

    def _pick_ithome_type(self, text: str) -> str:
        t = text.lower()
        if ("热榜" in text) or ("hot" in t):
            return "hot"
        return "news"

    def _pick_juejin_type(self, text: str) -> str:
        t = text.lower()
        if ("前端" in text): return "6809637767543259144"
        if ("后端" in text): return "6809637769959178254"
        if ("android" in t) or ("安卓" in text): return "6809637773935378440"
        if ("ios" in t) or ("苹果" in text): return "6809637771511078925"
        if ("人工智能" in text) or ("ai" in t): return "6809637776263217160"
        if ("开发工具" in text) or ("工具" in text): return "6809637772874219534"
        if ("代码人生" in text): return "6931685841039015950"
        if ("阅读" in text): return "6809637770487652366"
        return "1"

    def _pick_sina_type(self, text: str) -> str:
        t = text.lower()
        if ("热议" in text) or ("hotcmnt" in t): return "hotcmnt"
        if ("视频" in text) or ("minivideo" in t): return "minivideo"
        if ("娱乐" in text) or ("ent" in t): return "ent"
        if ("ai" in t) or ("人工智能" in text): return "ai"
        if ("汽车" in text) or ("auto" in t): return "auto"
        if ("育儿" in text) or ("mother" in t): return "mother"
        if ("时尚" in text) or ("fashion" in t): return "fashion"
        if ("旅游" in text) or ("travel" in t): return "travel"
        if ("esg" in t): return "esg"
        return "all"

    @filter.command("少数派热搜", alias={"sspai", "少数派", "少数派榜"})
    async def sspai(self, event: AstrMessageEvent):
        text = event.get_message_str() or ""
        stype = self._pick_sspai_type(text)
        async for r in self._handle(event, self.sspai_api, self.sspai_format, self.enable_sspai, "少数派", extra={"type": stype}):
            yield r

    @filter.command("澎湃新闻热搜", alias={"thepaper", "澎湃", "澎湃新闻", "澎湃新闻榜"})
    async def thepaper(self, event: AstrMessageEvent):
        async for r in self._handle(event, self.thepaper_api, self.thepaper_format, self.enable_thepaper, "澎湃新闻"):
            yield r

    @filter.command("气象预警", alias={"weatheralarm", "天气预警", "中央气象台预警"})
    async def weatheralarm(self, event: AstrMessageEvent):
        text = event.get_message_str() or ""
        async for r in self._handle(event, self.weatheralarm_api, self.weatheralarm_format, self.enable_weatheralarm, "气象预警", extra={"province": text}):
            yield r

    @filter.command("微信读书热搜", alias={"weread", "微信读书", "微信读书榜"})
    async def weread(self, event: AstrMessageEvent):
        text = event.get_message_str() or ""
        wtype = self._pick_weread_type(text)
        async for r in self._handle(event, self.weread_api, self.weread_format, self.enable_weread, "微信读书", extra={"type": wtype}):
            yield r

    @filter.command("第一财经热搜", alias={"yicai", "第一财经", "第一财经榜"})
    async def yicai(self, event: AstrMessageEvent):
        async for r in self._handle(event, self.yicai_api, self.yicai_format, self.enable_yicai, "第一财经"):
            yield r

    @filter.command("游研社热搜", alias={"yystv", "游研社", "游研社榜"})
    async def yystv(self, event: AstrMessageEvent):
        async for r in self._handle(event, self.yystv_api, self.yystv_format, self.enable_yystv, "游研社"):
            yield r

    def _pick_sspai_type(self, text: str) -> str:
        t = text.lower()
        if "应用" in text or "apps" in t: return "apps"
        if "生活" in text or "life" in t: return "life"
        if "效率" in text or "efficiency" in t: return "efficiency"
        if "播客" in text or "podcast" in t: return "podcast"
        return "hot"

    def _pick_weread_type(self, text: str) -> str:
        t = text.lower()
        if "热搜" in text or "hot_search" in t: return "hot_search"
        if "新书" in text or "newbook" in t: return "newbook"
        if "小说" in text or "general_novel_rising" in t: return "general_novel_rising"
        if "总榜" in text or "all" in t: return "all"
        return "rising"

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
            "• 夸克热搜\n"
            "• 猫眼票房\n"
            "• 豆瓣热榜 (指令: 豆瓣 电影/国内剧/全球剧/国内综艺/全球综艺)\n"
            "• 36氪热搜 (指令: 36氪 人气/视频/热议/收藏)\n"
            "• 51CTO热搜\n"
            "• 52破解热搜 (指令: 52破解 精华/热门/回复/发表)\n"
            "• AcFun热搜 (指令: AcFun 综合/番剧/动画/娱乐/生活/音乐/舞蹈/游戏/科技/影视/体育/鱼塘)\n"
            "• CSDN热搜\n"
            "• HelloGitHub热搜 (指令: HelloGitHub 精选/全部)\n"
            "• 米游社热搜 (指令: 米游社 [原神/崩坏3/崩坏学园2/未定事件簿/大别野/星穹铁道/绝区零] [公告/活动/资讯])\n"
            "• 爱范儿热搜\n"
            "• IT之家热搜 (指令: IT之家 热榜)\n"
            "• 掘金热搜 (指令: 掘金 前端/后端/Android/iOS/人工智能/开发工具/代码人生/阅读)\n"
            "• 网易新闻热搜\n"
            "• 新浪新闻热搜 (指令: 新浪新闻 热议/视频/娱乐/AI/汽车/育儿/时尚/旅游/ESG)\n"
            "• 少数派热搜 (指令: 少数派 应用/生活/效率/播客)\n"
            "• 澎湃新闻热搜\n"
            "• 气象预警 (指令: 气象预警 [省份]，默认全国)\n"
            "• 微信读书热搜 (指令: 微信读书 热搜/新书/小说/总榜)\n"
            "• 第一财经热搜\n"
            "• 游研社热搜\n\n"
        )
        yield event.plain_result(text)

    async def terminate(self):
        if self._monitoring_task:
            self._monitoring_task.cancel()
        logger.info("实时热搜插件已终止")
