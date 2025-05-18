import unittest
import os
from datetime import datetime
from src.infrastructure.clients.news_api_client import NewsAPIClient

class TestNewsAPIClient(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Configura variáveis de ambiente para teste
        os.environ['API_KEY'] = 'test_key'
        os.environ['API_URL'] = 'https://api.newsapi.org/v2/everything'
        os.environ['IMAGE_BASE_URL'] = 'https://static.newsapi.org'

    def setUp(self):
        self.client = NewsAPIClient(
            search_phrase="test",
            categories=["technology"],
            months_to_search=1
        )

    def test_build_categories_filter(self):
        filter_str = self.client._build_categories_filter()
        expected = 'section.name:("technology")'
        self.assertEqual(filter_str, expected)

    def test_build_request_params(self):
        begin_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 31)
        
        params = self.client._build_request_params(begin_date, end_date)
        
        self.assertEqual(params['api-key'], 'test_key')
        self.assertEqual(params['begin_date'], '20240101')
        self.assertEqual(params['end_date'], '20240131')
        self.assertEqual(params['q'], 'test')
        expected_filter = 'section.name:("technology")'
        self.assertEqual(params['fq'], expected_filter)
        self.assertEqual(params['sort'], 'newest')

    def test_extract_article_data(self):
        doc = {
            'headline': {'main': 'Test Article'},
            'pub_date': '2024-01-01T12:00:00+0000',
            'abstract': 'Test Description',
            'multimedia': {
                'default': {'url': '/test-image.jpg'}
            }
        }
        
        article_data = self.client._extract_article_data(doc)
        
        self.assertEqual(article_data['title'], 'Test Article')
        self.assertEqual(article_data['description'], 'Test Description')
        self.assertEqual(article_data['img_url'], 'https://static.newsapi.org/test-image.jpg')

if __name__ == '__main__':
    unittest.main() 