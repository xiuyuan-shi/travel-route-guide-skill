# Travel Route Guide Skill

一个面向 Codex 的城市旅行攻略 Skill。输入出发城市、目的城市和旅行天数，即可生成可执行的中文旅行计划与手机单文件 HTML；在日期和需求明确时，还可加入实时天气，并按需发布公开分享网页。

## 能做什么

- 按天规划景点顺序、时段、交通方式和体力删减项
- 生成全程与每日路线地图，区分步行、乘车和示意线路
- 把餐厅安排到顺路餐次，并生成美食速查
- 补充住宿候选、分项预算、行前清单、避坑和应急方案
- 日期明确时读取实时天气，并给出逐日对策
- 生成手机优先的单文件 HTML，核心行程和内嵌地图可离线查看
- 在用户明确需要时，将攻略发布为公共网页并验证匿名访问

## 安装

使用 Codex 自带的 GitHub Skill 安装脚本：

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-installer/scripts/install-skill-from-github.py" \
  --repo xiuyuan-shi/travel-route-guide-skill \
  --path travel-route-guide \
  --method git
```

`--method git` 可避开部分 macOS Python 环境的证书链问题。安装后重启 Codex，使新 Skill 生效。如果本机已经存在同名 Skill，请先自行备份或改名；安装器不会覆盖已有目录。

## 使用示例

```text
使用 $travel-route-guide，从杭州出发去苏州，玩 3 天
```

```text
使用 $travel-route-guide，从杭州去伊犁玩 7 天，生成手机网页版，并发布一个公共访问链接
```

如果提供出发日期、已订车次或航班、住宿、预算、同行人数和明确偏好，结果会更准确。没有具体日期时，Skill 会用 `Day 1` 到 `Day N` 编排行程，不会虚构天气、节日安排或已订票信息。

## 直接使用生成器

Skill 会先把研究结果整理成结构化的 `trip.json`，再生成 HTML。仓库附带的示例可以直接运行：

```bash
python3 travel-route-guide/scripts/build_guide.py \
  travel-route-guide/references/example-trip.json \
  --out outputs/travel-guide.html
```

数据字段和地图要求见：

- [`data-contract.md`](travel-route-guide/references/data-contract.md)
- [`maps.md`](travel-route-guide/references/maps.md)
- [`publishing.md`](travel-route-guide/references/publishing.md)

## 设计边界

- 实时票价、库存、开放时间、天气和商家状态需要联网核对，并显示来源或核对时间。
- 地图直线只能标为示意；真实步行路线需要可靠的道路几何数据。
- 页面可离线查看核心内容，实时天气和外部导航链接仍需要网络。
- Skill 只在用户明确要求时发布公开网页，不包含任何账号凭据。

## 仓库结构

```text
travel-route-guide/
├── SKILL.md
├── agents/openai.yaml
├── assets/
├── references/
└── scripts/
```

## 许可

本仓库原创内容使用 [MIT License](LICENSE)。随 Skill 分发的 Leaflet 文件保留其 BSD 2-Clause 许可，详见 [`LEAFLET-LICENSE.txt`](travel-route-guide/assets/LEAFLET-LICENSE.txt) 和 [第三方说明](THIRD_PARTY_NOTICES.md)。地图与数据提供方的内容仍受各自条款约束。
