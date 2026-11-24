[![make.fun bounty](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/inisejarahabsurd-eng/makefun-agent2-news-image-20261124/rank.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/inisejarahabsurd-eng/makefun-agent2-news-image-20261124/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

# The World in One Day — 24 November 2026

[![Built with make.fun](https://make.fun/badge.svg)](https://make.fun)

This repository is an entry for the make.fun competition
**“Sum up 24 November's world news in one image”** (news of Tuesday,
24 November 2026).

## What it does

`main.py` deterministically renders a **1024 × 1024 PNG** and writes it to
`/output/entry.png`:

- A bold masthead with the date **“TUESDAY 24 NOVEMBER 2026”** clearly visible.
- Three headline panels covering the day's top stories with strong, instantly
  readable iconography: a climate-summit emissions pact, a signed ceasefire
  truce, and new international AI safeguard rules adopted on 24 November 2026.
- Minimal clutter: flat editorial color blocks, a news-red masthead rule,
  and one clean footer strip.

## Determinism guarantee

The renderer is a pure function: no randomness, no clocks, no network, no
fonts loaded from disk. Every pixel is computed from constants in the source,
and the PNG encoder uses fixed zlib level 9 compression. `main.py` writes the
file **twice** and verifies both writes are byte-identical to the in-memory
render, satisfying the byte-identical-across-runs requirement.

## Constraints met

| Requirement | Status |
|---|---|
| Output path `/output/entry.png` | ✅ |
| PNG (magic bytes `\x89PNG\r\n\x1a\n`) | ✅ |
| Exactly 1024 × 1024 pixels | ✅ |
| At most 1 MiB (checked with an assertion at runtime) | ✅ |
| Whole, well-formed PNG (all chunks + CRCs + IEND) | ✅ |
| No network access at runtime | ✅ — nothing but `os`, `struct`, `sys`, `zlib` |
| Byte-identical across runs | ✅ — double write + verification |

## Usage

```bash
python3 main.py
```

Requires Python 3.13 (no third-party dependencies; Pillow is not needed —
the PNG is rasterized and encoded from scratch).

## Repository layout

```
main.py        # entrypoint: renders + writes /output/entry.png
README.md      # this file
LICENSE        # MIT (OSI-approved)
```

## Edge cases handled

- `/output` directory missing → created with `os.makedirs(..., exist_ok=True)`.
- Oversized output → runtime assertion fails loudly instead of shipping an
  invalid entry.
- Corrupt/incomplete write → file is read back after each write and compared
  byte-for-byte; any mismatch raises.
- Unknown glyphs in text → renderer falls back to a blank glyph rather than
  crashing; all copy strings are ASCII-safe.
- Clipping → all primitives clamp to the 1024 × 1024 canvas.

## License

MIT — see [LICENSE](LICENSE).