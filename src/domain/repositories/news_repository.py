from abc import ABC, abstractmethod
from typing import List
from src.domain.entities.news import News

class NewsRepository(ABC):
    @abstractmethod
    def save_news(self, news: List[News]) -> None:
        pass

    @abstractmethod
    def save_image(self, url: str, filename: str) -> None:
        pass 