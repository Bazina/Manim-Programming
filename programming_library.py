from manim import *

text_buffer = 0.18


def create_array_of_numbers(scene, nums, animate=None, font_size=36, side_length=1, stroke_width=5, position=ORIGIN):
    # Create squares for each element in the array
    squares = VGroup(*[Square(side_length=side_length, stroke_width=stroke_width) for _ in nums])
    squares.arrange(RIGHT, buff=0)
    squares.move_to(position)
    scene.play(AnimationGroup(*[Create(square) for square in squares], lag_ratio=0.1))

    # Add numbers inside the squares
    numbers = VGroup(
        *[Text(str(num), font_size=font_size, font="JetBrains Mono", weight=BOLD, stroke_width=0, z_index=2) for num in
          nums])

    for i in range(len(numbers)):
        numbers[i].move_to(squares[i].get_center())

    numbers.move_to(position)

    scene.play(Create(numbers))

    if animate is not None:
        scene.play(
            AnimationGroup(
                animate(squares),
                animate(numbers)
            )
        )

    scene.wait(1)

    return squares, numbers


def create_code_texts(code_texts, align_position):
    texts_group = VGroup(
        *[Text(text, font_size=18, font="JetBrains Mono", weight=BOLD, stroke_width=0, color=text_color)
          for text, text_color, _ in code_texts]
    )
    current_text = texts_group[0]
    for i, text in enumerate(texts_group[1:]):
        buffer = code_texts[i][2] if code_texts[i][
                                         2] is not None else text_buffer
        text.next_to(current_text, RIGHT, buffer)
        current_text = text
    texts_group.align_to(align_position)
    texts_group.shift(2.5 * DOWN)
    return texts_group


def move_pointer(scene, pointers, pointer_index, new_position, alignment):
    scene.play(pointers[pointer_index].animate.move_to(new_position, aligned_edge=alignment))
