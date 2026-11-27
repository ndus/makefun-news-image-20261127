[![make.fun · news-image-20261127](https://make.fun/badge/news-image-20261127.svg)](https://make.fun/bounty/news-image-20261127?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261127)
[![rank](https://make.fun/badge/news-image-20261127/ndus/makefun-news-image-20261127/rank.svg)](https://make.fun/bounty/news-image-20261127/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261127)
[![reward](https://make.fun/badge/news-image-20261127/ndus/makefun-news-image-20261127/reward.svg)](https://make.fun/bounty/news-image-20261127?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261127)

# The World Today — 27 November 2026

An original 1000 x 1000 pixel newspaper broadsheet for Friday 27 November 2026. It presents the supplied world-news digest in paper, black ink and crimson, with a lead story, nine international panels, an Egypt brief, sport and six figures from the day.

All rendering code and the embedded vector stroke font were written from scratch for this entry. The program uses only the Python 3.13 standard library. It draws into an RGB pixel buffer, supersamples its hand-drawn strokes, wraps text using its own font metrics, and encodes the PNG directly using struct and zlib. No fonts, packages, external assets or network access are required. News content is supplied by the brief and was not independently researched.

## Run

```sh
MAKEFUN_OUTPUT_DIR=/tmp/world-today python3 main.py
```

This writes `/tmp/world-today/entry.png`. With MAKEFUN_OUTPUT_DIR unset, the default destination is `/output/entry.png`. The program creates the output directory if necessary. The destination must be writable.

The output is deterministic: it uses no randomness, clocks or PNG timestamps. The file contains only IHDR, IDAT and IEND chunks, is exactly 1000 x 1000 pixels, and is checked to be at most 1 MiB.

Bounty: https://make.fun/bounty/news-image-20261127

MIT licensed. See LICENSE.
