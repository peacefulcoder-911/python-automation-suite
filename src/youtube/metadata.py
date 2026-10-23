from typing import List
from src.youtube.models import ShortScript, YouTubeMetadata, VideoNiche


class MetadataOptimizer:
    """Generates high-CTR titles, optimized descriptions, and search tags for YouTube Shorts."""

    NICHE_TAGS = {
        VideoNiche.SPACE: ["space", "universe", "science", "nasa", "astronomy", "cosmic", "blackhole"],
        VideoNiche.PSYCHOLOGY: ["psychology", "mindhacks", "humanbehavior", "facts", "darkpsychology"],
        VideoNiche.STOICISM: ["stoicism", "philosophy", "motivation", "discipline", "marcusaurelius", "mindset"],
        VideoNiche.TECH: ["technology", "ai", "artificialintelligence", "futurism", "breakthrough", "techfacts"],
    }

    @classmethod
    def optimize(cls, script: ShortScript) -> YouTubeMetadata:
        clean_topic = script.topic.title()
        title = f"{clean_topic} Will Blow Your Mind! 🤯 #Shorts"
        if len(title) > 95:
            title = f"{clean_topic[:60]}... 🤯 #Shorts"

        niche_tags = cls.NICHE_TAGS.get(script.niche, ["facts", "viral", "interestingfacts"])
        all_tags = list(set(["shorts", "viral", "knowledge", "learn"] + niche_tags + [script.topic.lower().replace(" ", "")]))

        hashtags_str = " ".join([f"#{t}" for t in all_tags[:6]])

        description = f"""{script.hook}

Did you know these mind-blowing facts about {script.topic}?
Watch until the end for the most insane revelation!

👉 Subscribe for daily mind-expanding Shorts!
{hashtags_str}

---
#Shorts #Viral #Trending #Education #{script.niche.value.capitalize()}
"""

        return YouTubeMetadata(
            title=title,
            description=description.strip(),
            tags=all_tags,
            category_id="27",
            privacy_status="private",
        )