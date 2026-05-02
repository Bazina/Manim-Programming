from __future__ import annotations


def slide_checkpoint(scene, *, phase=False, enabled=True, slide_stop_mode="scene", **next_slide_kwargs):
    """Trigger manim-slides checkpoint with optional phase gating.

    slide_stop_mode:
      - "off": disable all checkpoints
      - "scene": only non-phase checkpoints
      - "phase": both scene and phase checkpoints
    """
    if not enabled:
        return

    if slide_stop_mode == "off":
        return

    if phase and slide_stop_mode != "phase":
        return

    if hasattr(scene, "next_slide"):
        scene.next_slide(**next_slide_kwargs)

