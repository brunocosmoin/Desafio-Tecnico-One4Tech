from typing import List
from src.domain.entities.news import News
from src.domain.repositories.news_repository import NewsRepository
from src.infrastructure.clients.nytimes_api_client import NYTimesAPIClient

class FetchNewsUseCase:
    def __init__(self, repository: NewsRepository):
        self.repository = repository

    def execute(self, search_phrase: str, categories: List[str], months_to_search: int) -> None:
        api_client = NYTimesAPIClient(search_phrase, categories, months_to_search)
        news_list = api_client.fetch_news()
        
        # Salvar imagens
        for news in news_list:
            if news.image_filename and news.image_url:
                self.repository.save_image(news.image_url, news.image_filename)
        
        # Salvar notícias
        self.repository.save_news(news_list) 