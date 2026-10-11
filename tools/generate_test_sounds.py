#!/usr/bin/env python3
"""Generate the synthesized test packs of this repository.

    python3 tools/generate_test_sounds.py <pack-id> <version>

Writes packs/<pack-id>/<event>.wav and packs/<pack-id>/pack.json, then run
`python3 tools/luan_repo.py build .` to refresh luan.json.

Every version is a fixed pitch step: v1 is low, each next version is a perfect
fifth higher, so a version change is obvious by ear. Each event has its own
rhythm; each pack has its own timbre. Python 3 standard library only.
"""
import json
import math
import struct
import sys
import wave
from pathlib import Path

RATE = 44100
AMPLITUDE = 0.45  # about -7 dBFS, under the -1 dBFS recommendation

PACKS = {
    'test-alpha': {
        'name': 'Test Alpha',
        'zh': '测试 Alpha',
        'timbre': 'Soft sine tones',
        'zh_timbre': '柔和的正弦音',
        'base': 220.0,
        'harmonics': [(1, 1.0), (2, 0.25)],
        'decay': 9.0,
    },
    'test-beta': {
        'name': 'Test Beta',
        'zh': '测试 Beta',
        'timbre': 'Buzzy square tones',
        'zh_timbre': '带嗡声的方波音',
        'base': 196.0,
        'harmonics': [(1, 1.0), (3, 0.33), (5, 0.2), (7, 0.14)],
        'decay': 3.0,
    },
}

# event -> notes as (pitch ratio, seconds, silence after)
EVENTS = {
    'session-start': [(1.0, 0.12, 0.03), (1.5, 0.2, 0)],
    'task-acknowledge': [(2.0, 0.08, 0)],
    'task-complete': [(1.0, 0.1, 0.02), (1.25, 0.1, 0.02), (1.5, 0.22, 0)],
    'task-error': [(1.2, 0.14, 0.03), (0.8, 0.26, 0)],
    'input-required': [(1.5, 0.1, 0.08), (1.5, 0.1, 0)],
    'input-required-question': [(1.25, 0.1, 0.03), (1.68, 0.18, 0)],
    'resource-limit': [(0.75, 0.45, 0)],
    'user-spam': [(2.0, 0.05, 0.04)] * 3 + [(2.0, 0.05, 0)],
    'idle-reminder': [(1.0, 0.12, 0.18)] * 2 + [(1.0, 0.12, 0)],
}

REGISTERS = {1: ('low pitch', '低音'), 2: ('higher pitch', '较高音'), 3: ('highest pitch', '高音')}


def note(pack, frequency, seconds):
    frames = int(RATE * seconds)
    attack = int(RATE * 0.005)
    total = sum(weight for _, weight in pack['harmonics'])
    samples = []
    for i in range(frames):
        t = i / RATE
        tone = sum(weight * math.sin(2 * math.pi * frequency * n * t) for n, weight in pack['harmonics']) / total
        envelope = min(1.0, i / attack) * math.exp(-pack['decay'] * t) * min(1.0, (frames - i) / attack)
        samples.append(tone * envelope)
    return samples


def render(pack, pattern, step):
    samples = []
    for ratio, seconds, silence in pattern:
        samples += note(pack, pack['base'] * ratio * step, seconds)
        samples += [0.0] * int(RATE * silence)
    return b''.join(struct.pack('<h', round(s * AMPLITUDE * 32767)) for s in samples)


def describe(pack, version):
    english, chinese = REGISTERS.get(version, (f'pitch step {version}', f'第 {version} 级音高'))
    return (f'{pack["timbre"]}, v{version}: {english}. For testing only.',
            f'{pack["zh_timbre"]}，v{version}：{chinese}。仅供测试。')


def main(pack_id, version):
    pack = PACKS[pack_id]
    step = 2 ** (7 * (version - 1) / 12)
    directory = Path(__file__).resolve().parent.parent / 'packs' / pack_id
    directory.mkdir(parents=True, exist_ok=True)
    for event, pattern in EVENTS.items():
        with wave.open(str(directory / f'{event}.wav'), 'wb') as out:
            out.setnchannels(1)
            out.setsampwidth(2)
            out.setframerate(RATE)
            out.writeframes(render(pack, pattern, step))
    description, zh_description = describe(pack, version)
    meta = {
        'name': pack['name'],
        'description': description,
        'localizations': {'zh-Hans': {'name': pack['zh'], 'description': zh_description}},
        'version': version,
        'license': 'CC0-1.0',
    }
    (directory / 'pack.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    if len(sys.argv) != 3 or sys.argv[1] not in PACKS or not sys.argv[2].isdigit() or int(sys.argv[2]) < 1:
        sys.exit(f'usage: {sys.argv[0]} <{"|".join(PACKS)}> <version>')
    main(sys.argv[1], int(sys.argv[2]))
