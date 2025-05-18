import os
from datetime import datetime, timedelta
from typing import List, Dict
import requests
import time
from functools import lru_cache
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from src.domain.entities.news import News
from src.domain.services.news_analyzer import NewsAnalyzer
from src.infrastructure.logging.logger import logger

class NewsAPIClient:
    def __init__(self, search_phrase: str, categories: List[str], months_to_search: int):
        self.search_phrase = search_phrase.strip() if search_phrase else ""
        self.categories = [cat.lower().strip() for cat in categories] if categories else []
        self.months_to_search = months_to_search
        self.api_key = os.getenv('API_KEY')
        if not self.api_key:
            raise ValueError("API_KEY não encontrada no arquivo .env")
        self.api_url = os.getenv('API_URL', "https://api.newsapi.org/v2/everything")
        self._cache = {}
        self._last_request_time = 0
        self._min_request_interval = 2  # Aumentado para 2 segundos entre requisições

    def _wait_for_rate_limit(self):
        """Espera o tempo necessário para respeitar o rate limit."""
        current_time = time.time()
        time_since_last_request = current_time - self._last_request_time
        if time_since_last_request < self._min_request_interval:
            time.sleep(self._min_request_interval - time_since_last_request)
        self._last_request_time = time.time()

    def _build_categories_filter(self) -> str:
        if not self.categories:
            return ""
        # Usa a sintaxe correta da API: section.name:("value1" OR "value2")
        categories = [f'"{cat}"' for cat in self.categories]
        return f'section.name:({" OR ".join(categories)})'

    def _build_request_params(self, begin_date: datetime, end_date: datetime) -> Dict:
        params = {
            'api-key': self.api_key,
            'begin_date': begin_date.strftime('%Y%m%d'),
            'end_date': end_date.strftime('%Y%m%d'),
            'sort': 'newest'
        }
        
        if self.search_phrase:
            params['q'] = self.search_phrase
            
        categories_filter = self._build_categories_filter()
        if categories_filter:
            params['fq'] = categories_filter
            
        return params

    def _extract_article_data(self, doc: Dict) -> Dict:
        headline = doc.get('headline', {})
        title = headline.get('main', '') if isinstance(headline, dict) else str(headline)
        pub_date = datetime.strptime(doc.get('pub_date', ''), "%Y-%m-%dT%H:%M:%S%z")
        description = doc.get('abstract', '')
        img_url = self._extract_image_url(doc)
        return {
            'title': title,
            'date': pub_date,
            'description': description,
            'img_url': img_url
        }

    def _extract_image_url(self, doc: Dict) -> str:
        multimedia = doc.get('multimedia', {})
        default = multimedia.get('default', {})
        url = default.get('url')
        if not url:
            return None
        image_base_url = os.getenv('IMAGE_BASE_URL', 'https://static.newsapi.org')
        if url.startswith('/'):
            url = f"{image_base_url}{url}"
        return url

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=2, min=10, max=60),
        retry=retry_if_exception_type((requests.exceptions.RequestException, requests.exceptions.HTTPError)),
        reraise=True
    )
    def _make_api_request(self, params: Dict) -> requests.Response:
        self._wait_for_rate_limit()
        safe_params = params.copy()
        safe_params.pop('api-key', None)
        logger.debug(f"Parametros da requisicao: {safe_params}")
        full_url = requests.Request('GET', self.api_url, params=params).prepare().url
        logger.debug(f"URL completa da requisicao: {full_url}")
        response = requests.get(self.api_url, params=params)
        logger.debug(f"Status da resposta: {response.status_code}")
        logger.debug(f"Headers da resposta: {dict(response.headers)}")
        if response.status_code == 429:
            logger.warning("Rate limit excedido. Aguardando antes de tentar novamente...")
            logger.debug(f"Resposta do rate limit: {response.text.encode('ascii', 'ignore').decode()}")
            time.sleep(20)
            raise requests.exceptions.HTTPError("Rate limit exceeded")
        if response.status_code != 200:
            logger.error(f"Erro na requisicao: {response.status_code} - {response.text.encode('ascii', 'ignore').decode()}")
            raise requests.exceptions.RequestException(f"Erro na requisicao: {response.status_code}")
        response_text = response.text[:500] + "..." if len(response.text) > 500 else response.text
        logger.debug(f"Corpo da resposta: {response_text.encode('ascii', 'ignore').decode()}")
        return response

    @lru_cache(maxsize=128)
    def _get_cached_articles(self, cache_key: str) -> List[Dict]:
        """Obtém artigos do cache ou faz nova requisição."""
        logger.debug(f"Cache miss para chave: {cache_key}")
        return self._get_search_results()

    def _get_search_results(self) -> List[Dict]:
        """Obtém resultados da busca para todo o período."""
        cache_key = "all_results"
        if cache_key in self._cache:
            logger.debug(f"Cache hit para chave: {cache_key}")
            return self._cache[cache_key]
        logger.debug(f"Cache miss para chave: {cache_key}")

        # Calcula o período total
        current_year = datetime.now().year
        begin_date = datetime(current_year, 1, 1)  # Primeiro dia do primeiro mês
        end_date = datetime(current_year, self.months_to_search + 1, 1) - timedelta(days=1)  # Último dia do último mês

        logger.info(f"Fazendo requisicao para a API - Periodo: {begin_date.strftime('%Y-%m-%d')} ate {end_date.strftime('%Y-%m-%d')}")
        logger.debug(f"Categorias: {', '.join(self.categories)}")
        
        params = self._build_request_params(begin_date, end_date)
        try:
            response = self._make_api_request(params)
            data = response.json()
        except Exception as e:
            logger.error(f"Erro ao obter resposta da API: {str(e)}")
            self._cache[cache_key] = []
            return []
        # Processamento seguro do JSON
        if not data or 'response' not in data or 'docs' not in data['response']:
            logger.info(f"Nenhum artigo encontrado para o periodo")
            self._cache[cache_key] = []
            return []
        if data['response']['docs'] is None and data['response'].get('metadata', {}).get('hits', 0) == 0:
            logger.info(f"Nenhum artigo encontrado para o periodo")
            self._cache[cache_key] = []
            return []
        if data['response']['docs'] is None:
            logger.error(f"Campo 'docs' e null mas hits nao e 0: {data['response']}")
            self._cache[cache_key] = []
            return []
        logger.info(f"Encontrados {len(data['response']['docs'])} artigos")
        articles = []
        for article in data['response']['docs']:
            try:
                article_data = self._extract_article_data(article)
                articles.append(article_data)
                logger.debug(f"Artigo processado com sucesso: {article_data['title'].encode('ascii', 'ignore').decode()}")
            except Exception as e:
                logger.error(f"Erro ao processar artigo: {str(e)}")
                logger.debug(f"Artigo com erro: {article}")
                continue
        logger.info(f"Total de artigos processados com sucesso: {len(articles)}")
        self._cache[cache_key] = articles
        return articles

    def fetch_news(self) -> List[News]:
        news_list = []
        # Faz uma única requisição para todo o período
        articles = self._get_search_results()
        
        for idx, article in enumerate(articles):
            search_count, has_money = NewsAnalyzer.analyze_news(
                article['title'],
                article['description'],
                self.search_phrase
            )
            img_url = article['img_url']
            img_filename = f"image_{idx}.jpg" if img_url else ""
            if img_url and not img_url.startswith('http'):
                image_base_url = os.getenv('IMAGE_BASE_URL', 'https://static.newsapi.org')
                img_url = f"{image_base_url}{img_url.lstrip('/')}"
                logger.debug(f"URL da imagem completa: {img_url}")
            if img_url:
                logger.info(f"Imagem a ser baixada: {img_url}")
            news = News(
                title=article['title'],
                date=article['date'],
                description=article['description'],
                image_filename=img_filename,
                image_url=img_url or '',
                search_phrase_count=search_count,
                has_money=has_money
            )
            news_list.append(news)
        return news_list 