import os
from datetime import datetime, timedelta
from typing import List, Dict
import requests
from src.domain.entities.news import News
from src.domain.services.news_analyzer import NewsAnalyzer
import unicodedata

def remove_accents(text: str) -> str:
    return ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')

class NYTimesAPIClient:
    def __init__(self, search_phrase: str, categories: List[str], months_to_search: int):
        self.search_phrase = search_phrase.strip() if search_phrase else ""
        self.categories = [cat.lower().strip() for cat in categories] if categories else []
        self.months_to_search = months_to_search
        self.api_key = os.getenv('NYT_API_KEY')
        if not self.api_key:
            raise ValueError("NYT_API_KEY não encontrada no arquivo .env")
        self.api_url = os.getenv('NYT_API_URL', "https://api.nytimes.com/svc/search/v2/articlesearch.json")

    def _build_categories_filter(self) -> str:
        # Se não houver categorias, retorna string vazia
        if not self.categories:
            return ""
        # Monta o filtro de categorias usando a sintaxe Lucene da API do NYT
        categories = [f'"{cat}"' for cat in self.categories]
        return f'section.name:({" OR ".join(categories)})'

    def _build_request_params(self, begin_date: datetime, end_date: datetime) -> Dict:
        # Monta os parâmetros da requisição para a API do NYT
        params = {
            'api-key': self.api_key,
            'begin_date': begin_date.strftime('%Y%m%d'),
            'end_date': end_date.strftime('%Y%m%d'),
            'sort': 'newest'
        }
        
        # Adiciona frase de busca apenas se não estiver vazia
        if self.search_phrase:
            params['q'] = self.search_phrase
            
        # Adiciona filtro de categorias apenas se não estiver vazio
        categories_filter = self._build_categories_filter()
        if categories_filter:
            params['fq'] = categories_filter
            
        return params

    def _log_api_request(self, response: requests.Response):
        with open('nyt_api_debug.log', 'w', encoding='utf-8') as log_file:
            log_file.write('REQUEST URL:\n')
            log_file.write(f'{response.url}\n')
            log_file.write('\nREQUEST HEADERS:\n')
            log_file.write(f'{response.headers}\n')
            log_file.write('\nRESPONSE STATUS:\n')
            log_file.write(f'{response.status_code}\n')
            log_file.write('\nRESPONSE BODY:\n')
            log_file.write(response.text)

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
        # Extrai a URL da imagem principal do artigo, se existir
        multimedia = doc.get('multimedia', {})
        default = multimedia.get('default', {})
        url = default.get('url')
        if not url:
            return None
        # Se a URL for relativa, monta a URL completa usando a variável de ambiente
        image_base_url = os.getenv('NYT_IMAGE_BASE_URL', 'https://static01.nyt.com')
        if url.startswith('/'):
            url = f"{image_base_url}{url}"
        return url

    def _get_search_results(self) -> List[Dict]:
        print(f"Fazendo requisicao para a API do NYT")
        
        end_date = datetime.now()
        begin_date = end_date - timedelta(days=self.months_to_search * 30)
        
        params = self._build_request_params(begin_date, end_date)
        print(f"[DEBUG] Filtro de categorias: {params['fq']}")
        print(f"[DEBUG] URL completa: {self.api_url}?{requests.compat.urlencode(params)}")
        
        headers = {
            'User-Agent': os.getenv('USER_AGENT', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        }
        response = requests.get(self.api_url, params=params, headers=headers)
        print(f"Status da resposta: {response.status_code}")
        
        self._log_api_request(response)
        
        if response.status_code != 200:
            print(f"Erro na requisicao: {response.text}")
            return []
            
        data = response.json()
        if 'response' not in data or 'docs' not in data['response']:
            print("Formato de resposta invalido")
            return []
            
        print(f"Encontrados {len(data['response']['docs'])} artigos")
        
        articles = []
        for doc in data['response']['docs']:
            try:
                article_data = self._extract_article_data(doc)
                articles.append(article_data)
                print(f"[DEBUG] Artigo processado com sucesso: {remove_accents(article_data['title'])}")
            except Exception as e:
                print(f"[DEBUG] Erro ao processar artigo: {str(e)}")
                continue
                
        print(f"Total de artigos processados com sucesso: {len(articles)}")
        return articles

    def fetch_news(self) -> List[News]:
        articles = self._get_search_results()
        news_list = []
        for idx, article in enumerate(articles):
            search_count, has_money = NewsAnalyzer.analyze_news(
                article['title'],
                article['description'],
                self.search_phrase
            )
            img_url = article['img_url']
            img_filename = f"image_{idx}.jpg" if img_url else ""
            
            if img_url and not img_url.startswith('http'):
                image_base_url = os.getenv('NYT_IMAGE_BASE_URL', 'https://static01.nyt.com')
                img_url = f"{image_base_url}{img_url.lstrip('/')}"
                print(f"[DEBUG] URL da imagem completa: {img_url}")
                
            if img_url:
                print(f"[LOG] Imagem a ser baixada: {img_url}")
                
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