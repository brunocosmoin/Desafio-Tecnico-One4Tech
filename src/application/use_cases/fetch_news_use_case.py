from typing import List
from src.domain.entities.news import News
from src.domain.repositories.news_repository import NewsRepository
from src.infrastructure.clients.news_api_client import NewsAPIClient

class FetchNewsUseCase:
    def __init__(self, repository: NewsRepository):
        self.repository = repository

    def execute(self, search_phrase: str, categories: List[str], months_to_search: int) -> None:
        api_client = NewsAPIClient(search_phrase, categories, months_to_search)
        news_list = api_client.fetch_news()
        
        # Salvar notícias (inclui download assíncrono de imagens)
        self.repository.save_news(news_list) 