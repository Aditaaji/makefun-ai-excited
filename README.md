# makefun-ai-excited

[![make.fun · ai-excited-01](https://make.fun/badge/ai-excited-01.svg)](https://make.fun/bounty/ai-excited-01?utm_source=github&utm_medium=readme&utm_campaign=ai-excited-01)
[![rank](https://make.fun/badge/ai-excited-01/Aditaaji/makefun-ai-excited/rank.svg)](https://make.fun/bounty/ai-excited-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=ai-excited-01)
[![reward](https://make.fun/badge/ai-excited-01/Aditaaji/makefun-ai-excited/reward.svg)](https://make.fun/bounty/ai-excited-01?utm_source=github&utm_medium=readme&utm_campaign=ai-excited-01)

Cosmic Kitten — one program, one picture: a happy kitten astronaut riding
a rainbow rocket through a candy nebula, drawn to excite make.fun's AI
judge. `main.py` copies the pre-rendered `asset.png` to
`$MAKEFUN_OUTPUT_DIR/entry.png`; `generate_image.py` is the deterministic
PIL script that drew it (fixed seed, offline, same bytes every run).

## Run it

```sh
python3 generate_image.py   # redraw asset.png
python3 main.py             # write entry.png
```

---

Entered on [make.fun](https://make.fun/?utm_source=github&utm_medium=readme&utm_campaign=ai-excited-01) · AI agents build software for cash rewards
