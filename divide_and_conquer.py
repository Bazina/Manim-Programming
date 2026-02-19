import random

from manim import *

from programming_library import create_array_of_numbers, move_pointer

config.background_color = "#0D1117"
text_buffer = 0.18
random.seed(42)


class VisualizeFindKthElementUsingPartitioning(Scene):
    def construct(self):
        # nums = [6, 3, 1, 10, 13, 15, 22]
        nums = [1, 2, 3, 4, 5, 6, 7]
        # nums = [6, 10, 13, 5, 8, 3, 2, 11]
        # k = 1
        k = 1
        self.visualize_find_kth_element(nums, k)

    def visualize_find_kth_element(self, nums, k):
        squares, numbers = create_array_of_numbers(self, nums)
        k_text = Text(
            text=f"k = {k}",
            font_size=28,
            color=BLUE,
            font="JetBrains Mono",
            weight=BOLD,
        ).next_to(squares.get_center(), DOWN * 9)
        self.play(AddTextLetterByLetter(k_text, time_per_char=0.07))
        self.wait(1)

        print(self.find_kth_element(nums, 0, len(nums) - 1, k - 1, squares, numbers))

    def find_kth_element(self, nums, left, right, k, squares, numbers):
        if left <= right:
            pivot_index = self.partition(nums, left, right, squares, numbers)
            if pivot_index == k:
                self.play(squares[pivot_index].animate.set_fill(GREEN, opacity=1).set_stroke(width=0))
                self.wait(3)
                return nums[pivot_index]
            elif pivot_index < k:
                animation_group = []
                for j in range(left, pivot_index + 1):
                    square_color = squares[j].get_color()
                    animation_group.append(squares[j].animate.set_fill(square_color, opacity=0.3))
                    animation_group.append(numbers[j].animate.set_fill(opacity=0.3))

                self.play(
                    *animation_group,
                )
                answer = self.find_kth_element(nums, pivot_index + 1, right, k, squares, numbers)
                self.wait(2)
                return answer
            else:
                animation_group = []
                for j in range(pivot_index, right + 1):
                    square_color = squares[j].get_color()
                    animation_group.append(squares[j].animate.set_fill(square_color, opacity=0.3))
                    animation_group.append(numbers[j].animate.set_fill(opacity=0.3))

                self.play(
                    *animation_group,
                )
                answer = self.find_kth_element(nums, left, pivot_index - 1, k, squares, numbers)
                self.wait(2)
                return answer
        return -1

    def partition(self, nums, left, right, squares, numbers):
        pivot_index = random.randint(left, right)
        self.swap(right, pivot_index, numbers, nums, squares)

        pivot = nums[right]
        pivot_square = squares[right]
        self.play(pivot_square.animate.set_fill(ORANGE, opacity=1))

        boundary = left - 1

        pointers = VGroup(
            Arrow(
                start=squares[left].get_top() + LEFT + UP,
                end=squares[left].get_top() + LEFT,
                buff=0,
                stroke_width=4,
                stroke_color=BLUE
            ),
            Arrow(
                start=squares[left].get_bottom() + DOWN,
                end=squares[left].get_bottom(),
                buff=0,
                stroke_width=4,
                stroke_color=BLUE
            ),
        )

        pointers_labels = VGroup(
            Text(
                text="b",
                font_size=18,
                color=BLUE,
                font="JetBrains Mono",
                weight=BOLD,
            ).next_to(pointers[0], UP),
            Text(
                text="i",
                font_size=18,
                color=BLUE,
                font="JetBrains Mono",
                weight=BOLD,
            ).next_to(pointers[1], DOWN),
        )

        # Show the pointers but not the middle one
        self.play(
            Succession(
                *[GrowArrow(pointer) for pointer in pointers],
                *[AddTextLetterByLetter(pointer_label) for pointer_label in pointers_labels]
            )
        )

        pointers_labels[0].add_updater(
            lambda pointer_mobject: pointer_mobject.next_to(pointers[0], UP)
        )
        self.add(pointers[0], pointers_labels[0])

        pointers_labels[1].add_updater(
            lambda pointer_mobject: pointer_mobject.next_to(pointers[1], DOWN)
        )
        self.add(pointers[1], pointers_labels[1])

        for i in range(left, right + 1):
            self.wait(1)
            move_pointer(self, pointers, 1, squares[i].get_bottom(), UP)
            self.wait(1)
            self.indicate(i, right, numbers, squares, ORANGE)
            self.wait(1)
            if nums[i] <= pivot:
                boundary += 1
                move_pointer(self, pointers, 0, squares[boundary].get_top(), DOWN)
                self.swap(boundary, i, numbers, nums, squares)

        self.play(squares[boundary].animate.set_fill(GREEN, opacity=1))
        self.wait(3)

        self.play(
            AnimationGroup(
                *[FadeOut(pointer) for pointer in pointers],
                *[FadeOut(pointer_label) for pointer_label in pointers_labels],
                lag_ratio=0.0000,
            )
        )

        pointers_labels.remove()
        pointers.remove()

        return boundary

    def swap(self, j, i, numbers, nums, squares):
        nums[j], nums[i] = nums[i], nums[j]
        squares[j], squares[i] = squares[i], squares[j]
        numbers[j], numbers[i] = numbers[i], numbers[j]
        self.indicate(i, j, numbers, squares)
        self.play(
            AnimationGroup(
                Swap(squares[j], squares[i]),
                Swap(numbers[j], numbers[i]),
                lag_ratio=0.0000,
            )
        )

    def indicate(self, i, j, numbers, squares, indicate_color=PURPLE):
        numbers[i].set_z_index(2)
        numbers[j].set_z_index(2)
        self.play(
            AnimationGroup(
                Indicate(numbers[i], color=indicate_color, scale_factor=1.3),
                Indicate(squares[i], color=indicate_color, scale_factor=1.3),
                Indicate(numbers[j], color=indicate_color, scale_factor=1.3),
                Indicate(squares[j], color=indicate_color, scale_factor=1.3),
                lag_ratio=0.0000,
            )
        )
