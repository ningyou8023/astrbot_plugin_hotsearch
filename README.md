# 实时热搜插件（astrbot_plugin_hotsearch）

## 功能
- 聚合抖音/小红书/知乎/微博/百度/懂车帝/哔哩哔哩/腾讯/头条/猫眼票房实时热搜
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
- 猫眼票房
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

- `enable_maoyan`：开启或关闭猫眼票房
- `maoyan_api`：猫眼接口地址（默认 `https://api.nycnm.cn/API/maoyan.php`）
- `maoyan_type`：猫眼榜单类型 `movie|tv|web|all`（默认 `all`）
  - 不带关键词时默认返回 `hot`（百度）和 `all`（猫眼）内容；
  - 百度可在指令后带中文关键词，如“贴吧”“电视剧”来分别查看 `tieba` 或 `teleplay`；
  - 猫眼可在指令后带中文关键词，如“电影/票房”“电视/收视率”“网剧/网播/网络剧”来查看 `movie/tv/web`；
- `maoyan_format`：猫眼返回格式，`text|image`（默认 `image`）

## 依赖
- `aiohttp`

## 使用说明
- 直接发送中文指令即可，不需要携带参数
- 若接口返回图片，将以图片形式发送；返回文本时按各平台配置输出