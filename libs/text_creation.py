from manim import BOLD, DOWN, RIGHT, Text, VGroup

text_buffer = 0.18


def create_code_texts(code_texts, align_position):
    texts_group = VGroup(
        *[
            Text(
                text,
                font_size=18,
                font="JetBrains Mono",
                weight=BOLD,
                stroke_width=0,
                color=text_color,
            )
            for text, text_color, _ in code_texts
        ]
    )
    current_text = texts_group[0]
    for i, text in enumerate(texts_group[1:]):
        buffer = code_texts[i][2] if code_texts[i][2] is not None else text_buffer
        text.next_to(current_text, RIGHT, buffer)
        current_text = text
    texts_group.align_to(align_position)
    texts_group.shift(2.5 * DOWN)
    return texts_group
