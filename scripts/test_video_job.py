import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name('video_job.py')


class VideoJobTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = None
        if SCRIPT.exists():
            spec = importlib.util.spec_from_file_location('video_job', SCRIPT)
            cls.module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(cls.module)

    def api(self):
        self.assertIsNotNone(self.module, '缺少可执行的任务初始化与时间线验收脚本')
        return self.module

    def test_duration_units_and_invalid_values(self):
        m = self.api()
        for raw, seconds in [('60', 60), ('60秒', 60), ('1.5分钟', 90), ('2m', 120), ('12.25s', 12.25)]:
            self.assertEqual(m.parse_duration(raw), seconds)
        for raw in ['0', '-1', 'nan', 'inf', '两分钟', '1分钟30秒']:
            with self.assertRaises(ValueError, msg=raw):
                m.parse_duration(raw)

    def test_frame_budget_has_no_rounding_gap(self):
        m = self.api()
        for seconds in [0.1, 7.13, 60, 180]:
            brief = m.make_brief('RAG', seconds)
            scenes = m.make_draft(brief)['scenes']
            self.assertEqual(sum(s['duration_frames'] for s in scenes), brief['total_frames'])
            self.assertEqual(scenes[-1]['start_frame'] + scenes[-1]['duration_frames'], brief['total_frames'])
            self.assertTrue(all(s['duration_frames'] > 0 for s in scenes))

    def valid_board(self):
        m = self.api()
        board = m.make_draft(m.make_brief('RAG', 12))
        board['status'] = 'ready'
        for s in board['scenes']:
            s.update(title='知识与回答', visual='文档化为检索路径', animation='路径沿箭头逐步显现', kind='diagram', labels=['文档', '检索', '回答'])
            s['captions'] = [{'start_frame': 0, 'end_frame': s['duration_frames'], 'text': '检索相关知识。'}]
        return board

    def test_draft_cannot_pass_as_final(self):
        m = self.api()
        self.assertTrue(m.validate_board(m.make_draft(m.make_brief('RAG', 12))))
        self.assertEqual(m.validate_board(self.valid_board()), [])

    def test_gap_and_caption_overrun_are_rejected(self):
        m = self.api()
        board = self.valid_board()
        board['scenes'][1]['start_frame'] += 1
        board['scenes'][0]['captions'][0]['end_frame'] += 1
        self.assertGreaterEqual(len(m.validate_board(board)), 2)

    def test_caption_overlap_is_rejected(self):
        m = self.api()
        board = self.valid_board()
        s = board['scenes'][0]
        s['captions'].append({'start_frame': 1, 'end_frame': 2, 'text': '重叠'})
        self.assertTrue(m.validate_board(board))

    def test_init_preserves_existing_folder_and_copies_template(self):
        m = self.api()
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'job'
            m.init_job('RAG', 12, out)
            self.assertTrue((out / 'src' / 'Root.tsx').exists())
            self.assertIn('RAG', (out / 'production-prompt.md').read_text(encoding='utf-8'))
            before = (out / 'brief.json').read_bytes()
            with self.assertRaises(FileExistsError):
                m.init_job('覆盖', 5, out)
            self.assertEqual(before, (out / 'brief.json').read_bytes())

    def test_media_contract_rejects_wrong_duration_and_audio(self):
        m = self.api()
        brief = m.make_brief('RAG', 12)
        probe = {'streams': [{'codec_type': 'video', 'codec_name': 'h264', 'width': 1920, 'height': 1080, 'avg_frame_rate': '30/1', 'pix_fmt': 'yuv420p', 'duration': '12.0', 'nb_frames': '360'}], 'format': {'duration': '12.0'}}
        self.assertEqual(m.validate_probe(probe, brief), [])
        probe['streams'][0]['duration'] = '11'
        probe['streams'].append({'codec_type': 'audio'})
        self.assertGreaterEqual(len(m.validate_probe(probe, brief)), 2)


if __name__ == '__main__':
    unittest.main()
