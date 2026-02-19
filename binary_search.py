from manim import *

from libs.utils import move_pointer
from libs.array_creation import create_array_of_numbers

config.background_color = "#0D1117"
text_buffer = 0.18


class VisualizeBinarySearchPerspective(Scene):
    def construct(self):
        # Array and target
        nums = [1, 2, 2, 4, 5, 6, 7, 7, 8, 9]
        target = 7

        squares, numbers = create_array_of_numbers(self, nums)

        target_text = Text(
            text="Target = " + str(target),
            font_size=28,
            color=BLUE,
            font="JetBrains Mono",
            weight=BOLD,
        ).next_to(squares.get_center(), DOWN * 4)
        self.play(AddTextLetterByLetter(target_text, time_per_char=0.07))
        self.wait(1)

        how_to_interpret_bs = Text(
            text="How to interpret Binary Search?",
            font_size=32,
            color=ORANGE,
            font="JetBrains Mono",
            weight=BOLD,
        ).next_to(squares.get_center(), UP * 5)
        self.play(AddTextLetterByLetter(how_to_interpret_bs, time_per_char=0.07))
        self.wait(2)

        squares.save_state()
        numbers.save_state()

        self.play(
            Succession(
                AnimationGroup(
                    *[squares[i].animate.set_fill(RED, opacity=0.8) for i in range(6)],
                    squares[6].animate.set_fill(GREEN, opacity=0.8),
                    squares[7].animate.set_fill(GREEN, opacity=0.8),
                    *[squares[i].animate.set_fill(RED, opacity=0.8) for i in range(8, len(nums))]
                )
            )
        )

        self.wait(2)

        target_lower_bound_text = Text(
            text="Insert 7 Before First 7 (Like Lower Bound) = " + str(target),
            font_size=28,
            color=BLUE,
            font="JetBrains Mono",
            weight=BOLD,
        ).next_to(squares.get_center(), DOWN * 4)

        self.play(ReplacementTransform(target_text, target_lower_bound_text))

        how_to_interpret_bs.add_updater(
            lambda squares_mobject: squares_mobject.next_to(squares.get_center(), UP * 6)
        )

        target_lower_bound_text.add_updater(
            lambda squares_mobject: squares_mobject.next_to(squares.get_center(), DOWN * 4)
        )

        self.play(
            Succession(
                Restore(squares),
                AnimationGroup(
                    *[squares[i].animate.set_fill(GREEN, opacity=0.1 * (i + 1)) for i in range(6)],
                    *[squares[i].animate.set_fill(RED, opacity=0.1 * (i + 1)) for i in range(6, len(nums))]
                ),
            )
        )

        self.wait(2)

        self.play(
            AnimationGroup(
                squares.animate.shift(UP * 2).scale(0.8).set_stroke(width=3),
                numbers.animate.shift(UP * 2).scale(0.8),
                target_lower_bound_text.animate.scale(0.75),
                how_to_interpret_bs.animate.scale(0.8)
            )
        )

        self.wait(2)

        code_font = 20
        if_cond_1 = Text(
            text="if target > nums[mid]:",
            font_size=code_font,
            color=BLUE,
            font="JetBrains Mono",
            t2c={
                "if": PURPLE,
                "target": ORANGE,
                ">": BLUE,
                "nums": ORANGE,
                "[mid]": WHITE,
                ":": BLUE
            }
        ).next_to(squares.get_center(), DOWN * 7)

        if_cond_1_statement = Text(
            text="left = mid + 1",
            font_size=code_font,
            color=BLUE,
            font="JetBrains Mono",
            t2c={
                "left": ORANGE,
                "=": BLUE,
                "mid": ORANGE,
                "+": BLUE,
                "1": ORANGE
            }
        ).align_to(if_cond_1, LEFT).shift(DOWN * 0.25).shift(RIGHT * 0.4)

        else_1 = Text(
            text="else:",
            font_size=code_font,
            color=BLUE,
            font="JetBrains Mono",
            t2c={
                "else": PURPLE,
                ":": BLUE
            }
        ).align_to(if_cond_1, LEFT).shift(DOWN * 0.6)

        else_1_statement = Text(
            text="right = mid",
            font_size=code_font,
            color=BLUE,
            font="JetBrains Mono",
            t2c={
                "right": ORANGE,
                "=": BLUE,
                "mid": ORANGE,
            }
        ).align_to(if_cond_1, LEFT).shift(DOWN * 1).shift(RIGHT * 0.4)

        self.play(
            Succession(
                AddTextLetterByLetter(if_cond_1),
                AddTextLetterByLetter(if_cond_1_statement),
                AddTextLetterByLetter(else_1),
                AddTextLetterByLetter(else_1_statement)
            )
        )

        self.wait(2)

        self.play(
            AnimationGroup(
                Restore(numbers),
                Restore(squares),
                FadeOut(target_lower_bound_text),
                FadeOut(if_cond_1),
                FadeOut(if_cond_1_statement),
                FadeOut(else_1),
                FadeOut(else_1_statement),
                FadeOut(how_to_interpret_bs)
            )
        )

        # Binary search visualization
        left, right, mid = 0, len(nums), 0
        pointers = VGroup(
            Arrow(
                start=squares[left].get_top() + UP,
                end=squares[left].get_top(),
                buff=0,
                stroke_width=4,
                stroke_color=BLUE
            ),
            Arrow(
                start=squares[right - 1].get_bottom() + RIGHT + DOWN,
                end=squares[right - 1].get_bottom() + RIGHT,
                buff=0,
                stroke_width=4,
                stroke_color=BLUE,
            ),
        )

        pointers_labels = VGroup(
            Text(
                text="left",
                font_size=18,
                color=BLUE,
                font="JetBrains Mono",
                weight=BOLD,
            ).next_to(pointers[0], UP),
            Text(
                text="right",
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

        next_condition_text_factor = 3.5

        while left < right:
            mid = (left + right) // 2

            if len(pointers) != 3:
                pointers.add(
                    Arrow(
                        start=squares[mid].get_bottom() + 0.75 * DOWN,
                        end=squares[mid].get_bottom(),
                        buff=0,
                        stroke_width=4,
                        stroke_color=YELLOW
                    )
                )

                pointers_labels.add(
                    Text(
                        text="mid",
                        font_size=18,
                        color=ORANGE,
                        font="JetBrains Mono",
                        weight=BOLD,
                    ),
                )

                pointers_labels[2].add_updater(
                    lambda pointer_mobject: pointer_mobject.next_to(pointers[2], DOWN)
                )
                self.add(pointers[2], pointers_labels[2])

                self.play(AnimationGroup(
                    GrowArrow(pointers[-1]),
                    AddTextLetterByLetter(pointers_labels[-1])
                ))
            else:
                self.play(pointers[-1].animate.move_to(squares[mid].get_bottom(), aligned_edge=UP))

            # Highlight the middle element
            squares[mid].z_index = 1
            self.play(squares[mid].animate.set_stroke(width=7, color=YELLOW))
            self.play(
                Indicate(squares[mid], color=YELLOW, scale_factor=1.3),
                Indicate(numbers[mid], color=YELLOW, scale_factor=1.3)
            )
            self.wait(1)
            self.play(squares[mid].animate.set_fill(YELLOW, opacity=0.5))
            self.wait(1)

            if target > nums[mid]:
                move_pointer(self, pointers, 0, squares[mid + 1].get_top(), DOWN)
                left = mid + 1
                self.wait(2)
            else:
                move_pointer(self, pointers, 1, squares[mid].get_bottom(), UP)
                right = mid
                self.wait(2)

            next_condition_text_factor -= 0.3

            self.play(
                Succession(
                    squares[mid].animate.set_fill(WHITE, opacity=0.6).set_stroke(width=0).set_z_index(0),
                    FadeToColor(numbers[mid], "#0D1117"),
                )
            )

        self.play(squares[left].animate.set_fill(GREEN, opacity=0.5).set_stroke(GREEN, width=2))
        self.wait(3)


class VisualizeBinarySearch(Scene):
    code_font = 18

    @staticmethod
    def animate(object_to_animate: VMobject):
        object_stroke_width = 2.5
        if isinstance(object_to_animate, VGroup) and isinstance(object_to_animate[0], Text):
            object_stroke_width = 0
        return object_to_animate.animate.shift(LEFT * 3).scale(0.7).set_stroke(width=object_stroke_width)

    def binary_search_visualize(self, nums, low, high, key, numbers, squares, pointers, pointers_labels, stack,
                                stack_container):
        if low > high:
            return -1

        mid = (low + high) // 2

        if len(pointers) != 3:
            pointers.add(
                Arrow(
                    start=squares[mid].get_bottom() + 0.4 * DOWN,
                    end=squares[mid].get_bottom(),
                    buff=0,
                    stroke_width=2,
                    stroke_color=YELLOW
                )
            )

            pointers_labels.add(
                Text(
                    text="mid",
                    font_size=self.code_font,
                    color=ORANGE,
                    font="JetBrains Mono",
                    weight=BOLD,
                ),
            )

            pointers_labels[2].add_updater(
                lambda pointer_mobject: pointer_mobject.next_to(pointers[2], DOWN * 0.8)
            )
            self.add(pointers[2], pointers_labels[2])

            self.play(AnimationGroup(
                GrowArrow(pointers[-1]),
                AddTextLetterByLetter(pointers_labels[-1])
            ))
        else:
            self.play(pointers[-1].animate.move_to(squares[mid].get_bottom(), aligned_edge=UP))

        if nums[mid] == key:
            self.play(
                Succession(
                    squares[mid].animate.set_fill(WHITE, opacity=0.6).set_stroke(width=0).set_z_index(0),
                    FadeToColor(numbers[mid], "#0D1117"),
                )
            )

            bs_cond = Text(
                text="target == nums[mid]",
                font_size=self.code_font,
                color=BLUE,
                font="JetBrains Mono",
                t2c={
                    "target": ORANGE,
                    "==": BLUE,
                    "nums": ORANGE,
                    "[mid]": WHITE
                }
            ).next_to(squares.get_center(), DOWN * 6)

            self.play(
                AddTextLetterByLetter(bs_cond),
            )
            self.wait(1)

            self.play(squares[mid].animate.set_fill(GREEN, opacity=0.5).set_stroke(GREEN, width=2))
            self.play(bs_cond.animate.shift(LEFT * 10))
            self.wait(3)

            return mid
        if nums[mid] < key:
            self.play(
                Succession(
                    squares[mid].animate.set_fill(WHITE, opacity=0.6).set_stroke(width=0).set_z_index(0),
                    FadeToColor(numbers[mid], "#0D1117"),
                )
            )

            bs_cond = Text(
                text="target > nums[mid]",
                font_size=self.code_font,
                color=BLUE,
                font="JetBrains Mono",
                t2c={
                    "target": ORANGE,
                    ">": BLUE,
                    "nums": ORANGE,
                    "[mid]": WHITE
                }
            ).next_to(squares.get_center(), DOWN * 6)

            self.play(
                AddTextLetterByLetter(bs_cond),
            )
            self.wait(1)

            move_pointer(self, pointers, 0, squares[mid + 1].get_top(), DOWN)
            self.play(bs_cond.animate.shift(LEFT * 10))

            self.create_new_stack_frame(stack, low, high, key)

            return self.binary_search_visualize(nums, mid + 1, high, key, numbers, squares, pointers, pointers_labels,
                                                stack, stack_container)

        self.play(
            Succession(
                squares[mid].animate.set_fill(WHITE, opacity=0.6).set_stroke(width=0).set_z_index(0),
                FadeToColor(numbers[mid], "#0D1117"),
            )
        )

        bs_cond = Text(
            text="target < nums[mid]",
            font_size=self.code_font,
            color=BLUE,
            font="JetBrains Mono",
            t2c={
                "target": ORANGE,
                "<": BLUE,
                "nums": ORANGE,
                "[mid]": WHITE
            }
        ).next_to(squares.get_center(), DOWN * 6)

        self.play(
            AddTextLetterByLetter(bs_cond),
        )

        self.wait(1)
        move_pointer(self, pointers, 1, squares[mid - 1].get_bottom(), UP)
        self.play(bs_cond.animate.shift(LEFT * 10))

        self.create_new_stack_frame(stack, low, high, key)

        return self.binary_search_visualize(nums, low, mid - 1, key, numbers, squares, pointers, pointers_labels, stack,
                                            stack_container)

    def construct(self):
        # Array and target
        nums = [1, 2, 2, 4, 5, 6, 7, 7, 8, 9]
        target = 4

        squares, numbers = create_array_of_numbers(self, nums, animate=VisualizeBinarySearch.animate)

        pointers = VGroup(
            Arrow(
                start=squares[0].get_top() + UP * 0.5,
                end=squares[0].get_top(),
                buff=0,
                stroke_width=3.5,
                stroke_color=BLUE
            ),
            Arrow(
                start=squares[len(nums) - 1].get_bottom() + DOWN * 0.5,
                end=squares[len(nums) - 1].get_bottom(),
                buff=0,
                stroke_width=3.5,
                stroke_color=BLUE,
            ),
        )

        pointers_labels = VGroup(
            Text(
                text="left",
                font_size=self.code_font,
                color=BLUE,
                font="JetBrains Mono",
                weight=BOLD,
            ).next_to(pointers[0], UP * 0.6),
            Text(
                text="right",
                font_size=self.code_font,
                color=BLUE,
                font="JetBrains Mono",
                weight=BOLD,
            ).next_to(pointers[1], DOWN * 0.6),
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

        stack_container = Rectangle(width=5, height=1).shift(RIGHT * 4)
        stack = VGroup()
        stack_text = Text(
            text="Stack",
            font_size=24,
            color=BLUE,
            font="JetBrains Mono",
            weight=BOLD,
        )

        stack_text.add_updater(
            lambda stack_text_mobject: stack_text_mobject.next_to(stack.get_top(), UP)
        )

        # self.play(
        #    AnimationGroup(
        #        Create(stack_container)
        #    )
        # )

        self.create_new_stack_frame(stack, 0, len(nums) - 1, target)
        self.play(
            AddTextLetterByLetter(stack_text)
        )

        # def update_container_size(mobject):
        #    new_height = 5 * len(stack)
        #    mobject.stretch_to_fit_width(new_height)

        # stack_container.add_updater(
        #    update_container_size
        # )

        self.binary_search_visualize(nums, 0, len(nums) - 1, target, numbers, squares, pointers, pointers_labels, stack,
                                     stack_container)

    def create_new_stack_frame(self, stack, left, right, target):
        stack_frame = Rectangle(
            width=4.8,
            height=0.8,
        ).shift(RIGHT * 4)

        stack_frame_text = Text(
            text=f"binary_search(nums, {left}, {right}, {target})",
            font_size=18,
            color=WHITE,
            font="JetBrains Mono",
            weight=BOLD
        ).move_to(stack_frame.get_center())

        if len(stack) >= 1:
            self.play(
                stack.animate.shift(UP * 0.5)
            )

            self.play(
                AnimationGroup(
                    Create(stack_frame.shift(DOWN * 0.4 * len(stack))),
                    AddTextLetterByLetter(stack_frame_text.shift(DOWN * 0.4 * len(stack)))
                )
            )

            stack.add(
                VGroup(
                    stack_frame,
                    stack_frame_text
                )
            )
        else:
            self.play(
                AnimationGroup(
                    Create(stack_frame),
                    AddTextLetterByLetter(stack_frame_text)
                )
            )

            stack.add(
                VGroup(
                    stack_frame,
                    stack_frame_text
                )
            )


class VisualizeRotatedBinarySearch(Scene):
    code_font = 18

    def construct(self):
        text_buffer = 0.18
        # Array and target
        nums = [4, 5, 6, 7, 0, 1, 2]
        target = 0

        squares, numbers = create_array_of_numbers(self, nums)

        # Give Intuition before starting the visualization
        # Show the sorted parts of the array
        squares.save_state()
        numbers.save_state()

        self.play(
            AnimationGroup(*[squares[i].animate.set_fill(BLUE, opacity=0.1 * (i + 1)) for i in range(4)],
                           lag_ratio=0.1),
            AnimationGroup(*[squares[i].animate.set_fill(ORANGE, opacity=0.1 * (i + 1)) for i in range(4, 7)],
                           lag_ratio=0.1)
        )

        self.wait(2)

        self.play(Restore(squares))

        # Binary search visualization
        left, right = 0, len(nums) - 1
        mid = (left + right) // 2
        pointers = VGroup(
            Arrow(
                start=squares[left].get_top() + UP,
                end=squares[left].get_top(),
                buff=0,
                stroke_width=4,
                stroke_color=BLUE
            ),
            Arrow(
                start=squares[right].get_bottom() + DOWN,
                end=squares[right].get_bottom(),
                buff=0,
                stroke_width=4,
                stroke_color=BLUE,
            ),
            Arrow(
                start=squares[mid].get_bottom() + 0.75 * DOWN,
                end=squares[mid].get_bottom(),
                buff=0,
                stroke_width=4,
                stroke_color=YELLOW
            )
        )

        pointers_labels = VGroup(
            Text(
                text="left",
                font_size=18,
                color=BLUE,
                font="JetBrains Mono",
                weight=BOLD,
            ).next_to(pointers[0], UP),
            Text(
                text="right",
                font_size=18,
                color=BLUE,
                font="JetBrains Mono",
                weight=BOLD,
            ).next_to(pointers[1], DOWN),
            Text(
                text="mid",
                font_size=18,
                color=ORANGE,
                font="JetBrains Mono",
                weight=BOLD,
            ).next_to(pointers[2], DOWN),
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

        pointers_labels[2].add_updater(
            lambda pointer_mobject: pointer_mobject.next_to(pointers[2], DOWN)
        )
        self.add(pointers[2], pointers_labels[2])

        pointers[0].save_state()
        pointers[1].save_state()
        pointers[2].save_state()

        next_condition_text_factor = 3.5

        t2c = {
            "target": ORANGE,
            "nums": ORANGE,
            "[": WHITE,
            "]": WHITE,
            "left": ORANGE,
            "right": ORANGE,
            "mid": ORANGE,
            "or": PURPLE,
            "and": PURPLE
        }

        # Showing Conditions
        left, right = 0, len(nums) - 1
        mid = (left + right) // 2
        self.play(
            pointers[0].animate.move_to(squares[left].get_top(), aligned_edge=DOWN),
            pointers[1].animate.move_to(squares[right].get_bottom(), aligned_edge=UP),
            pointers[2].animate.move_to(squares[mid].get_bottom(), aligned_edge=UP),
        )
        self.wait(2)

        left, right = 0, len(nums) - 4
        mid = (left + right) // 2
        self.play(
            pointers[0].animate.move_to(squares[left].get_top(), aligned_edge=DOWN),
            pointers[1].animate.move_to(squares[right].get_bottom(), aligned_edge=UP),
            pointers[2].animate.move_to(squares[mid].get_bottom(), aligned_edge=UP),
        )
        self.wait(2)

        left, right = 4, len(nums) - 1
        mid = (left + right) // 2
        self.play(
            pointers[0].animate.move_to(squares[left].get_top(), aligned_edge=DOWN),
            pointers[1].animate.move_to(squares[right].get_bottom(), aligned_edge=UP),
            pointers[2].animate.move_to(squares[mid].get_bottom(), aligned_edge=UP),
        )
        self.wait(2)

        self.play(
            Restore(pointers[0]),
            Restore(pointers[1]),
            Restore(pointers[2])
        )

        left, right, mid = 0, len(nums) - 1, 0
        while left <= right:
            mid = (left + right) // 2

            self.play(pointers[-1].animate.move_to(squares[mid].get_bottom(), aligned_edge=UP))

            # Highlight the middle element
            squares[mid].z_index = 1
            self.play(squares[mid].animate.set_stroke(width=7, color=YELLOW))
            self.play(
                Indicate(squares[mid], color=YELLOW, scale_factor=1.3),
                Indicate(numbers[mid], color=YELLOW, scale_factor=1.3)
            )
            self.wait(1)
            self.play(squares[mid].animate.set_fill(YELLOW, opacity=0.5))
            self.wait(1)

            if nums[mid] == target:
                self.play(
                    Indicate(squares[mid]),
                    squares[mid].animate.set_fill(GREEN, opacity=0.5)
                )
                break

            def move_condition_texts_to_log(condition_texts, math_condition):
                self.play(
                    Transform(condition_texts, math_condition)
                )

                self.wait(2)

                self.play(
                    AnimationGroup(
                        condition_texts
                        .animate
                        .scale(0.65)
                        .move_to(squares.get_center())
                        .shift(UP * next_condition_text_factor)
                    )
                )

            if nums[left] <= nums[mid]:
                bs_cond = Text(
                    text="nums[left] <= nums[mid]",
                    font_size=self.code_font,
                    font="JetBrains Mono",
                    t2c={
                        **t2c,
                        "<=": BLUE
                    },
                ).next_to(squares.get_center(), DOWN).shift(2 * DOWN)

                self.play(AddTextLetterByLetter(bs_cond))
                self.wait(2)
                self.play(FadeOut(bs_cond))

                if target > nums[mid] or target < nums[left]:
                    move_pointer(self, pointers, 0, squares[mid + 1].get_top(), DOWN)
                    left = mid + 1

                    bs_cond = Text(
                        text="target > nums[mid] or target < nums[left]",
                        font_size=self.code_font,
                        font="JetBrains Mono",
                        t2c={
                            **t2c,
                            "<": BLUE,
                            ">": BLUE
                        }
                    ).next_to(squares.get_center(), DOWN).shift(2 * DOWN)

                    self.play(AddTextLetterByLetter(bs_cond))
                    self.wait(2)

                    math_condition = Text(
                        f"{target} > {nums[mid]} or {target} < {nums[left]}",
                        font_size=self.code_font,
                        color=ORANGE,
                        font="JetBrains Mono",
                        t2c={
                            **t2c,
                            ">": BLUE,
                            "<": BLUE
                        }
                    ).next_to(squares.get_center(), DOWN).shift(2 * DOWN)
                    move_condition_texts_to_log(bs_cond, math_condition)
                else:
                    move_pointer(self, pointers, 1, squares[mid - 1].get_bottom(), UP)
                    right = mid - 1

                    bs_cond = Text(
                        text="target <= nums[mid] and target >= nums[left]",
                        font_size=self.code_font,
                        font="JetBrains Mono",
                        t2c={
                            **t2c,
                            "<=": BLUE,
                            ">=": BLUE
                        }
                    ).next_to(squares.get_center(), DOWN).shift(2 * DOWN)

                    self.play(AddTextLetterByLetter(bs_cond))
                    self.wait(2)

                    math_condition = Text(
                        f"{target} <= {nums[mid]} and {target} >= {nums[left]}",
                        font_size=self.code_font,
                        color=ORANGE,
                        font="JetBrains Mono",
                        t2c={
                            **t2c,
                            "<=": BLUE,
                            ">=": BLUE
                        }
                    ).next_to(squares.get_center(), DOWN).shift(2 * DOWN)
                    move_condition_texts_to_log(bs_cond, math_condition)
            else:
                bs_cond = Text(
                    text="nums[left] > nums[mid]",
                    font_size=self.code_font,
                    font="JetBrains Mono",
                    t2c={
                        **t2c,
                        ">": BLUE
                    }
                ).next_to(squares.get_center(), DOWN).shift(2 * DOWN)

                self.play(AddTextLetterByLetter(bs_cond))
                self.wait(2)
                self.play(FadeOut(bs_cond))
                if target < nums[mid] or target > nums[right]:
                    move_pointer(self, pointers, 1, squares[mid - 1].get_bottom(), UP)
                    right = mid - 1

                    bs_cond = Text(
                        text="target < nums[mid] or target > nums[right]",
                        font_size=self.code_font,
                        font="JetBrains Mono",
                        t2c={
                            **t2c,
                            "<": BLUE,
                            ">": BLUE
                        }
                    ).next_to(squares.get_center(), DOWN).shift(2 * DOWN)

                    self.play(AddTextLetterByLetter(bs_cond))
                    self.wait(2)

                    math_condition = Text(
                        f"{target} < {nums[mid]} or {target} > {nums[right]}",
                        font_size=self.code_font,
                        color=ORANGE,
                        font="JetBrains Mono",
                        t2c={
                            **t2c,
                            "<": BLUE,
                            ">": BLUE
                        }
                    ).next_to(squares.get_center(), DOWN).shift(2 * DOWN)
                    move_condition_texts_to_log(bs_cond, math_condition)
                else:
                    move_pointer(self, pointers, 0, squares[mid + 1].get_top(), DOWN)
                    left = mid + 1

                    bs_cond = Text(
                        text="target >= nums[mid] and target <= nums[right]",
                        font_size=self.code_font,
                        font="JetBrains Mono",
                        t2c={
                            **t2c,
                            "<=": BLUE,
                            ">=": BLUE
                        }
                    ).next_to(squares.get_center(), DOWN).shift(2 * DOWN)

                    self.play(AddTextLetterByLetter(bs_cond))
                    self.wait(2)

                    math_condition = Text(
                        f"{target} >= {nums[mid]} and {target} <= {nums[right]}",
                        font_size=self.code_font,
                        color=ORANGE,
                        font="JetBrains Mono",
                        t2c={
                            **t2c,
                            "<=": BLUE,
                            ">=": BLUE
                        }
                    ).next_to(squares.get_center(), DOWN).shift(2 * DOWN)
                    move_condition_texts_to_log(bs_cond, math_condition)

            next_condition_text_factor -= 0.3
            # Reset the middle element color
            self.play(
                Succession(
                    squares[mid].animate.set_fill(WHITE, opacity=0.6).set_stroke(width=0).set_z_index(0),
                    FadeToColor(numbers[mid], "#0D1117"),
                )
            )

        # Highlight the final position
        if nums[mid] == target:
            self.play(squares[mid].animate.set_fill(GREEN, opacity=0.5).set_stroke(GREEN))
        else:
            self.play(squares[mid].animate.set_fill(RED, opacity=0.8))

        self.wait(2)


class VisualizeRotatedBinarySearchWithOffset(Scene):
    code_font = 18

    def construct(self):
        text_buffer = 0.18
        # Array and target
        nums = [4, 5, 6, 7, 0, 1, 2]
        target = 0

        squares, numbers = create_array_of_numbers(self, nums)

        # Give Intuition before starting the visualization
        # Show the sorted parts of the array
        squares.save_state()
        numbers.save_state()

        self.play(
            AnimationGroup(*[squares[i].animate.set_fill(BLUE, opacity=0.1 * (i + 1)) for i in range(4)],
                           lag_ratio=0.1),
            AnimationGroup(*[squares[i].animate.set_fill(ORANGE, opacity=0.1 * (i + 1)) for i in range(4, 7)],
                           lag_ratio=0.1)
        )

        self.wait(2)

        self.play(Restore(squares))

        # Binary search visualization
        left, right = 0, len(nums) - 1
        mid = (left + right) // 2
        pointers = VGroup(
            Arrow(
                start=squares[left].get_top() + UP,
                end=squares[left].get_top(),
                buff=0,
                stroke_width=4,
                stroke_color=BLUE
            ),
            Arrow(
                start=squares[right].get_bottom() + DOWN,
                end=squares[right].get_bottom(),
                buff=0,
                stroke_width=4,
                stroke_color=BLUE,
            ),
            Arrow(
                start=squares[mid].get_bottom() + 0.75 * DOWN,
                end=squares[mid].get_bottom(),
                buff=0,
                stroke_width=4,
                stroke_color=YELLOW
            )
        )

        pointers_labels = VGroup(
            Text(
                text="left",
                font_size=18,
                color=BLUE,
                font="JetBrains Mono",
                weight=BOLD,
            ).next_to(pointers[0], UP),
            Text(
                text="right",
                font_size=18,
                color=BLUE,
                font="JetBrains Mono",
                weight=BOLD,
            ).next_to(pointers[1], DOWN),
            Text(
                text="mid",
                font_size=18,
                color=ORANGE,
                font="JetBrains Mono",
                weight=BOLD,
            ).next_to(pointers[2], DOWN),
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

        pointers_labels[2].add_updater(
            lambda pointer_mobject: pointer_mobject.next_to(pointers[2], DOWN)
        )
        self.add(pointers[2], pointers_labels[2])

        pointers[0].save_state()
        pointers[1].save_state()
        pointers[2].save_state()

        # write Find Offset as text

        find_offset_text = Text(
            text="Find Offset",
            font_size=32,
            color=BLUE,
            font="JetBrains Mono",
            weight=BOLD,
        ).next_to(squares.get_center(), UP * 9)

        self.play(
            AddTextLetterByLetter(find_offset_text)
        )

        # Find offset
        offset = self.find_offset(nums, 0, len(nums) - 1, squares, pointers)
        self.play(
            find_offset_text.animate.shift(LEFT * 100)
        )
        self.wait(2)

        move_pointer(self, pointers, 0, squares[offset].get_top(), DOWN)
        if len(nums) - 1 + offset < len(nums):
            move_pointer(self, pointers, 1, squares[len(nums) - 1 + offset].get_bottom(), UP)
        else:
            move_pointer(self, pointers, 1, squares[len(nums) - 1].get_bottom() + RIGHT, UP)

        self.wait(2)

        # Binary search visualization with offset
        self.rotated_binary_search_visualize(nums, target, offset, len(nums) - 1 + offset, numbers, squares, pointers)

    def find_offset(self, nums, i, j, squares, pointers):
        if i == j:
            self.play(
                squares[i].animate.set_fill(GREEN, opacity=0.5),
            )
            return i

        mid = (i + j) // 2

        move_pointer(self, pointers, 2, squares[mid].get_bottom(), UP)

        squares[mid].save_state()

        self.play(
            squares[mid].animate.set_fill(YELLOW, opacity=0.6),
        )
        self.wait(1)
        self.play(Restore(squares[mid]))

        if nums[mid] < nums[j]:
            move_pointer(self, pointers, 1, squares[mid].get_bottom(), UP)
            self.wait(2)
            return self.find_offset(nums, i, mid, squares, pointers)
        else:
            move_pointer(self, pointers, 0, squares[mid + 1].get_top(), DOWN)
            self.wait(2)
            return self.find_offset(nums, mid + 1, j, squares, pointers)

    def rotated_binary_search_visualize(self, nums, target, i, j, numbers, squares, pointers):
        if i > j:
            return -1

        mid = (i + j) // 2
        mid_index = mid % len(nums)

        # write text with mid and mid_index values

        mid_text = Text(
            text=f"mid = {mid}",
            font_size=24,
            color=BLUE,
            font="JetBrains Mono",
            weight=BOLD,
        ).next_to(squares.get_center(), DOWN * 9)

        mid_index_text = Text(
            text=f"mid_index = {mid_index}",
            font_size=24,
            color=BLUE,
            font="JetBrains Mono",
            weight=BOLD,
        ).next_to(mid_text, DOWN)

        move_pointer(self, pointers, 2, squares[mid_index].get_bottom(), UP)

        self.play(
            Indicate(squares[mid_index], color=YELLOW, scale_factor=1.3),
            AddTextLetterByLetter(mid_text),
            AddTextLetterByLetter(mid_index_text)
        )
        self.wait(1)
        self.play(
            mid_text.animate.shift(LEFT * 10),
            mid_index_text.animate.shift(LEFT * 10)
        )

        if nums[mid_index] == target:
            self.play(
                Indicate(squares[mid_index]),
                squares[mid_index].animate.set_fill(GREEN, opacity=0.5)
            )
            return mid_index
        elif nums[mid_index] > target:
            move_pointer(self, pointers, 1, squares[mid_index - 1].get_bottom(), UP)
            return self.rotated_binary_search_visualize(nums, target, i, mid - 1, numbers, squares, pointers)
        else:
            move_pointer(self, pointers, 0, squares[mid_index + 1].get_top(), DOWN)
            return self.rotated_binary_search_visualize(nums, target, mid + 1, j, numbers, squares, pointers)
