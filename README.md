# world-news-2026-11-24

One 1024x1024 PNG that sums up the world's news of Tuesday 24 November 2026, written to `/output/entry.png`. Built for the make.fun bounty "Sum up 24 November's world news in one image".

## How it works

`main.py` draws the image deterministically at runtime with Pillow — a newspaper-front-page collage with a masthead, a top story banner, a 2×2 story grid, a news ticker band, a short-news column and a footer. No network access, no randomness, no user input. Same bytes every run.

## Requirements

- Python 3.13
- Pillow (`pip install pillow`)

## Run

```bash
python main.py
```

Creates `/output/entry.png` (creates the directory if missing). The script self-checks: PNG format, exact 1024×1024, at most 1 MiB; exits non-zero on violation.

## Edge cases handled

- Missing `/output` directory: created automatically.
- Font availability: falls back through common system font paths, then Pillow's default bitmap font.
- Oversized text: auto-shrinks and wraps to stay inside its box.
- Size cap: fails loudly rather than emitting an invalid entry.

## License

MIT — see [LICENSE](LICENSE).