# 工具执行与产物契约

## 环境检查

先确定 skill 的真实目录、当前 cwd、用户指定输出目录及现有工程。后续 `<SKILL>`／`<JOB>` 是需替换的绝对路径，不是可原样执行的变量。

通过 shell/exec 检查 `node --version`、`npm --version`、`ffmpeg -version`、`ffprobe -version`、可运行 Python。Windows 的 `WindowsApps/python.exe` 可能只是占位器，必须实际运行确认；Codex desktop 可用 `load_workspace_dependencies` 找到 runtime。以真实 `package.json`／lockfile 判断现有版本，不覆盖已有工程依赖。

选择依据：有现成 Remotion 工程则复用；全新任务默认本 skill 的 Remotion 4.0.530 起步模板。只有用户指定 HyperFrames 或可用 HTML 动画工程更适合时才切换。HyperFrames skill 当前要求 Node >=22，检查本机实际 CLI 版本与 `--help`，不要用 Node 18 强行跑。没有专用视频生成 MCP 也可以由 shell 调用这些本地渲染器完成视频。

必要渲染依赖只能安装到独立视频任务目录；复用缓存与现有 Chrome 优先。若已有 Chrome，Remotion compositions / still / render 可传 `--browser-executable="实际 chrome.exe 绝对路径"`，必须以真实命令结果确认兼容；此参数见官方 CLI 文档。完成引擎环境检查后再开始 still/render，不并发重复下载浏览器。新建工程允许安装模板列出的最小依赖，不全局改 Node，不自动装两个引擎，不引入不必要的 UI／动画库。网络或包安装被拒绝时保留工程并报告，不宣称渲染成功。

## Remotion 主路线

在当前任务的 `work/` 下为源码与缓存选一个新目录，把最终 MP4／源码 ZIP／报告保存到该任务允许的 `outputs/`，或遵循用户指定路径。不往 skill 源目录写视频、node_modules 或临时文件。

```powershell
python "<SKILL>/scripts/video_job.py" init --topic "RAG 原理" --duration "60秒" --out "<JOB>"
```

如果 `python` 不可用，改用已验证的 Python executable 绝对路径。`init` 创建的 storyboard 是未完成草稿，须由 Codex 研究、填写和设计，不能立即 render。阅读 `production-prompt.md`，保存 `script.md`、`sources.md`，填完场景后运行：

```powershell
python "<SKILL>/scripts/video_job.py" validate "<JOB>/storyboard.json" --srt "<OUTPUT>/subtitles.srt"
```

切换 shell 工作目录为 `<JOB>` 后执行：

```powershell
npm install
npm run typecheck
npm run compositions
npx --no-install remotion still src/index.tsx VibeTech "<OUTPUT>/scene-01.png" --frame=75
npm run render -- "<OUTPUT>/video.mp4" --codec=h264 --pixel-format=yuv420p --color-space=bt709 --concurrency=2
```

still 的帧数按各场景“元素最完整的一帧”选择，示例 75 不适用于所有时长。至少查看每个场景一个关键帧，并检查开头／结尾和关键转场两侧。用 `view_image` 或实际可用的图像查看工具打开结果，而非仅检查文件存在。先中分辨率试渲染困难场景，确认后渲染用户指定的完整时长；不要只交付测试片段。Remotion 4.0.530 的默认 JPEG 帧与默认色彩空间可能输出 full-range `yuvj420p`，仅 `--pixel-format=yuv420p` 不足以保证媒体契约；显式使用 `--color-space=bt709`，已通过短片实测。精确色彩需求可加 `--image-format=png`；复用其他版本仍以其文档与实际 ffprobe 为准。

完整成片检查：

```powershell
python "<SKILL>/scripts/video_job.py" check-video "<OUTPUT>/video.mp4" --brief "<JOB>/brief.json" --report "<OUTPUT>/validation.json"
ffmpeg -v error -i "<OUTPUT>/video.mp4" -f null NUL
```

`NUL` 适用于 Windows，其他系统用本系统空设备。`check-video` 失败返回非零；字段 `passed` 只代表媒体参数检查。将抽帧结论、解码 exit code、采用引擎、版本与真实运行命令补入最终报告，不能把 `visual_review: pending` 当成视觉验收成功。

## 素材与工具路由

| 环节 | 调用方式 | 无对应能力时 |
| --- | --- | --- |
| 时效事实核实 | 可用 web/search 工具查官方源 | 缩减未核实论点，记录事实范围 |
| 纸质插画／拼贴底图 | 读 imagegen skill，调用可用 ImageGen 工具 | 精细 SVG 插画＋纸纹；记录替代 |
| 图形、文字、中文字幕 | 本地 SVG/React 或 HTML/GSAP | 保留可执行源码，不能拿 prompt 冒充视频 |
| 可选合成声音 | 可用 TTS 工具及对应 skill | 见音频分支 |
| 视频输出 | shell 执行 Remotion 或 HyperFrames CLI | 定位 Node/Chrome/FFmpeg 具体缺项 |
| 媒体验收 | ffprobe＋ffmpeg＋抽帧查看 | 报告未验证的检查项 |

ImageGen 只生成视觉资产，不将它描述成视频生成工具；任务可完全使用本地 SVG 生成视频。用户已排除 Runway，不调用其任何工具。其他外部服务以实际可用接口和用户指定为准，不从用户环境搜集密钥。用户明确要求真实摄影／人物连续镜头且本机工具不能满足时，报告实际能力边界，提供已完成的分镜与工程。

## 音频分支

默认 `audio: silent`，不探测或调用 TTS，不从参考复制音频。只有用户要求配音时才在 `brief.json` 和 `storyboard.json` 同步修改 audio，并选择实际可用且支持中文的 TTS。工具明确显示额外付费／缺凭证时，只询问该缺失条件，不重问主题、画幅或已授权的制作步骤。

先测合成音频时长，再调文案、语速、停顿和场景预算，字幕须与音频对齐；依请求保持总时长。不要默认把某个英文本地声音当作中文 TTS，不拉伸整段语音来硬凑时长。配乐只在用户要求且素材有使用权时加入。起步模板是静音 renderer，启用配音必须实现实际 Audio 组件并验证音轨；只改 JSON 不能产生声音。

## 打包与故障处理

保存制作 prompt、脚本、分镜、DESIGN、实际用到的素材、本地字体（可分发时）、源码、package.json 与生成的 lockfile。排除 node_modules、Chromium、临时帧、缓存、.env／密钥、原始参考视频。用标准 ZIP 工具打包即可。

报告包括：实际完成阶段、失败命令和简短错误、可复用的文件路径、修复方向。同一环节最多诊断重试两次；时长超限先缩减场景复杂度或分段渲染再拼接，保持同一 fps、尺寸、编码和精确总帧数。工具被系统拒绝时不能绕过；无法完成就明确“未完成渲染”。
