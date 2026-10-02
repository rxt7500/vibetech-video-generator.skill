# 定制

- 改默认风格：先改 knowledge/visual_style.md，再同步 SKILL.md、workflow defaults 和 master prompt 中的相关规则；不要仅改一句风格名称。
- 改默认画幅／fps：同步 scripts/video_job.py 的 make_brief 默认值、SKILL.md 与 workflow。每个任务也可用 init 的 --width / --height / --fps 覆盖。
- 增加新场景：扩展 assets/remotion-starter/src/Root.tsx 或新增 component，并同步 validate_board 支持的 kind；现有分镜字段保持兼容。
- 改音频：默认仍为 silent；使用时可覆盖。旁白功能必须调用实际支持中文的 TTS、加入真实 Audio component、测音频长度和同步字幕，详见 references/execution.md。
- 改模板后执行脚本测试、skill-creator quick_validate 与短片渲染。仅 YAML 合法或测试通过不能证明视觉接近参考，仍须看实际画面。

不要把真实供应商凭据、成片、node_modules、缓存或依赖浏览器打包到 skill 里。
