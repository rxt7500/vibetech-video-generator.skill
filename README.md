# VibeTech 视频生成 skill

调用示例：`用 $vibetech-video-generator 做一个 RAG 原理视频，60 秒。`

Codex 自动完成研究、制作 prompt、脚本、分镜、素材与动画、实际渲染、成片验收；交付 MP4、字幕、prompt 和可复现源码。默认暖纸色档案纪录片风格，1920×1080 / 30 fps，中文短字幕，无旁白、无配乐。用户可以覆盖这些默认值。

入口见 [SKILL.md](SKILL.md)，用法见 [docs/usage.md](docs/usage.md)。这是 Codex skill，不是独立运行的文本到视频模型；主题理解、脚本、素材选择和实现由 Codex 执行，脚本只负责可靠的任务初始化与验收。包含 Remotion 起步模板，HyperFrames 可作为环境具备时的替代路线。
