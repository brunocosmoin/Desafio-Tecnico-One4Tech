"""
###############################################################
# DESAFIO TÉCNICO - Extrator de Notícias                     #
#                                                           #
# Este script segue as etapas do desafio:                   #
# 1. Lê variáveis de configuração (.env):                   #
#    - Frase de pesquisa                                    #
#    - Categorias/seções de notícias                        #
#    - Número de meses para buscar notícias                 #
# 2. Realiza busca via API oficial                          #
# 3. Filtra por categorias e período                        #
# 4. Extrai título, data, descrição                         #
# 5. Salva no Excel: título, data, descrição, nome da imagem#
#    contagem da frase de pesquisa, flag de valor monetário #
# 6. Baixa a imagem da notícia                              #
# 7. Repete para todas as notícias do período               #
#                                                           #
# Requisitos: Docker, variáveis em .env                     #
#                                                           #
# Desenvolvido por: Bruno Cosmo                             #
###############################################################
"""

import os
from datetime import datetime
from dotenv import load_dotenv
from src.application.use_cases.fetch_news_use_case import FetchNewsUseCase
from src.infrastructure.clients.news_api_client import NewsAPIClient
from src.infrastructure.repositories.excel_news_repository import ExcelNewsRepository
from src.domain.services.news_analyzer import NewsAnalyzer
from src.infrastructure.logging.logger import logger

class NewsExtractorFramework:
    def __init__(self):
        self.logger = logger
        self.state = {
            'start_time': None,
            'end_time': None,
            'news_count': 0,
            'errors': []
        }

    def initialize(self):
        """Fase de inicializacao do framework."""
        try:
            self.logger.info("DESAFIO TECNICO - Extrator de Noticias")
            self.logger.info("Desenvolvido por: Bruno Cosmo\n")
            
            self.logger.info("Iniciando extracao de noticias...")
            self.state['start_time'] = datetime.now()
            
            # Carrega variaveis de ambiente
            load_dotenv()
            
            # Loga as configuracoes carregadas (exceto a API key por seguranca)
            self.logger.info("Configuracoes carregadas:")
            self.logger.info(f"API_URL: {os.getenv('API_URL')}")
            self.logger.info(f"IMAGE_BASE_URL: {os.getenv('IMAGE_BASE_URL')}")
            self.logger.info(f"EXCEL_PATH: {os.getenv('EXCEL_PATH')}")
            self.logger.info(f"IMAGES_DIR: {os.getenv('IMAGES_DIR')}")
            self.logger.info(f"LOG_DIR: {os.getenv('LOG_DIR')}")
            self.logger.info(f"SEARCH_PHRASE: {os.getenv('SEARCH_PHRASE')}")
            self.logger.info(f"CATEGORIES: {os.getenv('CATEGORIES')}")
            self.logger.info(f"MONTHS_TO_SEARCH: {os.getenv('MONTHS_TO_SEARCH')}")
            
            # Valida configuracoes necessarias
            required_vars = ['API_KEY', 'API_URL', 'SEARCH_PHRASE', 'CATEGORIES']
            missing_vars = [var for var in required_vars if not os.getenv(var)]
            
            if missing_vars:
                raise ValueError(f"Variaveis de ambiente ausentes: {', '.join(missing_vars)}")
            
            self.logger.info("Configuracoes carregadas com sucesso")
            
        except Exception as e:
            self.logger.error(f"Erro na inicializacao: {str(e)}")
            self.state['errors'].append(f"Inicializacao: {str(e)}")
            raise

    def process(self):
        """Fase de processamento principal."""
        try:
            # Configura dependencias
            search_phrase = os.getenv('SEARCH_PHRASE', '')
            categories = os.getenv('CATEGORIES', '').split(',') if os.getenv('CATEGORIES') else []
            months_to_search = int(os.getenv('MONTHS_TO_SEARCH', '2'))
            
            api_client = NewsAPIClient(
                search_phrase=search_phrase,
                categories=categories,
                months_to_search=months_to_search
            )
            excel_path = os.getenv('EXCEL_PATH', 'news_results.xlsx')
            images_dir = os.getenv('IMAGES_DIR', 'images')
            repository = ExcelNewsRepository(
                excel_path=excel_path,
                images_dir=images_dir
            )
            analyzer = NewsAnalyzer()
            
            # Cria e executa o caso de uso
            use_case = FetchNewsUseCase(repository)
            news_list = use_case.execute(
                search_phrase=search_phrase,
                categories=categories,
                months_to_search=months_to_search
            )
            
            # Se news_list for None, evita erro de len
            if news_list is not None:
                self.state['news_count'] = len(news_list)
                self.logger.info(f"Processamento concluido. {len(news_list)} noticias extraidas")
            else:
                self.state['news_count'] = 0
                self.logger.info("Processamento concluido. Nenhuma noticia extraida")
            
        except Exception as e:
            self.logger.error(f"Erro no processamento: {str(e)}")
            self.state['errors'].append(f"Processamento: {str(e)}")
            raise

    def handle_exception(self, exception):
        """Tratamento de excecoes."""
        try:
            self.logger.error(f"Excecao capturada: {str(exception)}")
            self.state['errors'].append(f"Excecao: {str(exception)}")
            
            # Aqui voce pode implementar logicas de recuperacao
            # Por exemplo, tentar novamente com configuracoes diferentes
            
        except Exception as e:
            self.logger.error(f"Erro no tratamento de excecao: {str(e)}")
            self.state['errors'].append(f"Tratamento de excecao: {str(e)}")

    def finalize(self):
        """Fase de finalizacao."""
        try:
            self.state['end_time'] = datetime.now()
            duration = self.state['end_time'] - self.state['start_time']
            
            # Gera relatorio de execucao
            self.logger.info("=== Relatorio de Execucao ===")
            self.logger.info(f"Duracao: {duration}")
            self.logger.info(f"Noticias processadas: {self.state['news_count']}")
            
            if self.state['errors']:
                self.logger.warning("=== Erros Encontrados ===")
                for error in self.state['errors']:
                    self.logger.warning(f"- {error}")
            
            self.logger.info("Extracao de noticias finalizada")
            
        except Exception as e:
            self.logger.error(f"Erro na finalizacao: {str(e)}")

    def run(self):
        """Método principal que executa o fluxo completo."""
        try:
            self.initialize()
            self.process()
        except Exception as e:
            self.handle_exception(e)
        finally:
            self.finalize()

if __name__ == "__main__":
    framework = NewsExtractorFramework()
    framework.run() 