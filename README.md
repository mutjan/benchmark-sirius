# シリウスの心臓 Benchmark 展示页

评测大模型在零先验自然赏析提示下，对歌曲《シリウスの心臓》的理解深度，涵盖符号识别、元语言密钥、语言深度、信号结构、天文联结、时间推理和 Bonus 补充发现。

---

## 数据文件结构

```
data/
  benchmark.json       # v2.1 自然发现版 Benchmark 定义
  benchmark-v2.2.json  # v2.2 新 Prompt 试验版 Benchmark 定义
  results/             # v2.1 单模型测评源文件：每个模型一份 JSON（人工编辑）
  results-v2.2/        # v2.2 单次测评源文件；同一模型可保留多次尝试
  results.json         # v2.1 页面发布用聚合文件，由 scripts/build_results.py 生成
  results-v2.2.json    # v2.2 页面发布用聚合文件
scripts/
  build_results.py     # 合并指定榜单源文件 -> 指定聚合文件
  validate_results.py  # 校验 v2.1 单模型源文件，不改聚合文件
```

当前页面支持两套榜单：

| 榜单 | Prompt 类型 | Benchmark | 源文件目录 | 聚合文件 | 访问方式 |
|------|-------------|-----------|------------|----------|----------|
| v2.1 | 自然发现版，极简提示词 | `data/benchmark.json` | `data/results/` | `data/results.json` | `?board=v2.1` |
| v2.2 | 新 Prompt 试验版，提示隐藏信息/结构/意象/深层含义 | `data/benchmark-v2.2.json` | `data/results-v2.2/` | `data/results-v2.2.json` | 默认页面 |

---

## 快速启动

```bash
cd benchmark-sirius
python3 -m http.server 8080
# 访问 http://localhost:8080
# 旧 v2.1 榜单： http://localhost:8080/?board=v2.1
```

---

## 添加模型测评结果（v2.1）

在 `data/results/` 下新增一个以模型 `id` 命名的文件，例如 `data/results/gpt-4o-2024-11-20.json`：

```json
{
  "id": "gpt-4o-2024-11-20",
  "model": "GPT-4o",
  "model_version": "gpt-4o-2024-11-20",
  "provider": "OpenAI",
  "api_endpoint": "api.openai.com",
  "test_date": "2026-03-21",
  "notes": "可选备注",
  "scores": {
    "Q1": 1,
    "Q2": 2,
    "Q3": 1,
    "Q4": 1,
    "Q5": 1,
    "Q6": 1,
    "Q7": 3,
    "Q8": 2,
    "Q9": 2,
    "Q10": 1,
    "Q11": 2,
    "Q12": 2,
    "Q13": 1,
    "Q14": 1,
    "Q15": 1
  },
  "answers": {
    "Q1": {"snippet": "识别歌词点划序列为摩斯电码。"},
    "Q2": {"snippet": "逐组解码为 I LOVE YOU。"},
    "Q3": {"snippet": "识别 ずっと 双关。"},
    "Q4": {"snippet": "示例：必须覆盖到 Q15，每题一个非空 snippet。"},
    "Q5": {"snippet": "示例。"},
    "Q6": {"snippet": "示例。"},
    "Q7": {"snippet": "示例。"},
    "Q8": {"snippet": "示例。"},
    "Q9": {"snippet": "示例。"},
    "Q10": {"snippet": "示例。"},
    "Q11": {"snippet": "示例。"},
    "Q12": {"snippet": "示例。"},
    "Q13": {"snippet": "示例。"},
    "Q14": {"snippet": "示例。"},
    "Q15": {"snippet": "示例。"}
  },
  "full_answer": "模型原始完整回答文本。"
}
```

**字段说明**
- `id` — 唯一标识符，不能重复，并且必须与文件名一致
- `scores` — 各题得分，必须覆盖所有题目（Q1–Q15），允许小数（如 `1.5`、`0.5`、`0.75`）；0 分写 `0`，不可省略
- `answers` — 各题评分摘录，必须覆盖 Q1–Q15；每题至少包含非空 `snippet`
- `full_answer` — 模型原始完整回答，页面“完整答案”弹窗使用

更新后先校验，再生成页面读取的聚合文件：

```bash
python3 scripts/validate_results.py
python3 scripts/build_results.py
```

刷新页面即可看到新模型出现在排行榜和雷达图中。不要手动编辑 `data/results.json`；它是发布产物。

## 添加模型测评结果（v2.2）

新 Prompt 试验版使用独立目录和聚合文件，避免与 v2.1 混排。v2.2 榜单会把同一模型的多次尝试合并成一行，排行榜展示得分区间，得分详情、雷达图和完整答案仍使用该模型的最高分答案。

1. 在 `data/results-v2.2/` 下新增同样结构的模型 JSON。每次尝试都必须有唯一 `id` 和文件名；同一模型的多次尝试请保持 `model`、`model_version`、`provider`、`api_endpoint` 一致，页面会按这些字段聚合。
2. 使用 v2.2 的 benchmark 和输出路径构建：

```bash
python3 scripts/build_results.py \
  --check \
  --benchmark data/benchmark-v2.2.json \
  --source-dir data/results-v2.2 \
  --output data/results-v2.2.json

python3 scripts/build_results.py \
  --benchmark data/benchmark-v2.2.json \
  --source-dir data/results-v2.2 \
  --output data/results-v2.2.json
```

访问 `http://localhost:8080` 或页面顶部“榜单版本”切换入口查看新榜单。

重复测试的文件名示例：

```text
data/results-v2.2/glm-5.1__run-2026-05-04-a.json
data/results-v2.2/glm-5.1__run-2026-05-04-b.json
```

如果两份记录聚合后分数分别为 `15.5` 和 `15.75`，排行榜显示 `15.5–15.75`；点击详情时只展示 `15.75` 那份答案和各题摘录。

---

## 评分规则（questions）

每道题的评分定义在对应榜单的 benchmark 文件 → `questions` 数组中：

- v2.1：`data/benchmark.json`
- v2.2：`data/benchmark-v2.2.json`

```json
{
  "id": "Q1",
  "title": "摩斯识别",
  "max": 1,
  "dimension": "cipher",
  "description": "识别摩斯电码",
  "scoring": "识别歌词中嵌入的点划序列是摩斯电码，1分。"
}
```

**字段说明**
- `id` — 题号，与 `results[].scores` 中的键对应，不可更改（除非同步修改所有结果）
- `max` — 该题满分，修改后会影响维度满分和总分，需同步更新 `total_points`
- `dimension` — 所属维度的 `key`，需与 `dimensions` 中的 key 对应
- `scoring` — 评分标准描述，悬浮提示中显示

**当前题目一览**

| 题号 | 标题 | 满分 | 维度 | 评分标准要点 |
|------|------|------|------|------|
| Q1 | 摩斯识别 | 1 | cipher | 识别摩斯电码 |
| Q2 | I LOVE YOU 解码 | 2 | cipher | 解码得到 I LOVE YOU |
| Q3 | ずっと 元语言密钥 | 1 | meta | 发现 ずっと 双关 |
| Q4 | 表层语义与远离 | 1 | language | 明かりになったあなた、动作感知与远离/化光关系 |
| Q5 | 主歌情感递进 | 1 | language | 主歌三组变化与心理轨迹 |
| Q6 | 副歌空间与心脏递进 | 1 | language | 副歌两条递进轴与回环 |
| Q7 | 信号-心脏结构 | 3 | signal | 点滅、摩斯、星光、心跳构成信号收发 |
| Q8 | 媒介系统化解读 | 2 | signal | 把歌、闭眼、风、光、电码理解为通信系统 |
| Q9 | 信号延迟与存在不确定性 | 2 | signal | 旧光、延迟确认与回信不确定 |
| Q10 | 天狼星基础意象 | 1 | astronomy | 天狼星身份、距离、观测特征与歌词对应 |
| Q11 | 双星/白矮星事实 | 2 | astronomy | Sirius A/B 与白矮星核心 |
| Q12 | 双星引力与平等等待 | 2 | astronomy | 双星绕行、引力束缚与平等双向关系 |
| Q13 | 发布时间/时代语境 | 1 | temporal | 发布时间的季节、年末与时代语境 |
| Q14 | 精确观测/轨道推理 | 1 | temporal | Sirius AB 轨道或具体当夜观测推理 |
| Q15 | 额外自洽洞察 | 1 | bonus | 标准答案外的新颖、证据化、解释性洞察 |

总分：**22 分**

---

## 维度定义（dimensions）

维度在对应 benchmark 文件 → `dimensions` 数组中定义，用于雷达图和分类统计：

```json
{
  "key": "cipher",
  "label": "暗号识别",
  "questions": ["Q1", "Q2"],
  "max": 3
}
```

**字段说明**
- `key` — 唯一标识，题目的 `dimension` 字段引用此值
- `label` — 显示名称（雷达图轴标签）
- `questions` — 该维度包含的题号列表
- `max` — 该维度满分（= 所含题目 `max` 之和）

**当前七个维度**

| Key | 标签 | 题目 | 满分 |
|-----|------|------|------|
| cipher | 暗号识别 | Q1, Q2 | 3 |
| meta | 元语言密钥 | Q3 | 1 |
| language | 文本递进 | Q4, Q5, Q6 | 3 |
| signal | 信号结构 | Q7, Q8, Q9 | 7 |
| astronomy | 天文联结 | Q10, Q11, Q12 | 5 |
| temporal | 时间推理 | Q13, Q14 | 2 |
| bonus | Bonus | Q15 | 1 |

---

## 等级划分（tiers）

等级定义在对应 benchmark 文件 → `tiers` 数组中，按总分区间显示徽章：

```json
{ "min": 19, "max": 22, "label": "完整解读", "description": "..." }
```

修改 `min`/`max` 阈值或添加新等级均可，页面会自动应用。

---

## JSON 特殊字符转义规范

`data/benchmark*.json`、`data/results*/**.json` 和生成后的 `data/results*.json` 均为标准 JSON，**所有字符串值必须合法转义**，否则页面会静默白屏或数据丢失。

### 常见踩坑

| 场景 | 错误写法 | 正确写法 |
|------|----------|----------|
| 字符串内含双引号 | `"answer": "他说"好""` | `"answer": "他说\"好\""` |
| 字符串内含换行 | `"prompt": "第一行\n第二行"` （实际裸换行） | `"prompt": "第一行\\n第二行"` |
| 反斜杠本身 | `"path": "C:\users"` | `"path": "C:\\users"` |

> **注意**：`prompt` 字段的摩斯电码片段（`·`、`-`）本身无需转义；但如果字段内含有实际的回车符（ASCII 0x0A），JSON 解析会直接报错，必须替换为 `\n`。

### 验证方法

```bash
# 验证 JSON 合法性（python3 内置，无需安装）
python3 -m json.tool data/benchmark.json > /dev/null && echo "OK"
python3 -m json.tool data/results.json  > /dev/null && echo "OK"
python3 scripts/validate_results.py

# v2.2
python3 -m json.tool data/benchmark-v2.2.json > /dev/null && echo "OK"
python3 -m json.tool data/results-v2.2.json  > /dev/null && echo "OK"
python3 scripts/build_results.py --check --benchmark data/benchmark-v2.2.json --source-dir data/results-v2.2 --output data/results-v2.2.json
```

如果前两条输出 `OK`、校验脚本输出 `validated ... result files`，说明文件合法；否则会打印出错位置，定位修复后再刷新页面。

---

## 图表操作说明

页面右侧图表会随榜单版本切换：

- v2.1：雷达图展示所有模型在全部维度上的得分。
- v2.2：纵向 Box Plot / 分布图展示同一模型多次测试的总分稳定性，纵轴越高代表分数越高。

v2.2 分布图规则：

- `1` 条记录：显示一条横线和单次分数。
- `2–4` 条记录：显示最低分、最高分连线和中位数点。
- `≥5` 条记录：显示正式 Box Plot（min、Q1、median、Q3、max）。

因此 `5` 条记录是进入 Box Plot 的最低样本数；少于 `5` 条仍可展示波动，但页面会用更轻量的摘要形态。

**默认状态**：全量显示当前筛选范围内的已选模型，各自使用独立颜色。

**交互**：
- 点击排行榜中的某模型 → 该模型高亮，其余模型弱化显示
- 再次点击同一模型（或点击空白处）→ 恢复全量显示

**更新 v2.1 雷达图轴（维度变更）**：
1. 修改对应 benchmark 文件 → `dimensions` 数组（增删维度或改 `label`）
2. 同步修改 `questions[].dimension` 字段，确保每道题映射到存在的维度 key
3. 同步更新每个维度的 `max`（= 所含题目 max 之和）和顶层 `total_points`
4. 运行 JSON 合法性验证，刷新页面即生效

**注意**：雷达图轴数量由 `dimensions` 数组长度自动决定，增减维度后坐标系会自动重算，无需修改 `index.html`。

---

## B 站 MV 嵌入

Hero 区右侧通过 `<iframe>` 内嵌 B 站播放器，相关参数说明：

```html
<iframe src="//player.bilibili.com/player.html
  ?bvid=BV15v411t79V   <!-- 视频 BV 号 -->
  &danmaku=0           <!-- 关闭弹幕 -->
  &autoplay=0          <!-- 禁止自动播放 -->
  &high_quality=1"     <!-- 默认高清 -->
```

**替换视频**：将 `bvid=` 后的值改为目标 BV 号即可，其余参数保持不变。

**样式注意事项**：
- `.hero-video-wrap` 固定宽度 `280px`，窄屏（< 900px）自动变 `width: 100%; max-width: 400px`
- `aspect-ratio: 16/9` 维持比例，无需手动设置高度
- 若 B 站因跨域限制导致播放器加载失败，在本地 `http.server` 模式下属正常现象，部署到 HTTPS 域名后即可正常播放
