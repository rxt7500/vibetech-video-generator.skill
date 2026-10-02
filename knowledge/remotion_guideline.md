# Remotion 实现

新任务起步模板使用 Remotion / @remotion/cli **4.0.530**、React 19、TypeScript 5.7.3；npm registry 已核实版本存在。复用工程时保留其已安装版本，以工程 lockfile 和该版本官方文档为准，不盲升。所有 @remotion/* 保持同版本。

根 Composition 设置真实 width / height / fps / durationInFrames。Sequence 的 `from` 与 `durationInFrames` 由 storyboard 整数帧决定；Sequence 内 `useCurrentFrame()` 是相对帧。用 interpolate／spring 与 SVG 路径构成可寻址动画。SVG、React 已能完成默认效果，无需强制安装 GSAP；若确实需要 GSAP，必须让 timeline 随当前 frame seek 并清理实例。

starter 包含纸纹、暖色画面、字幕、图解、年表、关系树和本地图片背景等基础组件。它并不是完整导演系统，`visual`／`animation` 描述不会自动执行；Codex 仍须写主题专属组件。`status != ready` 会拒绝 render。对标题、长 label 和字幕用真实帧图查看布局。

命令见 [execution.md](../references/execution.md)。CLI 必须明确 entry-point、composition id、输出路径。默认 render script 显式设置 H.264、yuv420p、BT.709，避免该版本默认 JPEG/full-range 路径产生 yuvj420p；这一差异已通过六帧复现片验证。Windows 的 props 用 JSON 文件传入，不在 shell 中拼接 inline JSON。render 之后验证 MP4 而非只看 CLI 成功。

官方依据（2026-10-02 核对）：

- [Composition](https://www.remotion.dev/docs/composition)
- [Sequence](https://www.remotion.dev/docs/sequence)
- [useCurrentFrame](https://www.remotion.dev/docs/use-current-frame)
- [interpolate](https://www.remotion.dev/docs/interpolate)
- [render CLI](https://www.remotion.dev/docs/cli/render)
- [still CLI](https://www.remotion.dev/docs/cli/still)
- [compositions CLI](https://www.remotion.dev/docs/cli/compositions)
