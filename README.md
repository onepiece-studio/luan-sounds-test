# Luan Test Sounds

A **test-only** sound source for [Luan](https://luan.fuyo.app). The Luan team pushes changes here (new pack versions, removed packs, re-added packs) to test sound source updates and version rollback in the app.

**Do not use it day to day.** Packs, versions and files change or disappear at any time without notice. For real sounds, add the official source: <https://github.com/onepiece-studio/luan-sounds>.

## Add it in Luan (testers)

Paste this address in Luan Settings → Sounds:

```
https://github.com/onepiece-studio/luan-sounds-test
```

Luan reads `https://raw.githubusercontent.com/onepiece-studio/luan-sounds-test/HEAD/luan.json`. GitHub caches it for up to 5 minutes, so a push can take that long to show up.

## What is inside

| Pack | Timbre | How versions sound |
|---|---|---|
| Test Alpha (`test-alpha`) | Soft sine tones | v1 is low; every later version is a perfect fifth higher |
| Test Beta (`test-beta`) | Buzzy square tones | Same rule |

Each pack has all nine events, and every event has its own rhythm (for example `task-complete` rises over three notes, `task-error` falls over two). All sounds are synthesized by `tools/generate_test_sounds.py` with the Python standard library.

```sh
python3 tools/generate_test_sounds.py test-alpha 2   # write packs/test-alpha as v2
python3 tools/luan_repo.py build .                   # regenerate luan.json, then check
```

The format is the [Luan Sound Repository Standard v1](https://github.com/onepiece-studio/luan-sounds/blob/main/STANDARD.md). The repository may also hold other test material.

## License

The synthesized sounds are dedicated to the public domain (CC0-1.0). The tools are MIT licensed. See [LICENSE](LICENSE).
