# DDIA Course Presentations

Animated manim-slides decks for *Designing Data-Intensive Applications* TA sessions — one section per chapter, sheets per topic.

## Repository Layout

```
ddia/
├── section_1/   # Foundations
│   ├── data_intensive_intro.py
│   ├── reliability.py
│   ├── scalability.py
│   ├── twitter_fanout.py
│   ├── olap_lab.py
│   └── sheet_1_hardware.py        ← Sheet 1: Hardware & System Sizing
├── section_2/   # Microservices
│   ├── microservice_lab.py
│   └── sheet_2_file_formats.py    ← Sheet 2: File Formats & Replicas
├── section_3/   # Consistency
│   ├── consistency_lab.py
│   ├── lab2_id_followup.py
│   └── sheet_3_partitioning.py    ← Sheet 3: Partitioning
├── section_4/
│   └── sheet_4_consistency.py
├── section_5/
│   └── sheet_5_streaming.py
├── section_6/
│   └── lab_4_jms_kafka.py
└── section_7/
    └── project_weather_stations.py
libs/
├── ddia_components.py   # primitives: make_label, make_icon, make_fit_box, create_rect_glow, ICON_* constants
├── slide_controls.py    # slide_checkpoint helper for manim-slides
└── slide_style.py       # SlideStyleMixin: _card, _icon_row_card, _play_glow_row, _flow_node, _flow_arrow, _section_header, _code_box, _next_slide
assets/icons/            # SVG icon library
```

## Mapping (sheet → section)

| Sheet | Topic | File |
|---|---|---|
| Sheet 1 | Hardware & System Sizing | `ddia/section_1/sheet_1_hardware.py` |
| Sheet 2 | File Formats & Replicas (Avro · Protobuf · MessagePack · Thrift · Parquet) | `ddia/section_2/sheet_2_file_formats.py` |
| Sheet 3 | Partitioning (hash mod N · consistent hashing) | `ddia/section_3/sheet_3_partitioning.py` |
| Sheet 4 | Consistency (isolation · linearizability · FIFO · CAP) | `ddia/section_4/sheet_4_consistency.py` |
| Sheet 5 | Streaming (backpressure · ordering · transmission models) | `ddia/section_5/sheet_5_streaming.py` |

## Architecture

Every scene class follows the same pattern:

```python
from libs.slide_style import SlideStyleMixin
try:
    from manim_slides import Slide as BaseSlide
except Exception:
    BaseSlide = Scene

class SheetXTopic(SlideStyleMixin, BaseSlide):
    def construct(self):
        self.scene_title()
        self.scene_q1_...()
        ...
```

`SlideStyleMixin` provides:
- `_section_header(text, color)` — top banner
- `_icon_row_card(icon, color, title, desc, glow=False)` — bullet row card; returns `(card, glow)` tuple when `glow=True`
- `_play_glow_row(row, glow, color)` — pulse + bloom
- `_card`, `_flow_node`, `_flow_arrow`, `_code_box` — layout primitives
- `_next_slide(phase=False)` — manim-slides checkpoint (between scenes and between bullet rows)
- Class attrs: `slide_stop_mode = "phase"`, `max_duration_before_split_reverse = 4.0`

## Rendering

Install:
```bash
pip install manim manim-slides autoflake
```

Render a single deck (preview quality):
```bash
manim -ql ddia/section_1/sheet_1_hardware.py Sheet1Hardware
```

Render + present as slides:
```bash
manim-slides render ddia/section_1/sheet_1_hardware.py Sheet1Hardware
manim-slides Sheet1Hardware
```

Stop modes (set via `slide_stop_mode` class attr):
- `"off"`: no pauses, plays straight through
- `"scene"`: pause at scene boundaries only
- `"phase"` (default): pause at scene boundaries AND mid-scene phases

## Authoring new sheets

1. Copy a section subdir and rename the file: `sheet_N_topic.py`.
2. Inherit `(SlideStyleMixin, BaseSlide)`.
3. One `scene_*` method per question; use the helpers — DO NOT redefine them.
4. Highlight the key takeaway per scene via `GLOW = {idx}` + `_play_glow_row`.
5. End each scene with `self._next_slide(); self.play(FadeOut(*self.mobjects))`.
6. Run `autoflake --remove-all-unused-imports --in-place <file>` before commit.

## Conventions

- Background: `config.background_color = "#0D1117"` (GitHub dark)
- Highlight color: GOLD or YELLOW; tie color to topic family (BLUE = data, GREEN = success, RED = danger, PURPLE = orchestration)
- Icons: use `ICON_*` constants from `libs.ddia_components`; SVGs live under `assets/icons/`
- One question = one scene cluster (intro + per-part)
