import asyncio
import aiohttp
import tempfile
import os
import datetime
from contextlib import ExitStack
from pathlib import Path
from types import SimpleNamespace

from astrbot.api import AstrBotConfig, logger
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.message_components import Node, Nodes
from astrbot.api.star import Context, Star, register
from astrbot.core.message.message_event_result import MessageChain

PLUGIN_DATA_DIR = Path("data", "plugins_data", "astrbot_hotsearch")
PLUGIN_DATA_DIR.mkdir(parents=True, exist_ok=True)

class _CmdWrappedEvent:
    """包装原始 event，使 get_message_str 返回伪造的指令字符串，便于在 LLM Tool 中复用现有指令 handler。"""

    __slots__ = ("_event", "_fake_message")

    def __init__(self, original: AstrMessageEvent, fake_message: str):
        self._event = original
        self._fake_message = fake_message.strip()

    def get_message_str(self) -> str:
        return self._fake_message

    def __getattr__(self, name: str):
        return getattr(self._event, name)

@register(
    "astrbot_hotsearch",
    "柠柚",
    "实时热搜聚合，支持抖音/知乎/微博/百度/懂车帝/哔哩哔哩/腾讯/头条/猫眼票房/夸克/豆瓣/36氪/51CTO/52破解/AcFun/CSDN/HelloGitHub/米游社/爱范儿/IT之家/掘金/网易新闻/新浪新闻/少数派/澎湃新闻/气象预警/微信读书/第一财经/游研社/财联社/快手/好游快爆，输出图片或文本",
    "1.0.8",
)
class HotSearchPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context, config)
        self.douyin_api = getattr(config, "douyin_api", "https://api.nycnm.cn/api/v2/douyinrs")
        self.zhihu_api = getattr(config, "zhihu_api", "https://api.nycnm.cn/api/v2/zhihu")
        self.weibo_api = getattr(config, "weibo_api", "https://api.nycnm.cn/api/v2/wb")
        self.baidu_api = getattr(config, "baidu_api", "https://api.nycnm.cn/api/v2/baidu")
        self.dcd_api = getattr(config, "dcd_api", "https://api.nycnm.cn/api/v2/dongchedi")
        self.bilibili_api = getattr(config, "bilibili_api", "https://api.nycnm.cn/api/v2/bilibilirs")
        self.toutiao_api = getattr(config, "toutiao_api", "https://api.nycnm.cn/api/v2/toutiao")
        self.maoyan_api = getattr(config, "maoyan_api", "https://api.nycnm.cn/api/v2/maoyan")
        self.tencent_api = getattr(config, "tencent_api", "https://api.nycnm.cn/api/v2/txxw")
        self.quark_api = getattr(config, "quark_api", "https://api.nycnm.cn/api/v2/quark")
        self.douban_api = getattr(config, "douban_api", "https://api.nycnm.cn/api/v2/douban")
        self.kr36_api = getattr(config, "kr36_api", "https://api.nycnm.cn/api/v2/36kr")
        self.cto51_api = getattr(config, "cto51_api", "https://api.nycnm.cn/api/v2/51cto")
        self.pojie52_api = getattr(config, "pojie52_api", "https://api.nycnm.cn/api/v2/52pojie")
        self.acfun_api = getattr(config, "acfun_api", "https://api.nycnm.cn/api/v2/acfun")
        self.csdn_api = getattr(config, "csdn_api", "https://api.nycnm.cn/api/v2/csdn")
        self.hellogithub_api = getattr(config, "hellogithub_api", "https://api.nycnm.cn/api/v2/hellogithub")
        self.ithome_api = getattr(config, "ithome_api", "https://api.nycnm.cn/api/v2/xijiayi")
        self.juejin_api = getattr(config, "juejin_api", "https://api.nycnm.cn/api/v2/juejin")
        self.netease_api = getattr(config, "netease_api", "https://api.nycnm.cn/api/v2/netease")
        self.sina_api = getattr(config, "sina_api", "https://api.nycnm.cn/api/v2/sina")
        self.sspai_api = getattr(config, "sspai_api", "https://api.nycnm.cn/api/v2/sspai")
        self.thepaper_api = getattr(config, "thepaper_api", "https://api.nycnm.cn/api/v2/thepaper")
        self.weatheralarm_api = getattr(config, "weatheralarm_api", "https://api.nycnm.cn/api/v2/weatheralarm")
        self.weread_api = getattr(config, "weread_api", "https://api.nycnm.cn/api/v2/weread")
        self.cls_api = getattr(config, "cls_api", "https://api.nycnm.cn/api/v2/cls")
        self.kuaishou_api = getattr(config, "kuaishou_api", "https://api.nycnm.cn/api/v2/kuaishou")
        self.hykb_api = getattr(config, "hykb_api", "https://api.nycnm.cn/api/v2/hykb")

        self.global_apikey = getattr(config, "api_key", "")
        self.enable_memory_filter = getattr(config, "enable_memory_filter", False)
        self.user_preference = getattr(config, "user_preference", "")
        self.timeout = getattr(config, "timeout", 30)
        self.enable_douyin = getattr(config, "enable_douyin", True)
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
        self.enable_cls = getattr(config, "enable_cls", True)
        self.enable_kuaishou = getattr(config, "enable_kuaishou", True)
        self.enable_hykb = getattr(config, "enable_hykb", True)
        self.douyin_format = getattr(config, "douyin_format", "image")
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
        self.cls_format = getattr(config, "cls_format", "image")
        self.kuaishou_format = getattr(config, "kuaishou_format", "image")
        self.hykb_format = getattr(config, "hykb_format", "image")
        
        self.groups = list(dict.fromkeys(getattr(config, "groups", []) or []))
        self.push_time = getattr(config, "push_time", "") or ""
        self.push_items = list(dict.fromkeys(getattr(config, "push_items", []) or []))
        self.forward_message = getattr(config, "forward_message", False)
        self._push_times = self._parse_push_times(self.push_time)

        # 状态保存在事件循环上，插件模块重新导入后仍可找到旧任务和已触发时间。
        loop = asyncio.get_running_loop()
        state = getattr(loop, "_astrbot_hotsearch_schedule", None)
        if state is None:
            state = SimpleNamespace(task=None, lock=asyncio.Lock(), recent_slots={})
            loop._astrbot_hotsearch_schedule = state
        self._push_state = state
        if state.task is not None:
            state.task.cancel()
        self._monitoring_task = None
        if self._push_times and self.groups and self.push_items:
            self._monitoring_task = loop.create_task(self._daily_task())
        state.task = self._monitoring_task
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
            
        # 如果开启了偏好过滤功能，强制使用 text 格式请求
        if getattr(self, "enable_memory_filter", False):
            fmt = "text"
            
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
            text_result = result["text"]
            if getattr(self, "enable_memory_filter", False):
                umo = getattr(event, "unified_msg_origin", None) or getattr(event, "session_id", "")
                user_pref = getattr(self, "user_preference", "").strip()
                try:
                    provider_id = await self.context.get_current_chat_provider_id(umo=umo)
                    if provider_id:
                        pref_prompt = f"我的偏好内容是：【{user_pref}】。" if user_pref else "请根据你对我（当前用户）的了解、偏好以及历史记忆来判断。"
                        
                        # 尝试获取当前会话的 System Prompt（人格）
                        sys_prompt = ""
                        try:
                            if hasattr(self.context, 'persona_manager'):
                                persona_mgr = self.context.persona_manager
                                if hasattr(persona_mgr, 'get_default_persona_v3'):
                                    persona = persona_mgr.get_default_persona_v3(umo=umo)
                                    if persona and isinstance(persona, dict):
                                        sys_prompt = persona.get('prompt', '')
                                    elif persona and hasattr(persona, 'system_prompt'):
                                        sys_prompt = persona.system_prompt
                        except Exception as e:
                            logger.error(f"获取人格配置失败: {e}")
                            
                        system_instruction = f"你的角色设定是：\n{sys_prompt}\n\n" if sys_prompt else "请用你平时的人格和说话风格回复。\n"
                        
                        prompt = (
                            f"{system_instruction}"
                            f"以下是当前的{name}热搜内容。\n"
                            f"{pref_prompt}\n"
                            f"【重要要求】\n"
                            f"1. 必须根据用户的偏好过滤出最相关的几条热点进行播报。\n"
                            f"2. 绝对不能使用像机器或AI总结的口吻（如“根据你的偏好，我为你推荐...”）。\n"
                            f"3. 【最核心指令】：你必须完全代入上述的“角色设定”与我对话，使用符合角色性格的口癖、动作描写和语气来告诉我这些热搜！\n"
                            f"热搜内容：\n{text_result}"
                        )
                        # 这里我们不仅要传 prompt，还要确保把人格注入到系统提示词里
                        llm_resp = await self.context.llm_generate(
                            chat_provider_id=provider_id,
                            prompt=prompt,
                            system_prompt=sys_prompt if sys_prompt else None
                        )
                        out = (getattr(llm_resp, "completion_text", None) or "").strip()
                        if out:
                            text_result = out
                except Exception as e:
                    logger.error(f"LLM 记忆过滤失败: {e}")
            yield event.plain_result(text_result)
            return

    @staticmethod
    def _parse_push_times(push_time: str) -> set[tuple[int, int]]:
        times = set()
        for value in push_time.replace("，", ",").split(","):
            value = value.strip()
            if not value:
                continue
            try:
                hour, minute = map(int, value.split(":"))
                datetime.time(hour, minute)
            except (ValueError, OverflowError):
                logger.warning(f"[HotSearch] 忽略无效的推送时间: {value}")
                continue
            times.add((hour, minute))
        return times

    async def _daily_task(self):
        state = self._push_state
        task = asyncio.current_task()
        while state.task is task:
            async with state.lock:
                if state.task is not task:
                    return
                now = datetime.datetime.now()
                slot = now.replace(second=0, microsecond=0)
                if (slot.hour, slot.minute) in self._push_times and slot not in state.recent_slots:
                    # 发送前占用本次时间点，防止同一分钟重载后再次推送。
                    state.recent_slots[slot] = None
                    if len(state.recent_slots) > 1440:
                        del state.recent_slots[next(iter(state.recent_slots))]
                    try:
                        await self._push_to_groups()
                    except Exception:
                        logger.exception("[HotSearch] 定时推送失败")
                    continue

            # 按系统时间复核到点情况，不依据上一次 sleep 的结束直接推送。
            next_minute = slot + datetime.timedelta(minutes=1)
            await asyncio.sleep((next_minute - now).total_seconds())

    @staticmethod
    def _remove_push_image(path: str):
        try:
            Path(path).unlink(missing_ok=True)
        except OSError as exc:
            logger.warning(f"[HotSearch] 清理定时推送临时图片失败: {exc}")

    async def _send_push_chain(self, group_id: str, chain: MessageChain):
        try:
            if await self.context.send_message(group_id, chain) is False:
                logger.warning(f"[HotSearch] 未向 {group_id} 发送定时推送，请检查会话标识和平台连接")
        except Exception as exc:
            # 发送结果不确定时不重发，避免平台实际已送达后再出现重复消息。
            logger.error(f"[HotSearch] 定时推送到 {group_id} 失败: {exc}")
        await asyncio.sleep(1)

    async def _forward_sender(self, group_id: str) -> str | None:
        platform_id, _, session = group_id.partition(":GroupMessage:")
        if not platform_id or not session:
            return None
        try:
            platform = self.context.get_platform_inst(platform_id)
            if platform is None or platform.meta().name != "aiocqhttp":
                return None
            info = await asyncio.wait_for(
                platform.get_client().call_action("get_login_info"), timeout=5
            )
            sender = str(info["user_id"])
            return sender if sender.isdecimal() else None
        except Exception as exc:
            logger.warning(f"[HotSearch] 获取 {platform_id} 的合并转发发送者失败: {exc}")
            return None

    async def _push_to_groups(self):
        if not self.groups or not self.push_items:
            return
        
        mode = "合并转发" if self.forward_message else "逐条发送"
        logger.info(f"[HotSearch] 开始定时推送（{mode}）: {self.push_items}")
        
        # 中文名映射
        NAME_CN_MAP = {
            "douyin": "抖音", "zhihu": "知乎", "weibo": "微博",
            "baidu": "百度", "dcd": "懂车帝", "bilibili": "哔哩哔哩", "toutiao": "头条",
            "tencent": "腾讯", "quark": "夸克", "maoyan": "猫眼", "douban": "豆瓣",
            "kr36": "36氪", "cto51": "51CTO", "pojie52": "52破解", "acfun": "AcFun",
            "csdn": "CSDN", "hellogithub": "HelloGitHub", "miyoushe": "米游社",
            "ifanr": "爱范儿", "ithome": "IT之家", "juejin": "掘金", "netease": "网易新闻",
            "sina": "新浪新闻", "sspai": "少数派", "thepaper": "澎湃新闻",
            "weatheralarm": "气象预警", "weread": "微信读书", "yicai": "第一财经",
            "yystv": "游研社", "cls": "财联社", "kuaishou": "快手", "hykb": "好游快爆"
        }

        entries = []
        # 合并转发需要让图片存活到所有群发送完成；取消任务时同样清理。
        with ExitStack() as images:
            for item in self.push_items:
                api_url = getattr(self, f"{item}_api", None)
                if not api_url or item == "weatheralarm":
                    continue

                fmt = getattr(self, f"{item}_format", "image")
                fmt_key = "type" if item == "tencent" else "format"
                extra = {}
                if item == "baidu": extra = {"type": self.baidu_type}
                elif item == "maoyan": extra = {"type": self.maoyan_type}
                elif item == "douban": extra = {"category": "movie"}
                elif item == "kr36": extra = {"type": "hot"}
                elif item == "pojie52": extra = {"type": "hot"}
                elif item == "acfun": extra = {"type": "-1"}
                elif item == "hellogithub": extra = {"type": "featured"}
                elif item == "miyoushe": extra = {"game": "2", "type": "1"}
                elif item == "ithome": extra = {"type": "hot"}
                elif item == "juejin": extra = {"type": "1"}
                elif item == "sina": extra = {"type": "all"}
                elif item == "sspai": extra = {"type": "hot"}
                elif item == "weread": extra = {"type": "rising"}

                result = await self._request_hotsearch(api_url, fmt, self.global_apikey, extra, fmt_key)
                if not result:
                    continue
                chain = MessageChain()
                if image_path := result.get("image_path"):
                    images.callback(self._remove_push_image, image_path)
                    chain.file_image(image_path)
                elif result.get("text"):
                    chain.message(result["text"])
                else:
                    continue

                if self.forward_message:
                    entries.append((NAME_CN_MAP.get(item, item), chain))
                else:
                    for group_id in self.groups:
                        await self._send_push_chain(group_id, chain)
                    await asyncio.sleep(3)

            if entries:
                for group_id in self.groups:
                    sender = await self._forward_sender(group_id)
                    if sender is None:
                        logger.info(f"[HotSearch] {group_id} 未使用合并转发，逐条发送")
                        for _, chain in entries:
                            await self._send_push_chain(group_id, chain)
                        continue

                    nodes = [
                        Node(name=name, uin=sender, content=chain.chain)
                        for name, chain in entries
                    ]
                    await self._send_push_chain(group_id, MessageChain(chain=[Nodes(nodes=nodes)]))

    @filter.command("抖音热搜", alias={"抖音实时热搜", "抖音榜", "抖音热点", "抖音"})
    async def douyin(self, event: AstrMessageEvent):
        async for r in self._handle(event, self.douyin_api, self.douyin_format, self.enable_douyin, "抖音"):
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

    @filter.command("财联社热搜", alias={"cls", "财联社", "财联社榜", "财联社电报"})
    async def cls(self, event: AstrMessageEvent):
        async for r in self._handle(event, self.cls_api, self.cls_format, self.enable_cls, "财联社"):
            yield r

    @filter.command("快手热搜", alias={"kuaishou", "快手", "快手榜", "快手热榜"})
    async def kuaishou(self, event: AstrMessageEvent):
        async for r in self._handle(event, self.kuaishou_api, self.kuaishou_format, self.enable_kuaishou, "快手"):
            yield r

    @filter.command("好游快爆热搜", alias={"hykb", "好游快爆", "好游快爆榜"})
    async def hykb(self, event: AstrMessageEvent):
        async for r in self._handle(event, self.hykb_api, self.hykb_format, self.enable_hykb, "好游快爆"):
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

    @filter.regex(r"(抖音|知乎|微博|百度|懂车帝|b站|哔哩哔哩|头条|腾讯|夸克|猫眼|豆瓣|36氪|51cto|52破解|acfun|a站|csdn|github|米游社|爱范儿|it之家|掘金|网易|新浪|少数派|澎湃|气象预警|微信读书|第一财经|游研社|财联社|快手|好游快爆).*(热搜|热点|热榜|榜单|新闻|有什么)", priority=999)
    async def natural_hotsearch_interceptor(self, event: AstrMessageEvent):
        """
        强行拦截自然语言提问（如“今日微博热搜”、“b站有什么热点”），
        避免大模型（尤其是带强人设时）沉迷聊天而忘记触发 Tool Call。
        拦截后直接委托给原本的 tool_hotsearch_query 逻辑执行。
        """
        text = (event.get_message_str() or "").lower()
        platforms = [
            "抖音", "知乎", "微博", "百度", "懂车帝", "哔哩哔哩", "b站",
            "头条", "腾讯", "夸克", "猫眼", "豆瓣", "36氪", "51cto", "52破解",
            "acfun", "a站", "csdn", "github", "米游社", "爱范儿", "it之家",
            "掘金", "网易", "新浪", "少数派", "澎湃", "气象预警", "微信读书",
            "第一财经", "游研社", "财联社", "快手", "好游快爆"
        ]
        
        target_p = ""
        for p in platforms:
            if p in text:
                target_p = p
                break
                
        if target_p:
            # 停止事件继续往后传递给大模型自然对话
            event.stop_event()
            # 强制调用原本的工具处理逻辑
            async for r in self.tool_hotsearch_query(event, platform=target_p):
                yield r

    @filter.llm_tool(name="hotsearch_query")
    async def tool_hotsearch_query(self, event: AstrMessageEvent, platform: str, extra_args: str = ""):
        """查询各大平台的热搜榜单、热门话题、新闻热榜。
        
        【最高指令 / CRITICAL INSTRUCTION】
        当你决定查热搜时，你必须且只能通过触发标准的 Function Call (工具调用) 来获取数据！
        绝对不要在聊天框里写出类似 “(目的：调用热搜工具...)” 这样的假动作或旁白！
        绝对不要输出任何“稍等”、“这就帮你查”的过渡闲聊文本！
        任何只说不做的行为都是被严厉禁止的。请立即抛出工具调用。
        
        Args:
            platform(string): 平台名称，必须是以下之一：抖音、知乎、微博、百度、懂车帝、哔哩哔哩、B站、头条、腾讯、夸克、猫眼、豆瓣、36氪、51CTO、52破解、AcFun、A站、CSDN、HelloGitHub、米游社、爱范儿、IT之家、掘金、网易新闻、新浪新闻、少数派、澎湃新闻、气象预警、微信读书、第一财经、游研社、财联社、快手、好游快爆。
            extra_args(string): 附加参数，比如猫眼支持“电影/电视剧”、豆瓣支持“国内剧/美剧”等，没有则留空。
        """
        p = platform.lower()
        fake_msg = f"{platform} {extra_args}".strip()
        wrapped = _CmdWrappedEvent(event, fake_msg)
        
        if p in ["抖音"]:
            async for r in self.douyin(wrapped): yield r
        elif p in ["知乎"]:
            async for r in self.zhihu(wrapped): yield r
        elif p in ["微博"]:
            async for r in self.weibo(wrapped): yield r
        elif p in ["百度"]:
            async for r in self.baidu(wrapped): yield r
        elif p in ["懂车帝"]:
            async for r in self.dcd(wrapped): yield r
        elif p in ["哔哩哔哩", "b站"]:
            async for r in self.bilibili(wrapped): yield r
        elif p in ["头条", "今日头条"]:
            async for r in self.toutiao(wrapped): yield r
        elif p in ["腾讯", "腾讯新闻"]:
            async for r in self.tencent(wrapped): yield r
        elif p in ["夸克"]:
            async for r in self.quark(wrapped): yield r
        elif p in ["猫眼", "猫眼票房"]:
            async for r in self.maoyan(wrapped): yield r
        elif p in ["豆瓣", "豆瓣热榜"]:
            async for r in self.douban(wrapped): yield r
        elif p in ["36氪", "36kr"]:
            async for r in self.kr36(wrapped): yield r
        elif p in ["51cto"]:
            async for r in self.cto51(wrapped): yield r
        elif p in ["52破解", "吾爱破解"]:
            async for r in self.pojie52(wrapped): yield r
        elif p in ["acfun", "a站"]:
            async for r in self.acfun(wrapped): yield r
        elif p in ["csdn"]:
            async for r in self.csdn(wrapped): yield r
        elif p in ["hellogithub", "github"]:
            async for r in self.hellogithub(wrapped): yield r
        elif p in ["米游社"]:
            async for r in self.miyoushe(wrapped): yield r
        elif p in ["爱范儿"]:
            async for r in self.ifanr(wrapped): yield r
        elif p in ["it之家"]:
            async for r in self.ithome(wrapped): yield r
        elif p in ["掘金"]:
            async for r in self.juejin(wrapped): yield r
        elif p in ["网易新闻", "网易"]:
            async for r in self.netease(wrapped): yield r
        elif p in ["新浪新闻", "新浪"]:
            async for r in self.sina(wrapped): yield r
        elif p in ["少数派"]:
            async for r in self.sspai(wrapped): yield r
        elif p in ["澎湃新闻", "澎湃"]:
            async for r in self.thepaper(wrapped): yield r
        elif p in ["气象预警", "天气预警"]:
            async for r in self.weatheralarm(wrapped): yield r
        elif p in ["微信读书"]:
            async for r in self.weread(wrapped): yield r
        elif p in ["第一财经"]:
            async for r in self.yicai(wrapped): yield r
        elif p in ["游研社"]:
            async for r in self.yystv(wrapped): yield r
        elif p in ["财联社"]:
            async for r in self.cls(wrapped): yield r
        elif p in ["快手"]:
            async for r in self.kuaishou(wrapped): yield r
        elif p in ["好游快爆"]:
            async for r in self.hykb(wrapped): yield r
        else:
            yield event.plain_result(f"暂不支持该平台：{platform}，请检查平台名称。")

    @filter.command("help_hotsearch", alias={"热搜帮助", "实时热搜帮助"})
    async def show_help(self, event: AstrMessageEvent):
        text = (
            "🔥 实时热搜插件\n\n"
            "【指令，无需参数】\n"
            "• 抖音热搜\n"
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
            "• 财联社热搜\n"
            "• 快手热搜\n"
            "• 好游快爆热搜\n\n"
        )
        yield event.plain_result(text)

    async def terminate(self):
        task = self._monitoring_task
        if task is not None:
            if self._push_state.task is task:
                self._push_state.task = None
                task.cancel()
            await asyncio.gather(task, return_exceptions=True)
        logger.info("实时热搜插件已终止")
