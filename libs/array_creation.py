from manim import BOLD, ORIGIN, RIGHT, AnimationGroup, Create, Square, Text, VGroup


def create_array_of_numbers(
    scene,
    nums,
    animate=None,
    font_size=36,
    side_length=1,
    stroke_width=5,
    position=ORIGIN,
):
    # Create squares for each element in the array
    squares = VGroup(
        *[Square(side_length=side_length, stroke_width=stroke_width) for _ in nums]
    )
    squares.arrange(RIGHT, buff=0)
    squares.move_to(position)
    scene.play(AnimationGroup(*[Create(square) for square in squares], lag_ratio=0.1))

    # Add numbers inside the squares
    numbers = VGroup(
        *[
            Text(
                str(num),
                font_size=font_size,
                font="JetBrains Mono",
                weight=BOLD,
                stroke_width=0,
                z_index=2,
            )
            for num in nums
        ]
    )

    for i in range(len(numbers)):
        numbers[i].move_to(squares[i].get_center())

    numbers.move_to(position)

    scene.play(Create(numbers))

    if animate is not None:
        scene.play(AnimationGroup(animate(squares), animate(numbers)))

    scene.wait(1)

    return squares, numbers
