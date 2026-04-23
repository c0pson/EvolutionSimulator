### Evolution Simulator

Wild Life Simulator where two species compete for survival through natural selection. The least adapted individuals are killed off, and new ones are created with mixed genes of the strongest.

#### Project structure

```
src/
├── main.py
├── consts.py
├── specie.py
├── stats.py
├── ...
└── history.py
docs/
└── report.md
saves/
├── 24042026-214421.json
├── ...
└── 24042026-214734.json
out/
├── histogram-24042026-214421.png
└── histogram-24042026-214734.png
```

#### Tech stack

 - Python
 - Pygame

#### Architecture

 - **OOP** - Blueprints for `prey` and `hunter` implementation. Each object (individual) will be trying to survive as long as possible. After killing the least adapted individuals, we will be creating new ones with mixed genes of the strongest ones.
 - **Data classes** - `Stats` and `PopulationSegment` as lightweight data containers.

#### References

 - [Game of Life Wikipedia page](https://en.wikipedia.org/wiki/Conway's_Game_of_Life)
