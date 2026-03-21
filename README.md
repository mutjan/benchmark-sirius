# シリウスの心臓 Benchmark 展示页

评测大模型对歌曲《シリウスの心臓》的理解深度，涵盖符号识别、元语言密钥、语言深度、天文知识、时间推理五个维度。

---

## 数据文件结构

```
data/
  benchmark.json   # Benchmark 定义：题目、维度、等级（稳定，少改动）
  results.json     # 模型测评结果数组（频繁追加）
```

---

## 快速启动

```bash
cd benchmark-sirius
python3 -m http.server 8080
# 访问 http://localhost:8080
```

---

## 添加模型测评结果

编辑 `data/results.json`，在数组末尾追加一条记录：

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
    "Q2": 1,
    "Q3": 2,
    "Q4": 1,
    "Q5": 2,
    "Q6": 2,
    "Q7": 2,
    "Q8": 3,
    "Q9": 1
  }
}
```

**字段说明**
- `id` — 唯一标识符，不能重复
- `scores` — 各题得分，必须覆盖所有题目（Q1–Q9），允许小数（如 `1.5`、`0.5`）；0 分写 `0`，不可省略

刷新页面即可看到新模型出现在排行榜和雷达图中。

---

## 评分规则（questions）

每道题的评分定义在 `data/benchmark.json` → `questions` 数组中：

```json
{
  "id": "Q1",
  "title": "符号识别",
  "max": 1,
  "dimension": "cipher",
  "description": "识别摩斯电码",
  "scoring": "识别出歌词中嵌入的符号序列是摩斯电码（Morse Code）"
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
| Q1 | 符号识别 | 1 | cipher | 识别出摩斯电码 |
| Q2 | 解码结果 | 1 | cipher | 正确解码得到 I LOVE YOU |
| Q3 | 元语言密钥 | 2 | meta | 发现 (・=ず；ー＝と) 注释揭示「ずっと」双重密钥 |
| Q4 | 词语递进 | 2 | language | 寂しい→哀しい 情感深化分析 |
| Q5 | 副歌演变 | 2 | language | 三段心臓状态对应白矮星演化阶段 |
| Q6 | 意象关联 | 3 | astronomy | 天狼星天文特性与歌词意象对应（至少两点） |
| Q7 | 引力词义 | 3 | astronomy | 双星引力结构对「宇宙で会えるまで」的天文学解读 |
| Q8 | 发布时间意义 | 5 | temporal | 计算2020年轨道阶段（52%），分析象征意义，预测2044近星点 |
| Q9 | 主角视角 | 1 | astronomy | 识别主角是双星系统两颗星而非人与星的单向关系 |

总分：**20 分**

---

## 维度定义（dimensions）

维度在 `data/benchmark.json` → `dimensions` 数组中定义，用于雷达图和分类统计：

```json
{
  "key": "cipher",
  "label": "符号识别",
  "questions": ["Q1", "Q2"],
  "max": 2
}
```

**字段说明**
- `key` — 唯一标识，题目的 `dimension` 字段引用此值
- `label` — 显示名称（雷达图轴标签）
- `questions` — 该维度包含的题号列表
- `max` — 该维度满分（= 所含题目 `max` 之和）

**当前五个维度**

| Key | 标签 | 题目 | 满分 |
|-----|------|------|------|
| cipher | 符号识别 | Q1, Q2 | 2 |
| meta | 元语言密钥 | Q3 | 2 |
| language | 语言深度 | Q4, Q5 | 4 |
| astronomy | 天文知识 | Q6, Q7, Q9 | 7 |
| temporal | 时间推理 | Q8 | 5 |

---

## 等级划分（tiers）

等级定义在 `data/benchmark.json` → `tiers` 数组中，按总分区间显示徽章：

```json
{ "min": 16, "max": 20, "label": "完全解读", "description": "..." }
```

修改 `min`/`max` 阈值或添加新等级均可，页面会自动应用。
