"""Local job preparation and media checks. Python standard library only."""
import argparse
import json
import math
import re
import shutil
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]


def parse_duration(raw):
    match = re.fullmatch(r'\s*(\d+(?:\.\d+)?)\s*(秒|秒钟|s|sec|seconds?|分钟|分|m|min|minutes?)?\s*', str(raw), re.I)
    if not match:
        raise ValueError('时长使用数字秒数，或 60秒 / 1.5分钟 / 2m 格式')
    seconds = float(match[1])
    if (match[2] or '').lower() in ('分钟', '分', 'm', 'min', 'minute', 'minutes'):
        seconds *= 60
    if not math.isfinite(seconds) or seconds <= 0:
        raise ValueError('时长必须是有限的正数')
    return seconds


def make_brief(topic, seconds, fps=30, width=1920, height=1080):
    if not str(topic).strip():
        raise ValueError('主题不能为空')
    seconds = parse_duration(seconds)
    if fps not in (24, 30, 60):
        raise ValueError('fps 使用 24、30 或 60')
    if any(type(v) is not int or v <= 0 or v % 2 for v in (width, height)):
        raise ValueError('width 和 height 必须是正偶数')
    frames = math.floor(seconds * fps + 0.5)
    if frames < 1:
        raise ValueError('时长小于一帧')
    return {'topic': str(topic).strip(), 'requested_seconds': seconds,
            'duration_seconds': frames / fps, 'total_frames': frames,
            'fps': fps, 'width': width, 'height': height, 'audio': 'silent',
            'style': 'warm-archive-documentary', 'engine': 'remotion'}


def make_draft(brief):
    # Slots are a timing aid; Codex rewrites them to suit the story before rendering.
    count = min(brief['total_frames'], max(1, math.ceil(brief['duration_seconds'] / 8)))
    base, remainder = divmod(brief['total_frames'], count)
    scenes, cursor = [], 0
    for i in range(count):
        length = base + (i < remainder)
        scenes.append({'id': f's{i + 1:02d}', 'start_frame': cursor,
                       'duration_frames': length, 'kind': 'archive',
                       'chapter': f'{i + 1:02d}', 'title': '', 'visual': '',
                       'animation': '', 'labels': [], 'captions': []})
        cursor += length
    return {**brief, 'status': 'draft', 'scenes': scenes}


def init_job(topic, seconds, out, fps=30, width=1920, height=1080):
    out = Path(out).resolve()
    brief = make_brief(topic, seconds, fps, width, height)
    if out.exists():
        raise FileExistsError(f'拒绝覆盖现有目录：{out}')
    shutil.copytree(SKILL / 'assets' / 'remotion-starter', out)
    for name, value in [('brief.json', brief), ('storyboard.json', make_draft(brief))]:
        (out / name).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
    prompt = (SKILL / 'templates' / 'master_video_prompt.md').read_text(encoding='utf-8')
    values = {**brief, 'project_dir': str(out), 'skill_dir': str(SKILL)}
    for key, value in values.items():
        prompt = prompt.replace('{{' + key + '}}', str(value))
    (out / 'production-prompt.md').write_text(prompt, encoding='utf-8')
    (out / 'DESIGN.md').write_text((SKILL / 'knowledge' / 'visual_style.md').read_text(encoding='utf-8'), encoding='utf-8')
    return brief


def validate_board(board):
    errors = []
    integer = lambda v: type(v) is int
    total, fps = board.get('total_frames'), board.get('fps')
    if not integer(total) or total <= 0 or fps not in (24, 30, 60):
        return ['total_frames 必须是正整数，fps 必须是 24、30 或 60']
    if board.get('status') != 'ready':
        errors.append('storyboard.status 仍是 draft；完成内容后才可标为 ready')
    for key in ('width', 'height'):
        if not integer(board.get(key)) or board[key] <= 0 or board[key] % 2:
            errors.append(f'{key} 必须是正偶数')
    if board.get('audio') not in ('silent', 'narration', 'narration-music'):
        errors.append('audio 使用 silent / narration / narration-music')
    seconds = board.get('duration_seconds')
    if not isinstance(seconds, (int, float)) or not math.isfinite(seconds) or abs(seconds - total / fps) > 1e-6:
        errors.append('duration_seconds 与 total_frames / fps 不一致')
    scenes = board.get('scenes')
    if not isinstance(scenes, list) or not scenes:
        return errors + ['scenes 不能为空']
    cursor, ids = 0, set()
    for i, s in enumerate(scenes):
        prefix = f'scene[{i}]'
        if not isinstance(s, dict):
            errors.append(f'{prefix} 必须是 object')
            continue
        identity = s.get('id')
        if not isinstance(identity, str) or not identity or identity in ids:
            errors.append(f'{prefix} id 为空或重复')
        else:
            ids.add(identity)
        start, length = s.get('start_frame'), s.get('duration_frames')
        if not integer(start) or not integer(length) or length < 1:
            errors.append(f'{prefix} 帧数必须是整数，duration_frames > 0')
            continue
        if start != cursor:
            errors.append(f'{prefix} 时间线有空隙或重叠：应从 {cursor} 开始')
        cursor = start + length
        if s.get('kind') not in ('archive', 'diagram', 'timeline', 'tree', 'title'):
            errors.append(f'{prefix} 未支持的 kind；新 kind 要同时扩展 renderer 与 validator')
        for field in ('title', 'visual', 'animation'):
            if not isinstance(s.get(field), str) or not s[field].strip():
                errors.append(f'{prefix}.{field} 不能为空')
        if s.get('image') and (not isinstance(s['image'], str) or s['image'].startswith(('http:', 'https:', '/', '\\')) or '..' in Path(s['image']).parts):
            errors.append(f'{prefix}.image 必须是 public 下的相对路径')
        labels = s.get('labels', [])
        if not isinstance(labels, list) or len(labels) > 6 or any(not isinstance(label, str) or not label.strip() for label in labels):
            errors.append(f'{prefix}.labels 必须是最多 6 个非空字符串；复杂图另写 component')
        if s.get('kind') in ('diagram', 'timeline', 'tree') and len(labels) < 2:
            errors.append(f'{prefix} 图解至少要有两个 label')
        captions = s.get('captions')
        if not isinstance(captions, list) or not captions:
            errors.append(f'{prefix} 至少需要一条字幕')
            continue
        previous = 0
        for j, caption in enumerate(captions):
            if not isinstance(caption, dict):
                errors.append(f'{prefix}.caption[{j}] 必须是 object')
                continue
            a, b, text = (caption.get(k) for k in ('start_frame', 'end_frame', 'text'))
            if not integer(a) or not integer(b) or not 0 <= a < b <= length or a < previous:
                errors.append(f'{prefix}.caption[{j}] 越界或重叠；字幕帧数是场景内相对帧')
            else:
                previous = b
            if not isinstance(text, str) or not text.strip():
                errors.append(f'{prefix}.caption[{j}] 文字不能为空')
    if cursor != total:
        errors.append(f'总帧数不匹配：时间线 {cursor}，目标 {total}')
    return errors


def validate_probe(probe, brief):
    errors = []
    streams = probe.get('streams', [])
    videos = [s for s in streams if s.get('codec_type') == 'video']
    if len(videos) != 1:
        return ['媒体必须含一个视频流']
    v = videos[0]
    for field, expected in [('width', brief['width']), ('height', brief['height']), ('codec_name', 'h264'), ('pix_fmt', 'yuv420p')]:
        if v.get(field) != expected:
            errors.append(f'{field}: 实际 {v.get(field)}，预期 {expected}')
    try:
        rate = float(Fraction(v['avg_frame_rate']))
        if abs(rate - brief['fps']) > 0.01:
            errors.append(f'fps: 实际 {rate}，预期 {brief["fps"]}')
        duration = float(v.get('duration', probe['format']['duration']))
        if not math.isfinite(duration) or abs(duration - brief['total_frames'] / brief['fps']) > 1 / brief['fps'] + 0.001:
            errors.append(f'时长不匹配：实际 {duration} 秒')
        if 'nb_frames' in v and v['nb_frames'] != 'N/A' and int(v['nb_frames']) != brief['total_frames']:
            errors.append(f'帧数不匹配：实际 {v["nb_frames"]}')
    except (KeyError, ValueError, ZeroDivisionError):
        errors.append('无法读取媒体时长、帧率或帧数')
    audio = any(s.get('codec_type') == 'audio' for s in streams)
    if brief.get('audio') == 'silent' and audio:
        errors.append('silent 模式应不含音轨')
    if brief.get('audio') != 'silent' and not audio:
        errors.append('已选择配音模式，但媒体没有音轨')
    return errors


def srt_stamp(frame, fps):
    ms = round(frame * 1000 / fps)
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f'{h:02}:{m:02}:{s:02},{ms:03}'


def export_srt(board, target):
    blocks = []
    for scene in board['scenes']:
        for caption in scene['captions']:
            start = scene['start_frame'] + caption['start_frame']
            end = scene['start_frame'] + caption['end_frame']
            blocks.append(f'{len(blocks) + 1}\n{srt_stamp(start, board["fps"])} --> {srt_stamp(end, board["fps"])}\n{caption["text"]}\n')
    Path(target).write_text('\n'.join(blocks), encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    init = sub.add_parser('init')
    init.add_argument('--topic', required=True)
    init.add_argument('--duration', required=True)
    init.add_argument('--out', type=Path, required=True)
    init.add_argument('--fps', type=int, default=30)
    init.add_argument('--width', type=int, default=1920)
    init.add_argument('--height', type=int, default=1080)
    val = sub.add_parser('validate')
    val.add_argument('storyboard', type=Path)
    val.add_argument('--srt', type=Path)
    check = sub.add_parser('check-video')
    check.add_argument('video', type=Path)
    check.add_argument('--brief', type=Path, required=True)
    check.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == 'init':
            print(json.dumps(init_job(args.topic, parse_duration(args.duration), args.out, args.fps, args.width, args.height), ensure_ascii=False, indent=2))
            return 0
        if args.command == 'validate':
            board = json.loads(args.storyboard.read_text(encoding='utf-8-sig'))
            errors = validate_board(board)
            if not errors and args.srt:
                export_srt(board, args.srt)
            print(json.dumps({'passed': not errors, 'errors': errors}, ensure_ascii=False, indent=2))
            return int(bool(errors))
        brief = json.loads(args.brief.read_text(encoding='utf-8-sig'))
        result = subprocess.run(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(args.video)], capture_output=True, text=True, encoding='utf-8', check=True)
        probe = json.loads(result.stdout)
        errors = validate_probe(probe, brief)
        report = {'passed': not errors, 'video': str(args.video.resolve()), 'errors': errors, 'probe': probe,
                  'visual_review': 'pending: inspect sampled frames separately; metadata does not prove visual quality'}
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
        print(json.dumps({'passed': not errors, 'errors': errors, 'report': str(args.report.resolve())}, ensure_ascii=False))
        return int(bool(errors))
    except (ValueError, KeyError, TypeError, OSError, subprocess.CalledProcessError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
