# 实时热搜插件（astrbot_plugin_hotsearch）

## 功能
- 聚合抖音/小红书/知乎/微博/百度/懂车帝/哔哩哔哩/腾讯/头条/猫眼票房/夸克/豆瓣/36氪/51CTO/52破解/AcFun/CSDN/HelloGitHub/米游社/爱范儿/IT之家/掘金/网易新闻/新浪新闻/少数派/澎湃新闻/气象预警/微信读书/第一财经/游研社实时热搜
- 指令无需参数，默认返回图片（可改为 text）
- 支持统一 apikey 与单接口独立 apikey
- 每个接口可单独开启/关闭

## 指令
- 抖音热搜
- 小红书热搜
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
- 热搜帮助

## 配置
在 AstrBot 插件配置中填写以下项（已在 `_conf_schema.json` 定义，开关写法与 `astrbot_scheduler` 保持一致）：

- `api_key`：全局统一 API 密钥，所有接口共享（请到柠柚API https://api.nycnm.cn 注册账号获取）

- `enable_douyin`：开启或关闭抖音热搜
- `douyin_api`：抖音接口地址（默认 `https://api.nycnm.cn/API/douyinrs.php`）
- `douyin_format`：抖音返回格式，`text|image`（默认 `image`）

- `enable_xhs`：开启或关闭小红书热搜
- `xhs_api`：小红书接口地址（默认 `https://api.nycnm.cn/API/xhsrs.php`）
- `xhs_format`：小红书返回格式，`text|image`（默认 `image`）

- `enable_zhihu`：开启或关闭知乎热搜
- `zhihu_api`：知乎接口地址（默认 `https://api.nycnm.cn/API/zhihu.php`）
- `zhihu_format`：知乎返回格式，`text|image`（默认 `image`）

- `enable_weibo`：开启或关闭微博热搜
- `weibo_api`：微博接口地址（默认 `https://api.nycnm.cn/API/wb.php`）
- `weibo_format`：微博返回格式，`text|image`（默认 `image`）

- `enable_baidu`：开启或关闭百度热搜
- `baidu_api`：百度接口地址（默认 `https://api.nycnm.cn/API/baidu.php`）
- `baidu_type`：百度榜单类型 `hot|teleplay|tieba`（默认 `hot`）
- `baidu_format`：百度返回格式，`text|image`（默认 `image`）

- `enable_dcd`：开启或关闭懂车帝热搜
- `dcd_api`：懂车帝接口地址（默认 `https://api.nycnm.cn/API/dongchedi.php`）
- `dcd_format`：懂车帝返回格式，`text|image`（默认 `image`）

- `enable_bilibili`：开启或关闭哔哩哔哩热搜
- `bilibili_api`：哔哩哔哩接口地址（默认 `https://api.nycnm.cn/API/bilibilirs.php`）
- `bilibili_format`：哔哩哔哩返回格式，`text|image`（默认 `image`）

- `enable_toutiao`：开启或关闭头条热搜
- `toutiao_api`：头条接口地址（默认 `https://api.nycnm.cn/API/toutiao.php`）
- `toutiao_format`：头条返回格式，`text|image`（默认 `image`）

- `enable_tencent`：开启或关闭腾讯热搜
- `tencent_api`：腾讯接口地址（默认 `https://api.nycnm.cn/API/txxw.php`，使用 `type` 指定返回格式）
- `tencent_format`：腾讯返回格式，`text|image`（默认 `image`）

- `enable_quark`：开启或关闭夸克热搜
- `quark_api`：夸克接口地址（默认 `https://api.nycnm.cn/API/quark.php`）
- `quark_format`：夸克返回格式，`text|image`（默认 `image`）

- `enable_maoyan`：开启或关闭猫眼票房
- `maoyan_api`：猫眼接口地址（默认 `https://api.nycnm.cn/API/maoyan.php`）
- `maoyan_type`：猫眼榜单类型 `movie|tv|web|all`（默认 `all`）
  - 不带关键词时默认返回 `hot`（百度）和 `all`（猫眼）内容；
  - 百度可在指令后带中文关键词，如“贴吧”“电视剧”来分别查看 `tieba` 或 `teleplay`；
  - 猫眼可在指令后带中文关键词，如“电影/票房”“电视/收视率”“网剧/网播/网络剧”来查看 `movie/tv/web`；
- `maoyan_format`：猫眼返回格式，`text|image`（默认 `image`）

- `enable_douban`：开启或关闭豆瓣热榜
- `douban_api`：豆瓣接口地址（默认 `https://api.nycnm.cn/API/douban.php`）
- `douban_format`：豆瓣返回格式，`text|image`（默认 `image`）

- `enable_kr36`：开启或关闭36氪热搜
- `kr36_api`：36氪接口地址（默认 `https://api.nycnm.cn/API/36kr.php`）
- `kr36_format`：36氪返回格式，`text|image`（默认 `image`）

- `enable_cto51`：开启或关闭51CTO热搜
- `cto51_api`：51CTO接口地址（默认 `https://api.nycnm.cn/API/51cto.php`）
- `cto51_format`：51CTO返回格式，`text|image`（默认 `image`）

- `enable_pojie52`：开启或关闭52破解热搜
- `pojie52_api`：52破解接口地址（默认 `https://api.nycnm.cn/API/52pojie.php`）
- `pojie52_format`：52破解返回格式，`text|image`（默认 `image`）

- `enable_acfun`：开启或关闭AcFun热搜
- `acfun_api`：AcFun接口地址（默认 `https://api.nycnm.cn/API/acfun.php`）
- `acfun_format`：AcFun返回格式，`text|image`（默认 `image`）

- `enable_csdn`：开启或关闭CSDN热搜
- `csdn_api`：CSDN接口地址（默认 `https://api.nycnm.cn/API/csdn.php`）
- `csdn_format`：CSDN返回格式，`text|image`（默认 `image`）

- `enable_hellogithub`：开启或关闭HelloGitHub热搜
- `hellogithub_api`：HelloGitHub接口地址（默认 `https://api.nycnm.cn/API/hellogithub.php`）
- `hellogithub_format`：HelloGitHub返回格式，`text|image`（默认 `image`）

- `enable_miyoushe`：开启或关闭米游社热搜
- `miyoushe_api`：米游社接口地址（默认 `https://api.nycnm.cn/API/miyoushe.php`）
- `miyoushe_format`：米游社返回格式，`text|image`（默认 `image`）

- `enable_ifanr`：开启或关闭爱范儿热搜
- `ifanr_api`：爱范儿接口地址（默认 `https://api.nycnm.cn/API/ifanr.php`）
- `ifanr_format`：爱范儿返回格式，`text|image`（默认 `image`）

- `enable_ithome`：开启或关闭IT之家热搜
- `ithome_api`：IT之家接口地址（默认 `https://api.nycnm.cn/API/xijiayi.php`）
- `ithome_format`：IT之家返回格式，`text|image`（默认 `image`）

- `enable_juejin`：开启或关闭掘金热搜
- `juejin_api`：掘金接口地址（默认 `https://api.nycnm.cn/API/juejin.php`）
- `juejin_format`：掘金返回格式，`text|image`（默认 `image`）

- `enable_netease`：开启或关闭网易新闻热搜
- `netease_api`：网易新闻接口地址（默认 `https://api.nycnm.cn/API/netease.php`）
- `netease_format`：网易新闻返回格式，`text|image`（默认 `image`）

- `enable_sina`：开启或关闭新浪新闻热搜
- `sina_api`：新浪新闻接口地址（默认 `https://api.nycnm.cn/API/sina.php`）
- `sina_format`：新浪新闻返回格式，`text|image`（默认 `image`）

- `enable_sspai`：开启或关闭少数派热搜
- `sspai_api`：少数派接口地址（默认 `https://api.nycnm.cn/API/sspai.php`）
- `sspai_format`：少数派返回格式，`text|image`（默认 `image`）

- `enable_thepaper`：开启或关闭澎湃新闻热搜
- `thepaper_api`：澎湃新闻接口地址（默认 `https://api.nycnm.cn/API/thepaper.php`）
- `thepaper_format`：澎湃新闻返回格式，`text|image`（默认 `image`）

- `enable_weatheralarm`：开启或关闭气象预警
- `weatheralarm_api`：气象预警接口地址（默认 `https://api.nycnm.cn/API/weatheralarm.php`）
- `weatheralarm_format`：气象预警返回格式，`text|image`（默认 `image`）

- `enable_weread`：开启或关闭微信读书热搜
- `weread_api`：微信读书接口地址（默认 `https://api.nycnm.cn/API/weread.php`）
- `weread_format`：微信读书返回格式，`text|image`（默认 `image`）

- `enable_yicai`：开启或关闭第一财经热搜
- `yicai_api`：第一财经接口地址（默认 `https://api.nycnm.cn/API/yicai.php`）
- `yicai_format`：第一财经返回格式，`text|image`（默认 `image`）

- `enable_yystv`：开启或关闭游研社热搜
- `yystv_api`：游研社接口地址（默认 `https://api.nycnm.cn/API/yystv.php`）
- `yystv_format`：游研社返回格式，`text|image`（默认 `image`）

## 依赖
- `aiohttp`

## 使用说明
- 直接发送中文指令即可，不需要携带参数
- 若接口返回图片，将以图片形式发送；返回文本时按各平台配置输出
