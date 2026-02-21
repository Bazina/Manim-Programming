import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from manim import *

from libs.ddia_components import (
    FONT, DARK_BG, CARD_BG, SQL_T2C,
    make_label, make_card, make_user_icon,
)

config.background_color = "#0D1117"



class TwitterFanOut(Scene):
    def construct(self):
        self.scene_title()
        self.scene_problem_setup()
        self.scene_approach_pull()
        self.scene_approach_push()
        self.scene_hybrid()

    # ─── Scene 1: Title ───────────────────────────────────────────────
    def scene_title(self):
        title = make_label("Twitter Fan-Out Problem", font_size=42, color=BLUE)
        subtitle = make_label("Designing Data-Intensive Applications - Ch1", font_size=22, color=GREY_B)
        subtitle.next_to(title, DOWN, buff=0.4)

        self.play(AddTextLetterByLetter(title, time_per_char=0.05))
        self.play(FadeIn(subtitle, shift=UP * 0.2))
        self.wait(2)
        self.play(FadeOut(title), FadeOut(subtitle))

    # ─── Scene 2: Problem Setup ───────────────────────────────────────
    def scene_problem_setup(self):
        header = make_label("Twitter's Two Core Operations", font_size=32, color=ORANGE)
        header.to_edge(UP, buff=0.6)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))

        # Post tweet card
        post_card = make_card("Post Tweet", width=3, height=1, label_color=ORANGE, font_size=22)
        post_stats = make_label("4.6k req/s avg · 12k peak", font_size=16, color=GREY_A)
        post_stats.next_to(post_card, DOWN, buff=0.2)
        post_group = VGroup(post_card, post_stats).move_to(LEFT * 3 + DOWN * 0.3)

        # Home timeline card
        home_card = make_card("Home Timeline", width=3, height=1, label_color=GREEN, font_size=22)
        home_stats = make_label("300k req/s", font_size=16, color=GREY_A)
        home_stats.next_to(home_card, DOWN, buff=0.2)
        home_group = VGroup(home_card, home_stats).move_to(RIGHT * 3 + DOWN * 0.3)

        self.play(FadeIn(post_group, shift=UP * 0.3))
        self.wait(0.5)
        self.play(FadeIn(home_group, shift=UP * 0.3))
        self.wait(1)

        # Emphasize the read-heavy skew
        skew_text = make_label("Reads are ~65x more than writes!", font_size=24, color=RED)
        skew_text.next_to(VGroup(post_group, home_group), DOWN, buff=0.8)
        self.play(
            Indicate(home_stats, color=RED, scale_factor=1.4),
        )
        self.play(AddTextLetterByLetter(skew_text, time_per_char=0.03))
        self.wait(2)

        challenge = make_label(
            "The challenge is not tweet volume - it's fan-out.",
            font_size=22, color=YELLOW
        )
        challenge.next_to(skew_text, DOWN, buff=0.5)
        self.play(AddTextLetterByLetter(challenge, time_per_char=0.03))
        self.wait(3)

        self.play(FadeOut(*self.mobjects))

    # ─── Scene 3: Approach 1 — Fan-out on Read (Pull) ────────────────
    def scene_approach_pull(self):
        header = make_label("Approach 1: Fan-out on Read", font_size=30, color=BLUE)
        header.to_edge(UP, buff=0.5)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))

        # User posting
        user_a = make_user_icon("User A", color=BLUE_D, image_path="assets/person.png")
        user_a.move_to(LEFT * 5 + UP * 1.5)
        self.play(FadeIn(user_a, shift=RIGHT * 0.3))

        # Global tweets table
        tweets_table = make_card("tweets", width=2.4, height=0.7, fill_color="#2D333B", label_color=ORANGE,
                                 font_size=18)
        users_table = make_card("users", width=2.4, height=0.7, fill_color="#2D333B", label_color=PURPLE, font_size=18)
        follows_table = make_card("follows", width=2.4, height=0.7, fill_color="#2D333B", label_color=TEAL,
                                  font_size=18)
        tables = VGroup(tweets_table, users_table, follows_table).arrange(DOWN, buff=0.3).move_to(ORIGIN + UP * 0.5)

        # Show tables first, then arrow from user to tweets table
        self.play(FadeIn(tables, shift=DOWN * 0.2))

        write_arrow = Arrow(
            user_a.circle.get_right(), tweets_table.get_left(),
            buff=0.15, stroke_width=3, color=ORANGE, tip_length=0.15,
        )
        write_label = make_label("INSERT", font_size=14, color=ORANGE)
        write_label.next_to(write_arrow, UP, buff=0.1)

        self.play(GrowArrow(write_arrow), FadeIn(write_label))
        self.wait(1)

        # Follower requesting timeline
        follower = make_user_icon("Follower", color=GREEN_D, image_path="assets/person.png")
        follower.move_to(RIGHT * 5 + UP * 1.5)
        self.play(FadeIn(follower, shift=LEFT * 0.3))

        read_arrow = Arrow(
            follower.circle.get_left(), tweets_table.get_right(),
            buff=0.15, stroke_width=3, color=GREEN, tip_length=0.15,
        )
        read_label = make_label("SELECT + JOIN", font_size=14, color=GREEN)
        read_label.next_to(read_arrow, UP, buff=0.1)
        self.play(GrowArrow(read_arrow), FadeIn(read_label))
        self.wait(1)

        # Show JOIN connections
        join1 = DashedLine(tweets_table.get_bottom(), users_table.get_top(), color=GREY_B, stroke_width=1.5)
        join2 = DashedLine(users_table.get_bottom(), follows_table.get_top(), color=GREY_B, stroke_width=1.5)
        j1_label = make_label("JOIN", font_size=12, color=GREY_A)
        j1_label.next_to(join1, RIGHT, buff=0.1)
        j2_label = make_label("JOIN", font_size=12, color=GREY_A)
        j2_label.next_to(join2, RIGHT, buff=0.1)
        self.play(Create(join1), Create(join2), FadeIn(j1_label), FadeIn(j2_label))
        self.wait(1)

        # SQL query
        sql_text = (
            "SELECT tweets.*, users.*\n"
            "FROM tweets\n"
            "JOIN users ON tweets.sender_id = users.id\n"
            "JOIN follows ON follows.followee_id = users.id\n"
            "WHERE follows.follower_id = current_user"
        )
        sql_label = Text(
            sql_text,
            font=FONT,
            font_size=14,
            color=GREY_A,
            weight=BOLD,
            stroke_width=0,
            t2c=SQL_T2C,
        )
        sql_box = SurroundingRectangle(
            sql_label, color=GREY_B, buff=0.2, corner_radius=0.1,
            fill_color="#161B22", fill_opacity=0.9,
        )
        sql_vg = VGroup(sql_box, sql_label).to_edge(DOWN, buff=0.4)
        self.play(FadeIn(sql_vg, shift=UP * 0.3))
        self.wait(2)

        # Warning
        warning = make_label("300k reads/sec = heavy JOIN load!", font_size=22, color=RED)
        warning.next_to(sql_vg, UP, buff=0.35)
        self.play(AddTextLetterByLetter(warning, time_per_char=0.03))
        self.play(Indicate(warning, color=RED, scale_factor=1.2))
        self.wait(3)

        self.play(FadeOut(*self.mobjects))

    # ─── Scene 4: Approach 2 — Fan-out on Write (Push) ───────────────
    def scene_approach_push(self):
        header = make_label("Approach 2: Fan-out on Write", font_size=30, color=PURPLE)
        header.to_edge(UP, buff=0.5)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))

        # User posts a tweet
        user_a = make_user_icon("User A", color=BLUE_D, image_path="assets/person.png")
        user_a.move_to(LEFT * 4.5 + UP * 1)

        tweet_box = make_card("New Tweet", width=2, height=0.6, fill_color="#2D333B", label_color=ORANGE, font_size=16)
        tweet_box.next_to(user_a, RIGHT, buff=0.5)

        self.play(FadeIn(user_a, shift=RIGHT * 0.2))
        self.play(FadeIn(tweet_box, shift=RIGHT * 0.3))
        self.wait(0.5)

        # Follower caches
        num_followers = 5
        follower_names = [f"Follower {i + 1}" for i in range(num_followers)]
        follower_caches = VGroup()
        for name in follower_names:
            cache = make_card(
                f"{name} Cache", width=2.8, height=0.55,
                fill_color="#1C2128", label_color=GREEN, font_size=14,
            )
            follower_caches.add(cache)
        follower_caches.arrange(DOWN, buff=0.15).move_to(RIGHT * 3.5 + UP * 0.3)

        self.play(FadeIn(follower_caches, shift=LEFT * 0.3))
        self.wait(0.5)

        # Fan-out arrows
        arrows = VGroup()
        for cache in follower_caches:
            arrow = Arrow(
                tweet_box.get_right(), cache.get_left(),
                buff=0.1, stroke_width=2, color=YELLOW, tip_length=0.12,
            )
            arrows.add(arrow)

        self.play(
            AnimationGroup(*[GrowArrow(a) for a in arrows], lag_ratio=0),
        )
        self.wait(1)

        # Stats
        stats1 = make_label("Avg: 75 followers per user", font_size=18, color=GREY_A)
        stats2 = make_label("4.6k tweets/s x 75 = 345k writes/s", font_size=18, color=ORANGE)
        stats_group = VGroup(stats1, stats2).arrange(DOWN, buff=0.2).to_edge(DOWN, buff=1.2)
        self.play(AddTextLetterByLetter(stats1, time_per_char=0.03))
        self.play(AddTextLetterByLetter(stats2, time_per_char=0.03))
        self.wait(2)

        # Transition to celebrity problem
        self.play(FadeOut(arrows), FadeOut(follower_caches), FadeOut(tweet_box), FadeOut(stats_group))

        # Celebrity scenario — morph circle, swap text char by char
        celeb = make_user_icon("Taylor Swift", color=YELLOW, font_size=16, image_path="assets/taylor.png")
        celeb.move_to(LEFT * 4.5 + UP * 0.5)
        celeb_tweet = make_card("Tweet", width=1.8, height=0.6, fill_color="#2D333B", label_color=YELLOW, font_size=16)
        celeb_tweet.next_to(celeb, RIGHT, buff=0.5)

        # Morph: cross-fade images + remove old label letter by letter
        self.play(
            FadeOut(user_a[0]),                       # fade out person image
            FadeIn(celeb[0]),                          # fade in taylor image
            RemoveTextLetterByLetter(user_a[1], time_per_char=0.06),
        )
        # Add celebrity label letter by letter
        celeb_label = celeb[1]
        celeb_label.next_to(celeb[0], DOWN, buff=0.15)
        self.play(AddTextLetterByLetter(celeb_label, time_per_char=0.06))
        # Keep references consistent for the rest of the scene
        self.remove(user_a)
        self.add(celeb)

        self.play(FadeIn(celeb_tweet, shift=RIGHT * 0.3))
        self.wait(0.5)

        # Many follower caches (compressed visualization)
        many_caches = VGroup()
        rows, cols = 5, 4
        for r in range(rows):
            for c in range(cols):
                mini = RoundedRectangle(
                    corner_radius=0.05, width=0.7, height=0.35,
                    fill_color="#1C2128", fill_opacity=0.8,
                    stroke_color=GREEN, stroke_width=1,
                )
                many_caches.add(mini)
        many_caches.arrange_in_grid(rows=rows, cols=cols, buff=0.1).move_to(RIGHT * 3 + UP * 0.5)

        dots_label = make_label("... x 79 Million", font_size=16, color=RED)
        dots_label.next_to(many_caches, DOWN, buff=0.2)

        self.play(FadeIn(many_caches, shift=LEFT * 0.2), FadeIn(dots_label))
        self.wait(0.5)

        # Fan-out arrows to many caches
        celeb_arrows = VGroup()
        for cache in many_caches:
            arrow = Arrow(
                celeb_tweet.get_right(), cache.get_left(),
                buff=0.05, stroke_width=1.2, color=RED_C, tip_length=0.08,
            )
            celeb_arrows.add(arrow)

        self.play(
            AnimationGroup(*[GrowArrow(a) for a in celeb_arrows], lag_ratio=0),
        )
        self.wait(1)

        # Warning text
        celeb_warning = make_label("1 tweet = 79M+ writes to caches!", font_size=24, color=RED)
        celeb_warning.to_edge(DOWN, buff=0.7)
        self.play(AddTextLetterByLetter(celeb_warning, time_per_char=0.03))
        self.play(Indicate(celeb_warning, color=RED, scale_factor=1.2))

        delivery = make_label("Twitter aims to deliver within 5 seconds!", font_size=18, color=YELLOW)
        delivery.next_to(celeb_warning, DOWN, buff=0.3)
        self.play(AddTextLetterByLetter(delivery, time_per_char=0.03))
        self.wait(3)

        self.play(FadeOut(*self.mobjects))

    # ─── Scene 5: Hybrid Approach ─────────────────────────────────────
    def scene_hybrid(self):
        header = make_label("Hybrid Approach", font_size=32, color=GREEN)
        header.to_edge(UP, buff=0.5)
        self.play(AddTextLetterByLetter(header, time_per_char=0.04))

        # Divider
        divider = DashedLine(UP * 2.5, DOWN * 2.5, color=GREY, stroke_width=1.5)
        self.play(Create(divider))

        # ── Left side: Regular Users → Push ──
        left_title = make_label("Regular Users", font_size=20, color=BLUE)
        left_title.move_to(LEFT * 3.5 + UP * 2)
        left_sub = make_label("Fan-out on Write (Push)", font_size=14, color=GREY_A)
        left_sub.next_to(left_title, DOWN, buff=0.15)
        self.play(FadeIn(left_title), FadeIn(left_sub))

        reg_user = make_user_icon("User", color=BLUE_D, radius=0.25, font_size=12, image_path="assets/person.png")
        reg_user.move_to(LEFT * 5 + UP * 0.2)

        reg_caches = VGroup()
        for i in range(3):
            c = make_card(
                f"Cache {i + 1}", width=1.8, height=0.4,
                fill_color="#1C2128", label_color=GREEN, font_size=11,
            )
            reg_caches.add(c)
        reg_caches.arrange(DOWN, buff=0.12).move_to(LEFT * 2.5 + UP * 0.2)

        self.play(FadeIn(reg_user), FadeIn(reg_caches))
        reg_arrows = VGroup()
        for c in reg_caches:
            a = Arrow(
                reg_user.circle.get_right(), c.get_left(),
                buff=0.1, stroke_width=2, color=YELLOW, tip_length=0.12,
            )
            reg_arrows.add(a)
        self.play(AnimationGroup(*[GrowArrow(a) for a in reg_arrows], lag_ratio=0))
        self.wait(0.5)

        # ── Right side: Taylor Swift → Pull ──
        right_title = make_label("Taylor Swift", font_size=20, color=YELLOW)
        right_title.move_to(RIGHT * 3.5 + UP * 2)
        right_sub = make_label("Fan-out on Read (Pull)", font_size=14, color=GREY_A)
        right_sub.next_to(right_title, DOWN, buff=0.15)
        self.play(FadeIn(right_title), FadeIn(right_sub))

        celeb = make_user_icon("Taylor Swift", color=YELLOW, radius=0.25, font_size=10, image_path="assets/taylor.png")
        celeb.move_to(RIGHT * 1.3 + UP * 0.3)

        tweets_db = make_card(
            "tweets DB", width=1.8, height=0.5,
            fill_color="#2D333B", label_color=ORANGE, font_size=12,
        )
        tweets_db.next_to(celeb, RIGHT, buff=1.0)

        self.play(FadeIn(celeb), FadeIn(tweets_db))
        celeb_arrow = Arrow(
            celeb.circle.get_right(), tweets_db.get_left(),
            buff=0.1, stroke_width=2, color=ORANGE, tip_length=0.12,
        )
        self.play(GrowArrow(celeb_arrow))
        store_label = make_label("Store only", font_size=11, color=GREY_A)
        store_label.next_to(celeb_arrow, UP, buff=0.08)
        self.play(FadeIn(store_label))
        self.wait(1)

        # ── Bottom: Merge at read time ──
        timeline = make_card(
            "Home Timeline", width=3, height=0.8,
            fill_color="#0D4429", label_color=GREEN, font_size=18,
        )
        timeline.move_to(DOWN * 2.5)

        merge_label = make_label("Merge at read time", font_size=20, color=GREEN)
        merge_label.next_to(timeline, UP, buff=0.3)

        # Arrow from caches
        merge_arrow_left = Arrow(
            reg_caches.get_bottom(), timeline.get_left(),
            buff=0.1, stroke_width=2, color=GREEN, tip_length=0.12,
        )
        # Arrow from tweets DB
        merge_arrow_right = Arrow(
            tweets_db.get_bottom(), timeline.get_right(),
            buff=0.1, stroke_width=2, color=GREEN, tip_length=0.12,
        )

        self.play(FadeIn(timeline, shift=UP * 0.3), FadeIn(merge_label))
        self.play(GrowArrow(merge_arrow_left), GrowArrow(merge_arrow_right))
        self.wait(1)

        # Summary
        summary = make_label("Best of both worlds", font_size=26, color=GREEN)
        summary.to_edge(DOWN, buff=0.4)
        self.play(AddTextLetterByLetter(summary, time_per_char=0.04))
        self.play(Indicate(summary, color=GREEN, scale_factor=1.2))
        self.wait(3)

        self.play(FadeOut(*self.mobjects))
