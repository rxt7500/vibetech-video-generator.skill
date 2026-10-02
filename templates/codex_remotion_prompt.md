# Remotion 实现工作单

先完成 [master_video_prompt.md](master_video_prompt.md) 的脚本、来源和分镜，再执行本工作单。

- 使用任务 package.json 中的真实版本。新任务由 assets/remotion-starter 初始化，不强制添加 GSAP。
- 扩展 src/Root.tsx 或添加 src/scenes/ 中的专属场景，以分镜 visual／animation 制作真正的插画、物件与机制，不只换 title。
- 所有动效依赖 useCurrentFrame / fps，字幕读取 storyboard captions。total_frames 决定 Composition 时长。
- 验证 storyboard → typecheck → compositions → 各场关键帧 → 全片 render → ffprobe / ffmpeg / 抽帧。实际命令和交付规则见 [execution.md](../references/execution.md)。
- 完成后交付已存在 MP4、字幕与源码；渲染失败时明确完成到哪一步。
