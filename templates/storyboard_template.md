# 分镜契约

`video_job.py init` 创建 storyboard.json；Codex 填写后由 `validate` 验证。所有时间是 **整数帧**，字幕时间是**场景内相对帧**，end_frame 不包含自身。顶层与 brief 保持同一 topic、width、height、fps、audio、total_frames、duration_seconds。场景按顺序从 0 连续覆盖全片。

场景示例（30 fps / 6 秒，不代表所有场景都固定六秒）：

```json
{
  "id": "s03",
  "start_frame": 360,
  "duration_frames": 180,
  "kind": "diagram",
  "chapter": "03 · 检索",
  "title": "让问题找到知识",
  "visual": "纸面上左侧问题变成检索向量，右侧档案索引显现，三条相关摘录汇聚成上下文",
  "animation": "0–30f 问题显现；30–110f 路径生长与检索命中；110–180f 摘录汇聚并停留阅读",
  "labels": ["问题", "检索", "相关摘录"],
  "captions": [
    {"start_frame": 10, "end_frame": 85, "text": "先用问题找到相关资料。"},
    {"start_frame": 85, "end_frame": 175, "text": "再把摘录交给模型生成回答。"}
  ]
}
```

支持 kind：archive（物件／拼贴）、title（开场／收尾）、diagram（机制路径）、timeline（演进）、tree（关系树）。骨架图解最多 6 个 labels；更复杂场景应写独立 component 并同步扩展 validator。可选 `image` 是工程 public/ 下的相对路径，例如 `images/library.png`；可选 `dark: true` 用于少量暗场。

`visual` 和 `animation` 是导演说明，不会由起步 renderer 自动变成复杂画面，Codex 必须按说明制作 JSX/SVG/素材。图解起步组件用于承载准确 labels，不能替代主题设计。转场在场景预算内实现，若需要跨场景叠化，保留逻辑时间线不重叠并在 renderer 内建立单独过渡层。

每场至少一条短字幕。将脚本来源与不确定项写入 sources.md，画面不得宣称超出证据范围的具体成果。
