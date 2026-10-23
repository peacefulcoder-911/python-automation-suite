import random
from typing import Optional
from src.youtube.models import ShortScript, VideoNiche


class ScriptGenerator:
    """Generates viral, high-retention scripts for 30-50s YouTube Shorts."""

    PRESETS = {
        VideoNiche.SPACE: {
            "hooks": [
                "You won't believe what happens if you fall into a black hole.",
                "Space is terrifying, and here are 3 facts that prove it.",
                "There is a planet in our galaxy made entirely of diamonds.",
                "NASA discovered something on Mars that scientists cannot explain.",
            ],
            "bodies": [
                [
                    "First, in deep space, absolute silence reigns because sound waves cannot travel through a vacuum.",
                    "Second, a single day on Venus is longer than an entire year on Earth because it rotates backwards so slowly.",
                    "And third, if two pieces of the same type of metal touch in space, they fuse permanently in a process called cold welding.",
                ],
                [
                    "First, the largest known star, Stephenson 2-18, could engulf nearly 10 million suns inside its volume.",
                    "Second, neutron stars spin at an astonishing 700 rotations per second.",
                    "And third, astronomers discovered a giant interstellar cloud containing 400 trillion pints of alcohol.",
                ],
            ],
            "ctas": [
                "Subscribe to unlock daily cosmic mysteries!",
                "Which space fact shocked you the most? Drop a comment below and subscribe!",
                "Follow for more mind-bending science facts every day!",
            ],
        },
        VideoNiche.PSYCHOLOGY: {
            "hooks": [
                "Here are 3 psychological tricks that will change how you talk to anyone.",
                "This dark psychology trick makes people agree with you instantly.",
                "If someone is lying to you, look for these 3 subtle giveaways.",
            ],
            "bodies": [
                [
                    "First, when you want someone to reveal more information, simply stay completely quiet after they stop talking. Silence creates subconscious tension.",
                    "Second, nod your head gently while asking a question. Humans mirror body language, making them far more likely to say yes.",
                    "Third, if someone tries to interrupt you, do not shout. Keep speaking at the exact same calm pace until they yield.",
                ]
            ],
            "ctas": [
                "Save this video for later and subscribe for daily psychology hacks!",
                "Subscribe now to master human psychology before everyone else!",
            ],
        },
        VideoNiche.STOICISM: {
            "hooks": [
                "Marcus Aurelius followed 3 rules that made him mentally indestructible.",
                "Stop wasting your energy on things that do not matter. Listen closely.",
                "The ancient Stoics had a secret for dealing with toxic people.",
            ],
            "bodies": [
                [
                    "Rule one: You have power over your mind, not outside events. Realize this, and you will find instant strength.",
                    "Rule two: Never complain about what you cannot control. The obstacle in your path becomes the path itself.",
                    "Rule three: Remember that today could be your last day alive. Live with purpose, honesty, and focus.",
                ]
            ],
            "ctas": [
                "Stay disciplined. Subscribe to master Stoic philosophy every single day.",
                "Which Stoic rule hits you hardest? Leave a comment and subscribe.",
            ],
        },
        VideoNiche.TECH: {
            "hooks": [
                "AI is advancing so fast that these 3 breakthroughs seem like magic.",
                "These futuristic technologies are already here, but nobody is talking about them.",
                "In 5 years, smartphones will be completely obsolete. Here is why.",
            ],
            "bodies": [
                [
                    "First, humanoid robots are now learning complex manufacturing tasks purely through neural computer vision in days.",
                    "Second, quantum computers just solved a physics simulation that would take classical supercomputers 47 years.",
                    "Third, neural implants are allowing paralyzed patients to type messages directly using thought alone.",
                ]
            ],
            "ctas": [
                "Are you ready for this AI revolution? Subscribe to stay ahead of the curve!",
                "Hit that subscribe button for the latest tech breakthroughs daily!",
            ],
        },
    }

    @classmethod
    def generate(cls, topic: str, niche: VideoNiche = VideoNiche.SPACE) -> ShortScript:
        preset = cls.PRESETS.get(niche, cls.PRESETS[VideoNiche.SPACE])
        hook = random.choice(preset["hooks"])
        body = random.choice(preset["bodies"])
        cta = random.choice(preset["ctas"])

        if topic and topic.strip():
            hook = f"Did you know this about {topic.strip()}? {hook}"

        return ShortScript(
            niche=niche,
            topic=topic or "Cosmic Mysteries",
            hook=hook,
            facts_or_body=body,
            call_to_action=cta,
            estimated_duration_seconds=42,
        )