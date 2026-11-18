# 实时热搜插件（astrbot_plugin_hotsearch）

## 功能
- 聚合抖音/知乎/微博/百度/懂车帝/哔哩哔哩/腾讯/头条/猫眼票房/夸克/豆瓣/36氪/51CTO/52破解/AcFun/CSDN/HelloGitHub/米游社/爱范儿/IT之家/掘金/网易新闻/新浪新闻/少数派/澎湃新闻/气象预警/微信读书/第一财经/游研社/财联社/快手/好游快爆实时热搜
- 指令无需参数，默认返回图片（可改为 text）
- 支持统一 apikey 与单接口独立 apikey
- 每个接口可单独开启/关闭
- 支持自定义多时段定时推送热搜到指定群组，可选合并转发。

## 指令
- 抖音热搜
- 知乎热搜
- 微博热搜
- 百度热搜
- 懂车帝热搜
- 哔哩哔哩热搜
- 腾讯热搜
- 头条热搜
- 夸克热搜
- 猫眼票房
- 豆瓣热榜 (指令: 豆瓣 电影/国内剧/全球剧/国内综艺/全球综艺)
- 36氪热搜 (指令: 36氪 人气/视频/热议/收藏)
- 51CTO热搜
- 52破解热搜 (指令: 52破解 热帖/精华/回复/技术)
- AcFun热搜 (指令: AcFun 综合/视频/番剧/文章)
- CSDN热搜
- HelloGitHub热搜 (指令: HelloGitHub c/c++/python/java/go/rust/js/ts/php/css)
- 米游社热搜 (指令: 米游社 [原神/崩坏3/崩坏星穹铁道/绝区零] [同人/酒馆/攻略/硬核])
- 爱范儿热搜
- IT之家热搜 (指令: IT之家 热榜/最新)
- 掘金热搜 (指令: 掘金 全站/后端/前端/Android/iOS/人工智能/开发工具/代码人生/阅读)
- 网易新闻热搜
- 新浪新闻热搜 (指令: 新浪新闻 热议/视频/娱乐/AI/汽车/育儿/时尚/旅游/ESG)
- 少数派热搜 (指令: 少数派 应用/生活/效率/播客)
- 澎湃新闻热搜
- 气象预警 (指令: 气象预警 [省份]，默认全国)
- 微信读书热搜 (指令: 微信读书 热搜/新书/小说/总榜)
- 第一财经热搜
- 游研社热搜
- 财联社热搜
- 快手热搜
- 好游快爆热搜
- 热搜帮助


## 配置
在 AstrBot 插件配置中填写以下项：

- `api_key`：全局统一 API 密钥，所有接口共享（请到柠柚API https://api.nycnm.cn 注册账号获取）

- `enable_douyin`：开启或关闭抖音热搜
- `douyin_api`：抖音接口地址（默认 `https://api.nycnm.cn/api/v2/douyinrs`）
- `douyin_format`：抖音返回格式，`text|image`（默认 `image`）

- `enable_zhihu`：开启或关闭知乎热搜
- `zhihu_api`：知乎接口地址（默认 `https://api.nycnm.cn/api/v2/zhihu`）
- `zhihu_format`：知乎返回格式，`text|image`（默认 `image`）

- `enable_weibo`：开启或关闭微博热搜
- `weibo_api`：微博接口地址（默认 `https://api.nycnm.cn/api/v2/wb`）
- `weibo_format`：微博返回格式，`text|image`（默认 `image`）

- `enable_baidu`：开启或关闭百度热搜
- `baidu_api`：百度接口地址（默认 `https://api.nycnm.cn/api/v2/baidu`）
- `baidu_type`：百度榜单类型 `hot|teleplay|tieba`（默认 `hot`）
- `baidu_format`：百度返回格式，`text|image`（默认 `image`）

- `enable_dcd`：开启或关闭懂车帝热搜
- `dcd_api`：懂车帝接口地址（默认 `https://api.nycnm.cn/api/v2/dongchedi`）
- `dcd_format`：懂车帝返回格式，`text|image`（默认 `image`）

- `enable_bilibili`：开启或关闭哔哩哔哩热搜
- `bilibili_api`：哔哩哔哩接口地址（默认 `https://api.nycnm.cn/api/v2/bilibilirs`）
- `bilibili_format`：哔哩哔哩返回格式，`text|image`（默认 `image`）

- `enable_toutiao`：开启或关闭头条热搜
- `toutiao_api`：头条接口地址（默认 `https://api.nycnm.cn/api/v2/toutiao`）
- `toutiao_format`：头条返回格式，`text|image`（默认 `image`）

- `enable_tencent`：开启或关闭腾讯热搜
- `tencent_api`：腾讯接口地址（默认 `https://api.nycnm.cn/api/v2/txxw`，使用 `type` 指定返回格式）
- `tencent_format`：腾讯返回格式，`text|image`（默认 `image`）

- `enable_quark`：开启或关闭夸克热搜
- `quark_api`：夸克接口地址（默认 `https://api.nycnm.cn/api/v2/quark`）
- `quark_format`：夸克返回格式，`text|image`（默认 `image`）

- `enable_maoyan`：开启或关闭猫眼票房
- `maoyan_api`：猫眼接口地址（默认 `https://api.nycnm.cn/api/v2/maoyan`）
- `maoyan_type`：猫眼榜单类型 `movie|tv|web|all`（默认 `all`）
  - 不带关键词时默认返回 `hot`（百度）和 `all`（猫眼）内容；
  - 百度可在指令后带中文关键词，如“贴吧”“电视剧”来分别查看 `tieba` 或 `teleplay`；
  - 猫眼可在指令后带中文关键词，如“电影/票房”“电视/收视率”“网剧/网播/网络剧”来查看 `movie/tv/web`；
- `maoyan_format`：猫眼返回格式，`text|image`（默认 `image`）

- `enable_douban`：开启或关闭豆瓣热榜
- `douban_api`：豆瓣接口地址（默认 `https://api.nycnm.cn/api/v2/douban`）
- `douban_format`：豆瓣返回格式，`text|image`（默认 `image`）

- `enable_kr36`：开启或关闭36氪热搜
- `kr36_api`：36氪接口地址（默认 `https://api.nycnm.cn/api/v2/36kr`）
- `kr36_format`：36氪返回格式，`text|image`（默认 `image`）

- `enable_cto51`：开启或关闭51CTO热搜
- `cto51_api`：51CTO接口地址（默认 `https://api.nycnm.cn/api/v2/51cto`）
- `cto51_format`：51CTO返回格式，`text|image`（默认 `image`）

- `enable_pojie52`：开启或关闭52破解热搜
- `pojie52_api`：52破解接口地址（默认 `https://api.nycnm.cn/api/v2/52pojie`）
- `pojie52_format`：52破解返回格式，`text|image`（默认 `image`）

- `enable_acfun`：开启或关闭AcFun热搜
- `acfun_api`：AcFun接口地址（默认 `https://api.nycnm.cn/api/v2/acfun`）
- `acfun_format`：AcFun返回格式，`text|image`（默认 `image`）

- `enable_csdn`：开启或关闭CSDN热搜
- `csdn_api`：CSDN接口地址（默认 `https://api.nycnm.cn/api/v2/csdn`）
- `csdn_format`：CSDN返回格式，`text|image`（默认 `image`）

- `enable_hellogithub`：开启或关闭HelloGitHub热搜
- `hellogithub_api`：HelloGitHub接口地址（默认 `https://api.nycnm.cn/api/v2/hellogithub`）
- `hellogithub_format`：HelloGitHub返回格式，`text|image`（默认 `image`）

- `enable_miyoushe`：开启或关闭米游社热搜
- `miyoushe_api`：米游社接口地址（默认 `https://api.nycnm.cn/api/v2/miyoushe`）
- `miyoushe_format`：米游社返回格式，`text|image`（默认 `image`）

- `enable_ifanr`：开启或关闭爱范儿热搜
- `ifanr_api`：爱范儿接口地址（默认 `https://api.nycnm.cn/api/v2/ifanr`）
- `ifanr_format`：爱范儿返回格式，`text|image`（默认 `image`）

- `enable_ithome`：开启或关闭IT之家热搜
- `ithome_api`：IT之家接口地址（默认 `https://api.nycnm.cn/api/v2/xijiayi`）
- `ithome_format`：IT之家返回格式，`text|image`（默认 `image`）

- `enable_juejin`：开启或关闭掘金热搜
- `juejin_api`：掘金接口地址（默认 `https://api.nycnm.cn/api/v2/juejin`）
- `juejin_format`：掘金返回格式，`text|image`（默认 `image`）

- `enable_netease`：开启或关闭网易新闻热搜
- `netease_api`：网易新闻接口地址（默认 `https://api.nycnm.cn/api/v2/netease`）
- `netease_format`：网易新闻返回格式，`text|image`（默认 `image`）

- `enable_sina`：开启或关闭新浪新闻热搜
- `sina_api`：新浪新闻接口地址（默认 `https://api.nycnm.cn/api/v2/sina`）
- `sina_format`：新浪新闻返回格式，`text|image`（默认 `image`）

- `enable_sspai`：开启或关闭少数派热搜
- `sspai_api`：少数派接口地址（默认 `https://api.nycnm.cn/api/v2/sspai`）
- `sspai_format`：少数派返回格式，`text|image`（默认 `image`）

- `enable_thepaper`：开启或关闭澎湃新闻热搜
- `thepaper_api`：澎湃新闻接口地址（默认 `https://api.nycnm.cn/api/v2/thepaper`）
- `thepaper_format`：澎湃新闻返回格式，`text|image`（默认 `image`）

- `enable_weatheralarm`：开启或关闭气象预警
- `weatheralarm_api`：气象预警接口地址（默认 `https://api.nycnm.cn/api/v2/weatheralarm`）
- `weatheralarm_format`：气象预警返回格式，`text|image`（默认 `image`）

- `enable_weread`：开启或关闭微信读书热搜
- `weread_api`：微信读书接口地址（默认 `https://api.nycnm.cn/api/v2/weread`）
- `weread_format`：微信读书返回格式，`text|image`（默认 `image`）

- `enable_yicai`：开启或关闭第一财经热搜
- `yicai_api`：第一财经接口地址（默认 `https://api.nycnm.cn/api/v2/yicai`）
- `yicai_format`：第一财经返回格式，`text|image`（默认 `image`）

- `enable_yystv`：开启或关闭游研社热搜
- `yystv_api`：游研社接口地址（默认 `https://api.nycnm.cn/api/v2/yystv`）
- `yystv_format`：游研社返回格式，`text|image`（默认 `image`）

- `enable_cls`：开启或关闭财联社热搜
- `cls_api`：财联社接口地址（默认 `https://api.nycnm.cn/api/v2/cls`）
- `cls_format`：财联社返回格式，`text|image`（默认 `image`）

- `enable_kuaishou`：开启或关闭快手热搜
- `kuaishou_api`：快手接口地址（默认 `https://api.nycnm.cn/api/v2/kuaishou`）
- `kuaishou_format`：快手返回格式，`text|image`（默认 `image`）

## 定时推送与群组配置说明

- `groups`：接收定时推送的群组唯一标识符列表。
- `push_time`：定时推送时间，使用 AstrBot 所在服务或容器的本地时间。格式为 `HH:MM`，支持英文或中文逗号分隔（如 `08:30,08:31`），留空则不推送。只在配置的分钟内触发，同一进程内热重载不会重复触发同一时间点。
- `push_items`：选择要定时推送的热搜平台（如 `["weibo", "baidu"]`）。
- `forward_message`：定时推送使用合并转发，默认关闭。开启后，OneBot（`aiocqhttp`）群内本次热搜合为一条消息，每个热搜平台占一个节点，保留文本或图片格式；其他适配器仍逐条发送。此设置不影响手动查询。

从旧版升级后，建议完整重启 AstrBot 进程一次，以清除旧版可能遗留的定时任务。

**群聊唯一标识符说明：**
群聊唯一标识符分为: `前缀:中缀:后缀`

下面是所有可选的群组唯一标识符前缀:
| 平台                                | 群组唯一标识符前缀     |
|-------------------------------------|------------------------|
| qq, napcat, Lagrange 之类的         | aiocqhttp              |
| qq 官方 bot                         | qq_official            |
| telegram                            | telegram               |
| 钉钉                                | dingtalk               |
| wechatpadpro微信                    | wechatpadpro           |
| gewechat 微信(虽然已经停止维护)     | gewechat               |
| lark                                | lark                   |
| qq webhook 方法                     | qq_official_webhook    |
| astrbot 网页聊天界面                | webchat                |

下面是所有可选的群组唯一标识符中缀:
| 群组唯一标识符中缀   | 描述       |
|----------------------|------------|
| GroupMessage         | 群组消息   |
| FriendMessage        | 私聊消息   |
| OtherMessage         | 其他消息   |

前缀为`机器人名称`，中缀为`GroupMessage`，后缀为`QQ群号或QQ号`
最终组合结果类似：
```text
CoCo机器人:GroupMessage:QQ群号或QQ号
```

## 依赖
- `aiohttp`

## 使用说明
- 直接发送中文指令即可，不需要携带参数
- 若接口返回图片，将以图片形式发送；返回文本时按各平台配置输出
