# 寰宇古今 · Chronica

[English](README.md)

寰宇古今（Chronica）是一套按地区组织的历史地图。第一个地区是“欧陆古今”（Europe Through the Ages），覆盖公元前 700 年到公元 2000 年的欧洲，内容包括：
- 44 份边界快照，以及每两份相邻快照之间易手的领土；
- 296 条事件；
- 10 个故事章节。每一步都有简短导语，也有适合细读的全文。

界面和全部内容都有中文和英文。

页面代码本身与地区无关：地区特有的东西都放在 `regions/` 下该地区的文件夹里。所以以后增加东亚、中东等地区时，只要在欧洲旁边新建一个文件夹，不必改页面代码。

**在线访问：https://c.ilewen.com**

## 功能

- **探索**：拖动时间轴或按播放，看边界变化；斜线区域是本期的领土变化。
  - 点击一个政权，看它的名称沿革和面积曲线。
  - 点击时间轴左侧的“各国疆域”按钮可以展开泳道。点一条彩色泳道，可以跟着一个谱系（比如法国、俄罗斯）看它跨越历次改名的变化。
- **故事**：每章是一串会移动地图的步骤，例如“雅典的世纪”“拿破仑时代”。点“阅读全文”进入阅读视图：右边是全章正文，左边的地图跟着正在读的段落变化。
- **对比**：左右两个年份并排，中间的分隔线可以拖动；侧栏列出扩张、收缩最多的政权和期间的事件。
- **搜索**（按 `/`）：可以搜政权、谱系、城市（旧名也行）、事件和故事，也认常见俗称，比如“神罗”“一战”“HRE”“WWII”。
- **链接**：地址栏始终反映当前视图，可以直接复制分享（见[链接](#链接)）。

## 本地预览

不需要构建，除了 Python 3 也不用安装别的东西。先获取代码：

```bash
git clone https://github.com/Snowpine/chronica.git
```

页面用 `fetch` 读取数据，不能直接双击打开，需要一个本地服务器。在任何目录下都可以运行：

```bash
python3 path/to/chronica/scripts/serve.py
```

然后打开 http://localhost:8000 ，按 Ctrl+C 停止。端口被占用时可以换一个：`serve.py 8001`。

## 语言

页面按下面的顺序选择语言：

1. 地址里的 `?lang=<代码>`，例如 `http://localhost:8000/?lang=en`；
2. 用户上次用语言按钮选的语言（保存在浏览器里）；
3. 浏览器偏好语言里第一个本站有的语言（所有 `zh-*` 都算中文）；
4. 都没有就用英文。

右上角的语言按钮在 `index.html` 的 `LOCALES` 列出的语言之间轮换。

## 目录结构

```
chronica/
  index.html                 页面和全部前端代码，不含任何地区或语言的内容
  favicon.svg  og.png        网站图标，以及分享链接时显示的预览图
  locales/
    en.json  zh.json         界面文字（按钮、标签、帮助），所有地区共用
  regions/
    europe/
      region.json            地图范围、投影、初始视野和年份、时代、时间刻度、谱系颜色、对比预设
      borders.json           边界快照（TopoJSON）、每期变化、面积序列           —— 由脚本生成
      physical.json          河流、湖泊、山脉                                    —— 由脚本生成
      events.json            事件：[键, 年份, 纬度, 经度, 类型]
      stories.json           故事章节：每一步的年份、地图范围、高亮的政权、引用的事件
      cities.json            城市：[纬度, 经度, 级别, [[起始年份, 名称键], …]]
      locales/
        en.json  zh.json     该地区的内容：各类名称、时代、事件、故事、搜索别名
      polities.py            怎样读边界数据源：用哪些快照、谱系、数据修正
      physical.py            画哪些河流和山脉、给哪些加标注
  scripts/
    make_data.py             从原始数据重新生成某个地区的 borders.json 或 physical.json
    build.py                 make_data.py 的一步：合并政权、计算变化和面积序列
    build_physical.py        make_data.py 的一步：挑选河流、湖泊、山脉
    check.py                 检查各地区和各语言有没有缺漏
    serve.py                 本地预览服务器
  wrangler.jsonc             Cloudflare 部署配置（见“部署”）
  .assetsignore              部署时不上传的文件
  LICENSE                    GPL-3.0
```

年份一律是整数，公元前为负数（`-500` 即公元前 500 年），没有 0 年。

## region.json

| 字段 | 含义 |
|---|---|
| `window` | `[[西, 南], [东, 北]]`，单位是度。原始数据裁剪到这个范围，地图上的海也画在这个范围里。 |
| `projection` | [d3-geo](https://d3js.org/d3-geo) 的投影名（去掉 `geo` 前缀）和要设置的参数，例如 `{"type": "ConicConformal", "parallels": [40, 62], "rotate": [-15, 0]}`。 |
| `focus` | 初始视野必须包含的点，地图取包住它们的最小视野。 |
| `core` | 可选，`[[西, 南], [东, 北]]`。落在这个范围里的领土变化排在边缘地区的变化前面。默认等于 `window`。 |
| `start`、`end` | 打开时显示的年份，以及时间轴的终点。时间轴的起点是第一份边界快照。 |
| `eras` | 时代分界年份，从第一份快照的年份到 `end`；时代名称写在各语言文件里。 |
| `periods` | 可选。由若干完整时代组成的大时期，写法是从 `eras` 里取的分界年份（欧洲：古代、中世纪、近现代）。时间轴太窄、放不下某个时代的名称时（比如在手机上），这个时期的几个时代会合并成一段，标上时期的名称。 |
| `scale` | 时间轴刻度：一串 `[年份, 比例]`，从 `[起始年, 0]` 到 `[end, 1]`，中间线性。史料稀疏的时期可以给小一点的比例。 |
| `denseFrom` | 可选。这一年以前，“最近发生的事件”回溯 100 年而不是 25 年，时间轴按半个世纪而不是十年统计事件。 |
| `lineages` | `{谱系 id: [浅色主题颜色, 深色主题颜色]}`，对应 `polities.py` 里的每个谱系，顺序就是时间轴泳道的顺序。 |
| `presets` | 可选，对比模式的快捷年份对 `[[左, 右], …]`；说明文字写在各语言文件里。 |

## 语言文件

每种语言由两个文件合成：
- `locales/<语言>.json`：界面文字；
- `regions/<id>/locales/<语言>.json`：该地区的内容。

地区文件的每一部分叠加到界面文件的同名部分上。地区文件的 `ui` 只放 `title`、`subtitle` 和 `map`（地图的无障碍名称）三项，补进界面文字里。

**界面文件**（`locales/<语言>.json`）：

- `meta`：
  - `code`：语言代码；
  - `lang`：BCP 47 标签，如 `fr`；
  - `name`：该语言的自称，如 `Français`；
  - `area`：面积格式。`number` 按当地习惯分组数字，`wan` 以“万”为单位。
- `ui`：界面文字。
  - `{y}`、`{name}` 这类占位符要保留。
  - 少数条目（`keys`、`credit`、`changeRow`）里有 HTML，或者会插入 HTML，保持结构不变。
  - `bc` 是公元前年份的写法，例如中文 `前{y}`、英文 `{y} BC`。
- `types`：事件类型 `war`、`treaty`、`politics`、`faith`、`culture`、`plague` 的名称。新增类型还要在 `index.html` 的 `TYPES` 里给它一个地图符号。

**地区文件**（`regions/<id>/locales/<语言>.json`）：

- `ui`：`title`、`subtitle`、`map`。
- `eras`：`region.json` 里每个时代的名称。
- `erasShort`（可选）：每个时代的简称（没有就写 `""`），全称放不下时使用。
- `periods`：`region.json` 里每个时期的名称。
- `lanes`：时间轴泳道的短名，用 `/` 分隔几个说法，窄屏只显示最后一个。
- `lineages`：谱系全名。
- `notes`：个别快照的数据说明，按年份为键。
- `presets`：对比预设的说明，键是 `"<左>-<右>"`。
- `names`、`cities`、`rivers`、`ranges`：各类地名，按名称键（见下文）。
- `short`（可选）：地图标注用的简称，全名放不下时才用，例如 `Polish–Lithuanian Commonwealth` → “波兰立陶宛”。名称末尾的括号注释（如“（法属）”）会自动去掉，不必另列。
- `events`：`{ 事件键: [标题, 说明] }`。
- `stories`：`{ 章节 id: { title, lede, steps: [[标题, 导语, 全文?], …] } }`。
  - 步数必须和 `stories.json` 一致。
  - 全文可选，格式是 `{ "p": [段落, …], "facts": [[要点, 内容], …] }`。
  - 一章里只要有一步带全文，故事卡片上就会出现“阅读全文”，可以进入阅读视图。
  - 欧洲的 10 章都写了全文：每步三段，中文约 500 字。
- `aliases`（可选）：搜索也认的俗称和别名，例如“神罗”“沙俄”“HRE”“WWII”。
  - 分四组：`names`（按政权名称键）、`lineages`（按谱系 id）、`events`（按事件键）、`stories`（按章节 id）。
  - 每项是一个字符串数组。
  - 非英文界面也能搜到英文别名。
  - 结果的副标题会显示命中的别名，所以可以把“工业革命”这类主题词挂在代表性事件上。

### 名称键

`borders.json` 里的政权名称不是某种语言的文字，而是键：

- 一般就是原始数据的 `NAME`，例如 `Tsardom of Muscovy`、`Holy Roman Empire`。
- 名称随年份变化的，键后面加 `|标签`，例如 `Germany|empire`（1914 年及以前）、`Germany|weimar`、`Germany|nazi`。规则写在该地区 `polities.py` 的 `VARIANTS` 里。
- `_none` 表示无主或未记载的地区。

显示名称时，先查当前语言的 `names[键]`，查不到再去掉 `|标签` 查一次，仍然查不到就显示原始英文名。所以漏译不会出错，只会显示英文。

古代快照里有很多民族和考古学文化（凯尔特人、骨灰瓮文化等）。它们不是国家，原始数据也常常这一期画、下一期不画。`polities.py` 的 `PEOPLES` 列出这类名称，它们：
- 在地图上用浅色和斜体显示；
- 范围变化不算作“变化”；
- 在对比模式里不计入扩张和收缩。

### 缺漏时的处理

- 缺界面文字：显示它的键。
- 缺政权、河流、山脉名称：显示原始英文名。
- 地区没有当前语言的文件：在译好的界面里显示该地区的英文内容。

这些缺漏都可以用 `scripts/check.py` 查出来。

## 增加一种语言

1. 复制 `locales/en.json` 为 `locales/<代码>.json`（例如 `fr.json`），翻译 `meta`、`ui`、`types`。
2. 对每个地区，复制 `regions/<id>/locales/en.json` 为 `<代码>.json` 并翻译。没翻译之前，该地区显示英文内容。
3. 在 `index.html` 的 `LOCALES` 里加上它：`fr: ["Français", "fr"]`，也就是语言自称和 BCP 47 标签。
4. 字体：页面 CSS 默认按中文排版，其他语言一律用拉丁字体和较紧的字距（即 `:root:not([lang|="zh"])` 这组规则）。日文、阿拉伯文这类其他文字的语言，需要在那里另加 `:root[lang|="xx"]` 规则。
5. 运行 `python3 scripts/check.py`，按提示补全。

## 增加一个地区

1. **定范围和快照。** 选好 `window` 和要用的 [historical-basemaps](https://github.com/aourednik/historical-basemaps) 年份，参照欧洲的 `region.json` 写一份 `regions/<id>/region.json`。
2. **写数据说明。** 把 `regions/europe/polities.py` 和 `physical.py` 复制到新文件夹，改写里面的表。每张表都要有，但可以是空的。
   - `polities.py` 里的表：
     - `YEARS`：用哪些快照；
     - `LINEAGE_NAMES`：哪些名称属于同一谱系，id 要和 `region.json` 的 `lineages` 一致；
     - `OVERLORD_LINEAGES`：宗主名称的写法和谱系成员名称不同时，把它对应到谱系；
     - `IDENTITY_GROUPS`：哪些名称算同一个政权，改名不算领土变化；
     - 修正原始数据标注的 `RENAMES`、`GROUP_RENAMES`、`OVERLORD_RENAMES`、`NOT_POLITIES`；
     - `PEOPLES`、`VARIANTS`；
     - 几何修正 `UNNAMED`、`REASSIGN`。
   - `physical.py`：要画和标注的河流、山脉，用 Natural Earth 的名称。
3. **生成数据**（见[重新生成数据](#重新生成数据)）：
   ```bash
   python3 scripts/make_data.py <id> borders  <historical-basemaps>/geojson
   ```
   ```bash
   python3 scripts/make_data.py <id> physical <natural-earth-vector>/geojson
   ```
   生成时会打印每期最大的几处变化。如果有明显不合理的，通常是原始数据的标注需要在 `polities.py` 里修正。
4. **写内容。** 加上 `events.json`、`stories.json`、`cities.json`，开始时都可以是 `[]`。再写 `locales/en.json`，至少要有 `ui`、`eras`、`lanes`、`lineages`。其他语言可以以后再加。
5. **登记地区。** 把 id 加进 `index.html` 的 `REGIONS`，打开 `http://localhost:8000/?region=<id>` 查看。列表里的第一个地区是默认地区。现在还没有切换地区的菜单，有了第二个地区再加。
6. **检查。** 运行 `python3 scripts/check.py <id>`。它会列出这些问题：
   - 未翻译的名称；
   - 步数对不上的故事；
   - 不存在的事件键；
   - 和 `region.json` 不一致的谱系；
   - 其他问题。

## 链接

地址栏 `#` 后面的部分跟着当前视图变化：

- **探索：**
  - `#1650`、`#500bc`：某一年，公元前写作 `bc`。
  - `#1914/state:Serbia`、`#1650/lineage:poland`、`#1215/event:magna-carta`：某一年，同时选中一个政权、谱系或事件（键见该地区的数据文件）。
- **故事：**
  - `#napoleon`、`#napoleon/3`：某个章节，及其第几步。
  - `#napoleon/3/read`：在阅读视图里打开这一步。
  - `#stories`：章节列表。
- **对比：** `#compare-1914-1920`：对比两年，后面也可以加 `/state:…` 等选择。

查询参数写在 `#` 前面：`?lang=en`、`?region=europe`。

## 重新生成数据

需要：
- Python 3，并装有 shapely 2；
- [mapshaper](https://github.com/mbloch/mapshaper)（`npm install -g mapshaper`，或者用环境变量 `MAPSHAPER` 指定路径）。

每个文件一条命令，完成裁剪、合并、计算变化和打包；中间文件放在 `work/<地区>/`：

```bash
python3 scripts/make_data.py europe borders  <historical-basemaps>/geojson
```

```bash
python3 scripts/make_data.py europe physical <natural-earth-vector>/geojson
```

### 边界：`borders.json`

数据来源是 https://github.com/aourednik/historical-basemaps 的 `geojson/world_<年份>.geojson`，公元前为 `world_bc<年份>.geojson`。`make_data.py borders` 依次：

1. **裁剪简化。** 用 mapshaper 把 `YEARS` 里的每份快照裁剪到该地区的 `window`，并做简化。
2. **运行 `scripts/build.py`**，按该地区的 `polities.py`：
   - 合并同一政权的多边形，生成名称键，标出谱系和宗主；
   - 修正原始数据的已知错误（`RENAMES`、`OVERLORD_RENAMES`、`UNNAMED`、`REASSIGN`）；
   - 计算每两份相邻快照之间各政权从各邻国得到的领土（小于 6000 km² 的不计）；
   - 生成各政权和各谱系的面积序列。
3. **打包。** 把各年和这些元数据合并成一个 TopoJSON 文件。

新出现的名称键需要在各语言文件的 `names` 里补上翻译，不补就显示原始英文名。`scripts/check.py` 会列出这些名称。

### 河流、湖泊、山脉：`physical.json`

数据来源是 [Natural Earth](https://www.naturalearthdata.com/)（公有领域），用的是 https://github.com/nvkelso/natural-earth-vector 的 `geojson/` 下这三个文件：
- `ne_10m_rivers_lake_centerlines`；
- `ne_50m_lakes`；
- `ne_10m_geography_regions_polys`。

`make_data.py physical` 按该地区的 `physical.py` 运行 `scripts/build_physical.py`：保留列出的河流和山脉，以及范围内所有湖泊，再简化打包。

## 部署

网站全是静态文件，任何静态托管都可以。线上版本部署在 Cloudflare 上，是一个只提供静态文件的 Worker：
- `wrangler.jsonc` 写了 Worker 的名字和自定义域名；
- `.assetsignore` 规定只上传页面、图标和预览图，以及语言和地区数据。脚本、Python 表格和 README 都不上传。

部署自己的副本时，把 `wrangler.jsonc` 里的 `routes` 改成自己的域名（或者删掉，改用 workers.dev 地址），然后运行：

```bash
npx wrangler deploy
```

## 参与贡献

欢迎指正和补充，可以开 issue 或提交 pull request。

- **史实更正：** 请注明出处。
- **数据或翻译：** 提交前运行 `python3 scripts/check.py`，确认没有报错。

## 数据来源与许可

本项目（代码和数据）以 [GPL-3.0](LICENSE) 发布。

- 边界：[aourednik/historical-basemaps](https://github.com/aourednik/historical-basemaps)，GPL-3.0。`borders.json` 是它的衍生数据。
- 河流、湖泊、山脉：[Natural Earth](https://www.naturalearthdata.com/)，公有领域。
- 事件、故事、译名为本项目整理。
- 程序库：[d3](https://d3js.org/) 和 [TopoJSON client](https://github.com/topojson/topojson-client)（均为 ISC 许可），从 cdnjs 加载。
- 字体：Spectral、Noto Sans SC、IBM Plex Sans Condensed、站酷小薇（ZCOOL XiaoWei），来自 Google Fonts（SIL 开源字体许可）。
