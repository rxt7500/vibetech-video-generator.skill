# 使用

```text
用 $vibetech-video-generator 做一个 RAG 原理视频，60 秒。
用 $vibetech-video-generator 做一个人工智能发展史视频，3 分钟。
用 $vibetech-video-generator 做一个 MCP 和 Function Calling 区别视频，90 秒。
```

只需主题与时长。Codex 自动生成 production-prompt.md 并在当前任务继续执行，最终返回成片，而不是要求你把提示词再复制到另一个任务。

默认横屏 1080p、30 fps、中文字幕、静音、暖色纸质档案与插画风格。`竖屏`／`2K`／`英文字幕`／`带中文旁白` 等在调用时说明即可；只要提示词时明确写“只生成 prompt，暂不渲染”。缺少主题或时长时 Codex 会询问缺项。

默认使用内置 ImageGen＋Remotion，HyperFrames 可作为适用时的替代路线。按用户最新选择，不使用 Runway，后续调用也不会自动启用该插件。

源 skill 可保存在任意目录，但要让 `$vibetech-video-generator` 自动发现，需在 Codex 的个人 skills 目录中存在 `vibetech-video-generator/SKILL.md`。本次已创建的安装副本与源目录内容保持一致；以后手工修改源目录，需要同步安装副本。新开聊天检查可用技能列表；不要把“文件已复制”当作当前聊天已热加载技能。

视频任务生成在该任务允许的输出位置，工程与临时文件在独立 work 目录。第一次渲染可能需安装模板的 Node 包和下载 renderer 使用的 Chrome，后续可复用缓存。无法联网或缺依赖时会保存制作工作单和工程，明确报告未完成渲染。

示例只示范叙事与调用，涉及当前产品版本、年份、性能的数据必须在生成时重新核实。
