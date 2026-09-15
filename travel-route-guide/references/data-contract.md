# 数据格式与命令

`python3 SKILL_DIR/scripts/build_guide.py trip.json --out outputs/旅行攻略.html`

仅依赖 Python 标准库；将 SKILL_DIR 替换为本 Skill 目录。输入和输出路径均由当前任务决定，勿硬编码上一次城市、用户名或仓库。

最小结构参考 `example-trip.json`，它是离线测试数据，不可直接当旅游建议交付。

- `trip`: `origin`, `destination`, `duration`（正整数，等于 days 长度）；可选 `title`, `dates`, `summary`, `tags`（字符串数组）, `share_url`（空或已确认的 http/https 公开网址）, `checked_at`。
- `places`: 以稳定 ID 为键的对象。每项 `name`, `lat`, `lon`, `kind`（spot/food/hotel/station）, `description`；可选 `address`, `map_query`, `source_url`。纬度经度为 WGS84。
- `days`: 每项 `title`, `summary`, `stops`, `leg_ids`；可选 `date`, `tip`。每个 stop 含 `time`, `title`, `description`，可选 `place_id`, `food`。food 含 `menu`,`budget`；分店地址与来源放在 place，避免重复来源。
- `legs`: ID 对象，每项 `from`, `to`（place ID）, `mode`（walk/transit/drive）, `status`（schematic/routed）。routed 需要 `geometry: {type:"LineString", coordinates:[[lon,lat],...]}`。schematic 不带 geometry，由端点生成虚线。不要根据交通方式自动把直线当 routed。
- `sections`: 其他出行准备数组，每项 `title`, `body`（纯文本，可含换行）。适合交通确认、预约说明和返程缓冲；已有独立字段的住宿、预算、餐饮、清单、避坑、应急和实时天气不要重复写进 sections。
- `lodging`: 可选住宿候选数组。每项 `place_id`（指向 kind=hotel 的 place）, `label`, `price`, `reason`, `caveat`。`price` 必须带“每间每晚／总价”等口径；实时价格未经核对时在 caveat 写明。导航、地址和来源复用 place。
- `budget`: 可选分项预算对象。`basis`, `total_estimate`, `reserve_note` 为纯文本；`items` 每项含 `label`, `amount`, `note`。住宿按房、其他按人时不能直接相加成一个伪精确总价。
- `food_quick`: 可选美食速查数组。每项 `place_id`（指向 kind=food 的 place）, `when`, `order`, `budget`, `fallback`；用于快速浏览，实际餐次仍写入 day stop。
- `checklist`: 可选数组，每项 `category` 与非空字符串数组 `items`。网页按行程生成本地存储键，勾选只保存在当前浏览器。
- `pitfalls`: 可选数组，每项 `title`, `advice`。只写会改变行动的避坑信息，预约、封闭和交通规则需可追溯。
- `emergencies`: 可选数组，每项 `scenario`, `action`。替代方案优先同片区，至少考虑天气、停业／排队、体力、延误和断网。
- `weather`: 可选实时天气配置。日期明确时填写 `lat`, `lon`（目的地代表点，WGS84）, `timezone`（IANA 名称）, `start_date`, `end_date`（YYYY-MM-DD）；`provider` 目前仅支持 `open-meteo`，可选 `official_url` 指向当地官方预警。页面调用 Open-Meteo 最长 16 日预报；超出范围、失败和缓存都有明确状态。不要写静态“实时天气”数据。
- `sources`: 数组，`label`, `url`，用于可追溯资料。所有链接必须 http/https。
- `basemap`: 可选，内嵌 GeoJSON FeatureCollection；或输入 JSON 同目录下 `basemap_file`。features 的 `properties.kind` 可为 road/coast/boundary/land；可有 name。真实填色陆地仅用于经过核对的 Polygon/MultiPolygon，海岸折线不可直接封闭成陆地。

修改 JSON 后重跑生成器；它不负责联网研究、不核实业务事实、不自动发布。脚本对字段完整性、链接协议和端点做校验；人工仍需审核行程合理性。输入文本按纯文本处理，不支持内嵌HTML。

默认首页显示 Day 1；选日期切换当天时间表。地图显示当天／全程路线；当无基图时明确说明点位关系示意。准备页按存在的数据依次显示实时天气、住宿、预算、美食速查、行前清单、避坑、应急和通用 sections。已发布后将真实返回地址写入 share_url，再重建并发布相同版本，使下载 HTML 也能分享正确链接。
