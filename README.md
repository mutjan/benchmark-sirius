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

---

## JSON 特殊字符转义规范

`data/benchmark.json` 和 `data/results.json` 均为标准 JSON，**所有字符串值必须合法转义**，否则页面会静默白屏或数据丢失。

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
```

如果输出 `OK` 说明文件合法；否则会打印出错行号，定位修复后再刷新页面。

---

## 雷达图（星图）操作说明

雷达图展示所有模型在五个维度上的得分。

**默认状态**：全量显示所有模型，各自用独立颜色实线绘制，顶点有发光圆点。

**交互**：
- 点击排行榜中的某模型 → 该模型高亮，其余模型降至 45% 透明度并改为虚线轮廓
- 再次点击同一模型（或点击空白处）→ 恢复全量显示

**更新雷达图轴（维度变更）**：
1. 修改 `data/benchmark.json` → `dimensions` 数组（增删维度或改 `label`）
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
