from dataclasses import dataclass
from datetime import datetime

@dataclass
class News:
    title: str
    date: datetime
    description: str
    image_filename: str
    image_url: str
    search_phrase_count: int
    has_money: bool 