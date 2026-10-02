# HyperFrames 替代路线

只有实际可用或用户明确要求时使用。先读环境中的 hyperframes 和 hyperframes-cli skills；本机检查 Node、FFmpeg、Chrome 和 CLI help/version。当前技能文档要求 Node >=22。不要在 Remotion 工程中混入 HyperFrames runtime。

将本 skill 的视觉规则写入任务 DESIGN.md，复用 brief / storyboard 的内容与帧预算。根 HTML composition 明确 data-composition-id、data-width、data-height、data-start=0、data-duration=total_frames/fps。clip timing 换算为帧数/fps，避免累计浮点误差。

GSAP timeline 要 paused，注册给 HyperFrames 渲染器，按当前版本文档处理 seek；不能让 CSS/GSAP 自己按墙钟运行。准确字幕与文字用 HTML/SVG，主体与字幕保持安全区。

依次执行真实 CLI：`init --non-interactive` → lint → inspect → render；命令 flags 先核对本机 `--help`。当前已安装技能文档给出的示例：

```powershell
npx hyperframes init archive-film --non-interactive
npx hyperframes lint
npx hyperframes inspect --samples 15
npx hyperframes render --output "<OUTPUT>/video.mp4" --fps 30 --quality high
```

即使选此路线也要使用 `video_job.py validate` 检查分镜，`check-video` 验证 MP4。依用户任务更新 brief.engine，实际 renderer 参数必须与 brief 一致。本次完善的成片实测只覆盖 Remotion 路线，不能说 HyperFrames 也已实测通过。
