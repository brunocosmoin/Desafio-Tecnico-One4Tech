import unittest
from src.domain.services.news_analyzer import NewsAnalyzer

class TestNewsAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = NewsAnalyzer()

    def test_analyze_news_with_money(self):
        """Testa análise de notícia com valores monetários nos formatos especificados"""
        title = "Empresa anuncia investimento de $ 11,1 milhões"
        description = "A empresa planeja gastar US$ 111.111,11 em infraestrutura"
        
        search_count, has_money = self.analyzer.analyze_news(title, description, "investimento")
        
        self.assertEqual(search_count, 1)
        self.assertTrue(has_money)

    def test_analyze_news_without_money(self):
        """Testa análise de notícia sem valores monetários"""
        title = "Nova tecnologia revoluciona mercado"
        description = "Empresa lança produto inovador"
        
        search_count, has_money = self.analyzer.analyze_news(title, description, "tecnologia")
        
        self.assertEqual(search_count, 1)
        self.assertFalse(has_money)

    def test_analyze_news_empty_inputs(self):
        """Testa análise com entradas vazias"""
        search_count, has_money = self.analyzer.analyze_news("", "", "test")
        
        self.assertEqual(search_count, 0)
        self.assertFalse(has_money)

if __name__ == '__main__':
    unittest.main() 