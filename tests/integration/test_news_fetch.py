import unittest
import os
from datetime import datetime
from src.application.use_cases.fetch_news_use_case import FetchNewsUseCase
from src.infrastructure.repositories.excel_news_repository import ExcelNewsRepository
from src.domain.entities.news import News

class TestNewsFetch(unittest.TestCase):
    def setUp(self):
        """Configuração inicial para os testes"""
        # Configurar arquivo de teste
        self.test_excel_path = 'test_results.xlsx'
        
        # Limpar arquivo anterior se existir
        if os.path.exists(self.test_excel_path):
            os.remove(self.test_excel_path)
        
        # Configurar repositório de teste
        self.repository = ExcelNewsRepository(
            excel_path=self.test_excel_path,
            images_dir='images'  # Usa o diretório padrão
        )
        
        # Configurar caso de uso
        self.use_case = FetchNewsUseCase(self.repository)

    def tearDown(self):
        """Limpeza após os testes"""
        if os.path.exists(self.test_excel_path):
            os.remove(self.test_excel_path)

    def test_fetch_news_empty_categories(self):
        """Testa busca de notícias sem categorias"""
        # Executar busca
        self.use_case.execute(
            search_phrase="test",
            categories=[],
            months_to_search=1
        )
        
        # Verificar se o Excel foi criado
        self.assertTrue(os.path.exists(self.test_excel_path))

    def test_fetch_news_success(self):
        """Testa busca de notícias com sucesso"""
        # Executar busca
        self.use_case.execute(
            search_phrase="test",
            categories=["business", "technology"],
            months_to_search=1
        )
        
        # Verificar se o Excel foi criado
        self.assertTrue(os.path.exists(self.test_excel_path))

if __name__ == '__main__':
    unittest.main() 