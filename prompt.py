from dataclasses import dataclass


@dataclass
class ClarifyingQuestions:
    question_one: str = (
        "What is your current background with this topic (e.g., absolute beginner, some basics, intermediate)?"
    )
    question_two: str = (
        "How many hours per week can you realistically commit and what learning style do you prefer (reading, videos, hands-on)?"
    )


def build_playlist_query(topic: str) -> str:
    """Build a search query for finding relevant YouTube playlists."""
    return f"{topic} beginner to advanced full course playlist"


