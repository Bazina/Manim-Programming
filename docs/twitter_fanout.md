First, we need to succinctly describe the current load on the system; only then can we
discuss growth questions (what happens if our load doubles?). Load can be described
with a few numbers which we call load parameters. The best choice of parameters
depends on the architecture of your system: it may be requests per second to a web
server, the ratio of reads to writes in a database, the number of simultaneously active
users in a chat room, the hit rate on a cache, or something else. Perhaps the average
case is what matters for you, or perhaps your bottleneck is dominated by a small
number of extreme cases.
To make this idea more concrete, let’s consider Twitter as an example, using data
published in November 2012 [16]. Two of Twitter’s main operations are:
Post tweet
A user can publish a new message to their followers (4.6k requests/sec on aver
age, over 12k requests/sec at peak).
Home timeline
A user can view tweets posted by the people they follow (300k requests/sec).
Simply handling 12,000 writes per second (the peak rate for posting tweets) would be
fairly easy. However, Twitter’s scaling challenge is not primarily due to tweet volume,
but due to fan-outii—each user follows many people, and each user is followed by
many people. There are broadly two ways of implementing these two operations:
1. Posting a tweet simply inserts the new tweet into a global collection of tweets.
When a user requests their home timeline, look up all the people they follow,
find all the tweets for each of those users, and merge them (sorted by time). In a
relational database like in Figure 1-2, you could write a query such as:
SELECT tweets.*, users.* FROM tweets
JOIN users   ON tweets.sender_id    
= users.id
JOIN follows ON follows.followee_id = users.id
WHERE follows.follower_id = current_user

2. Maintain a cache for each user’s home timeline—like a mailbox of tweets for
each recipient user (see Figure 1-3). When a user posts a tweet, look up all the
people who follow that user, and insert the new tweet into each of their home
timeline caches. The request to read the home timeline is then cheap, because its
result has been computed ahead of time.

The first version of Twitter used approach 1, but the systems struggled to keep up
with the load of home timeline queries, so the company switched to approach 2. This
works better because the average rate of published tweets is almost two orders of
magnitude lower than the rate of home timeline reads, and so in this case it’s prefera
ble to do more work at write time and less at read time.
However, the downside of approach 2 is that posting a tweet now requires a lot of
extra work. On average, a tweet is delivered to about 75 followers, so 4.6k tweets per
second become 345k writes per second to the home timeline caches. But this average
hides the fact that the number of followers per user varies wildly, and some users

have over 30 million followers. This means that a single tweet may result in over 30
million writes to home timelines! Doing this in a timely manner—Twitter tries to
deliver tweets to followers within five seconds—is a significant challenge.
In the example of Twitter, the distribution of followers per user (maybe weighted by
how often those users tweet) is a key load parameter for discussing scalability, since it
determines the fan-out load. Your application may have very different characteristics,
but you can apply similar principles to reasoning about its load.
The final twist of the Twitter anecdote: now that approach 2 is robustly implemented,
Twitter is moving to a hybrid of both approaches. Most users’ tweets continue to be
fanned out to home timelines at the time when they are posted, but a small number
of users with a very large number of followers (i.e., celebrities) are excepted from this
fan-out. Tweets from any celebrities that a user may follow are fetched separately and
merged with that user’s home timeline when it is read, like in approach 1. This hybrid
approach is able to deliver consistently good performance. We will revisit this exam
ple in Chapter 12 after we have covered some more technical ground.


Plan: Twitter Fan-Out Problem Manim Animation
Create a single-scene Manim animation in twitter_fanout.py that visually explains the Twitter fan-out problem from DDIA, using the same style conventions (JetBrains Mono font, #0D1117 background, AddTextLetterByLetter, Indicate, arrows, etc.) found in existing files like binary_search.py and greedy_and_dp.py. The file is currently empty and the reference content lives in twitter_fanout.md.
Steps
Scaffold the scene class and imports in twitter_fanout.py: Import manim, set config.background_color = "#0D1117", define a single class TwitterFanOut(Scene) with a construct method that delegates to five helper methods (scene_title, scene_problem_setup, scene_approach_pull, scene_approach_push, scene_hybrid), each ending with FadeOut(*self.mobjects) to clear the stage.
Scene 1 – Title: Create a Text("Twitter Fan-Out Problem", font="JetBrains Mono", weight=BOLD, font_size=42, color=BLUE) centered on screen, animate with AddTextLetterByLetter, hold, then fade out. Add a small subtitle Text("Designing Data-Intensive Applications", font_size=22, color=GREY) below it.
Scene 2 – Problem Setup: Build two VGroup rows (icon + label + stats) for "Post Tweet" (with Text showing "4.6k req/s avg, 12k peak", color ORANGE) and "Home Timeline" (Text showing "300k req/s", color GREEN). Use Arrow objects between a user icon (Circle + label) and each operation label. Animate rows with AddTextLetterByLetter and Indicate on the 300k number to emphasize the read-heavy skew. Use RoundedRectangle cards (matching the array-square pattern) to frame each operation.
Scene 3 – Approach 1 (Pull / Fan-out on Read):
Place a user icon (small Circle + "User A" label) on the left posting a tweet: animate an Arrow into a central RoundedRectangle labeled "tweets table".
On the right, show a follower icon requesting their timeline: animate an Arrow from follower to the tweets table, draw three RoundedRectangle tables ("tweets", "users", "follows") with DashedLine connectors to represent the JOIN.
Display the SQL query from the docs using a Code or multi-line Text block (font_size 16, JetBrains Mono, with t2c keyword coloring: SELECT/JOIN/WHERE/FROM in PURPLE, table names in ORANGE, columns in WHITE).
Flash a warning Text("300k reads/sec → heavy JOIN load!", color=RED) with Indicate.
Scene 4 – Approach 2 (Push / Fan-out on Write):
Reuse the user icon posting a tweet; show an Arrow fan-out to 3–4 follower mailbox RoundedRectangle objects arranged vertically on the right (labeled "Follower 1 cache", etc.) using AnimationGroup of GrowArrow with lag_ratio.
Show a stats badge: Text("75 followers avg → 4.6k × 75 = 345k writes/sec", color=ORANGE) animated with AddTextLetterByLetter.
Transform the user icon into a "Celebrity" icon (larger Circle, YELLOW stroke), animate fan-out arrows multiplying to fill the screen, then show Text("30M followers → 30M writes!", color=RED, font_size=28) with Indicate and a brief Flash.
Scene 5 – Hybrid Approach:
Split the screen into left ("Regular Users → Push") and right ("Celebrities → Pull") using a DashedLine divider.
Left side: compact replay of push fan-out (reuse small arrow group to caches).
Right side: show celebrity tweet staying in tweets table, fetched at read time.
Bottom center: Text("Merge at read time", color=GREEN, font_size=28) with converging Arrow objects from both sides into a single "Home Timeline" RoundedRectangle. Animate with GrowArrow and FadeIn.
End with a summary badge: Text("Best of both worlds ✓", color=GREEN).
Further Considerations
User/Celebrity icons: Use simple Circle + Text label combos (like pointer labels in binary_search.py), or would you prefer SVG icons for a Twitter-bird/person silhouette?
SQL rendering: Code mobject (supports syntax highlighting natively) vs. manually colored Text with t2c — Code is cleaner but requires a file or string; t2c matches existing codebase style. Recommend t2c for consistency.
Animation length: Each scene section will have ~5–8 seconds of content; total ~40–50 seconds. Should any section be expanded with more detailed sub-steps or kept compact?