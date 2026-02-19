import bisect
import random

from manim import *

from libs.array_creation import create_array_of_numbers

config.background_color = "#0D1117"
text_buffer = 0.18
random.seed(42)


class VisualizeMaximumProfitInJobScheduling(Scene):
    def construct(self):
        start_times = [1, 2, 3, 4, 6]
        end_times = [3, 5, 10, 6, 9]
        profits = [20, 20, 100, 70, 60]
        self.visualize_find_kth_element(start_times, end_times, profits)

    def visualize_find_kth_element(self, start_times, end_times, profits):
        print(self.job_scheduling(start_times, end_times, profits))

    def job_scheduling(self, start_times, end_times, profits):
        jobs = sorted(zip(start_times, end_times, profits))

        start_times = [job[0] for job in jobs]
        end_times = [job[1] for job in jobs]
        profits = [job[2] for job in jobs]

        start_times_squares, start_times_numbers = create_array_of_numbers(self, start_times, font_size=24,
                                                                           side_length=0.75, position=UP * 3)
        start_times_text = Text(
            text="Start Times",
            font_size=28,
            color=BLUE,
            font="JetBrains Mono",
            weight=BOLD,
        ).next_to(start_times_squares.get_center(), LEFT * 10)
        start_times_text.add_updater(
            lambda x: x.next_to(start_times_squares.get_center(), LEFT * 10)
        )
        self.play(
            AnimationGroup(
                AddTextLetterByLetter(start_times_text),
            )
        )

        end_times_squares, end_times_numbers = create_array_of_numbers(self, end_times, font_size=24, side_length=0.75,
                                                                       position=UP * 2)
        end_times_text = Text(
            text="End Times",
            font_size=28,
            color=PURPLE,
            font="JetBrains Mono",
            weight=BOLD,
        ).next_to(end_times_squares.get_center(), LEFT * 10)
        end_times_text.add_updater(
            lambda x: x.next_to(end_times_squares.get_center(), LEFT * 10)
        )
        self.play(
            AnimationGroup(
                AddTextLetterByLetter(end_times_text),
            )
        )

        profits_squares, profits_numbers = create_array_of_numbers(self, profits, font_size=24, side_length=0.75,
                                                                   position=UP)
        profits_text = Text(
            text="Profits",
            font_size=28,
            color=GREEN,
            font="JetBrains Mono",
            weight=BOLD,
        ).next_to(profits_squares.get_center(), LEFT * 10)
        profits_text.add_updater(
            lambda x: x.next_to(profits_squares.get_center(), LEFT * 10)
        )
        self.play(
            AnimationGroup(
                AddTextLetterByLetter(profits_text),
            )
        )

        n = len(start_times)
        dp = [0] * (n + 1)
        dp_squares, dp_numbers = create_array_of_numbers(self, dp, font_size=32, position=DOWN)

        def iterative():
            dp[0] = 0
            for i in range(1, n + 1):
                dp[i] = jobs[i - 1][2]
                new_number = Text(str(dp[i]), font_size=32, font="JetBrains Mono", weight=BOLD, stroke_width=0,
                                  z_index=2).move_to(dp_squares[i].get_center())
                self.play(
                    Succession(
                        RemoveTextLetterByLetter(dp_numbers[i]),
                        AddTextLetterByLetter(new_number),
                        lag_ratio=1.2,
                    )
                )
                remove_dp_number = dp_numbers[i]
                dp_numbers[i] = new_number
                self.remove(remove_dp_number)

            for i in range(n, 0, -1):
                end_time = jobs[i - 1][1]
                profit = jobs[i - 1][2]
                dp_squares[i].save_state()
                end_times_squares[i - 1].save_state()
                profits_squares[i - 1].save_state()
                self.play(
                    AnimationGroup(
                        FadeToColor(dp_squares[i], ORANGE),
                        FadeToColor(end_times_squares[i - 1], PURPLE),
                        FadeToColor(profits_squares[i - 1], GREEN),
                    )
                )

                self.wait(2)
                self.play(
                    AnimationGroup(
                        Indicate(
                            end_times_squares[i - 1], scale_factor=1.5, color=PURPLE
                        ),
                        Indicate(
                            end_times_numbers[i - 1], scale_factor=1.5, color=PURPLE
                        )
                    )
                )
                j = bisect.bisect(jobs, (end_time, -1, -1))

                if j != n:
                    start_times_squares[j].save_state()
                    self.play(
                        AnimationGroup(
                            Indicate(
                                start_times_squares[j], scale_factor=1.5, color=BLUE
                            ),
                            Indicate(
                                start_times_numbers[j], scale_factor=1.5, color=BLUE
                            )
                        )
                    )
                    self.play(
                        FadeToColor(start_times_squares[j], BLUE),
                    )
                    self.wait(2)

                    dp_squares[j + 1].save_state()
                    self.play(
                        AnimationGroup(
                            Indicate(
                                dp_squares[j + 1], scale_factor=1.5, color=GREEN
                            ),
                            Indicate(
                                dp_numbers[j + 1], scale_factor=1.5, color=GREEN
                            )
                        )
                    )
                    self.play(
                        FadeToColor(dp_squares[j + 1], GREEN),
                    )
                    max_text = Text(
                        text=f"max(profit = {profit} + {dp[j + 1]}, dp[{i if i == n else i + 1}] = {dp[i if i == n else i + 1]})",
                        font_size=24,
                        color=ORANGE,
                        font="JetBrains Mono",
                        t2c={
                            "max": BLUE,
                            "profit": GREEN,
                            "dp": GREEN,
                            "(": WHITE,
                            ")": WHITE,
                            "=": BLUE,
                            ",": WHITE,
                            "[": WHITE,
                            "]": WHITE,
                            "+": BLUE,
                        }
                    ).next_to(dp_squares[i].get_center(), DOWN * 4)
                    profit += dp[j + 1]
                    self.play(
                        AddTextLetterByLetter(max_text),
                    )
                    self.wait(2)
                    self.play(
                        Restore(start_times_squares[j]),
                        Restore(dp_squares[j + 1]),
                    )
                else:
                    max_text = Text(
                        text=f"max(profit = {profit}, dp[{i if i == n else i + 1}] = {dp[i if i == n else i + 1]})",
                        font_size=24,
                        color=ORANGE,
                        font="JetBrains Mono",
                        t2c={
                            "max": BLUE,
                            "profit": GREEN,
                            "dp": GREEN,
                            "(": WHITE,
                            ")": WHITE,
                            "=": BLUE,
                            ",": WHITE,
                            "[": WHITE,
                            "]": WHITE,
                            "+": BLUE,
                        }
                    ).next_to(dp_squares[i].get_center(), DOWN * 4)
                    self.play(
                        AddTextLetterByLetter(max_text),
                    )
                    self.wait(2)

                dp[i] = max(dp[i if i == n else i + 1], profit)
                new_number = Text(str(dp[i]), font_size=32, font="JetBrains Mono", weight=BOLD, stroke_width=0,
                                  z_index=2).move_to(dp_squares[i].get_center())
                self.play(
                    AnimationGroup(
                        Succession(
                            RemoveTextLetterByLetter(dp_numbers[i]),
                            AddTextLetterByLetter(new_number),
                            lag_ratio=1.2,
                        ),
                        RemoveTextLetterByLetter(max_text),
                    )
                )

                remove_dp_number = dp_numbers[i]
                dp_numbers[i] = new_number
                self.remove(remove_dp_number)

                self.wait(2)

                self.play(
                    AnimationGroup(
                        Restore(dp_squares[i]),
                        Restore(end_times_squares[i - 1]),
                        Restore(profits_squares[i - 1]),
                    )
                )

            max_index = 0
            for i in range(1, n + 1):
                if dp[i] > dp[max_index]:
                    max_index = i

            self.play(
                AnimationGroup(
                    Indicate(
                        dp_squares[max_index], scale_factor=1.5, color=GREEN
                    ),
                    Indicate(
                        dp_numbers[max_index], scale_factor=1.5, color=GREEN
                    )
                )
            )

            self.play(
                dp_squares[max_index].animate.set_fill(GREEN, opacity=1),
            )
            self.wait(2)
            return dp[max_index]

        return iterative()
