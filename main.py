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
from dotenv import load_dotenv
from src.application.use_cases.fetch_news_use_case import FetchNewsUseCase
from src.infrastructure.repositories.excel_news_repository import ExcelNewsRepository
from src.infrastructure.logging.logger import logger

def main():
    # 1. Carregar variáveis de ambiente (.env)
    load_dotenv()

    logger.info("\nDESAFIO TECNICO - Extrator de Noticias")
    logger.info("Desenvolvido por: Bruno Cosmo\n")
    
    # Loga as configuracoes carregadas (exceto a API key por seguranca)
    logger.info("Configuracoes carregadas:")
    logger.info(f"API_URL: {os.getenv('API_URL')}")
    logger.info(f"IMAGE_BASE_URL: {os.getenv('IMAGE_BASE_URL')}")
    logger.info(f"EXCEL_PATH: {os.getenv('EXCEL_PATH')}")
    logger.info(f"IMAGES_DIR: {os.getenv('IMAGES_DIR')}")
    logger.info(f"LOG_DIR: {os.getenv('LOG_DIR')}")
    logger.info(f"SEARCH_PHRASE: {os.getenv('SEARCH_PHRASE')}")
    logger.info(f"CATEGORIES: {os.getenv('CATEGORIES')}")
    logger.info(f"MONTHS_TO_SEARCH: {os.getenv('MONTHS_TO_SEARCH')}")
    
    # 2. Configurar repositório para salvar Excel e imagens
    repository = ExcelNewsRepository(
        excel_path=os.getenv('EXCEL_PATH', 'news_results.xlsx'),
        images_dir=os.getenv('IMAGES_DIR', 'images')
    )

    # 3. Configurar caso de uso (orquestra busca e salvamento)
    use_case = FetchNewsUseCase(repository)

    # 4. Executar busca (busca, filtra, extrai, salva)
    use_case.execute(
        search_phrase=os.getenv('SEARCH_PHRASE', ''),
        categories=os.getenv('CATEGORIES', '').split(',') if os.getenv('CATEGORIES') else [],
        months_to_search=int(os.getenv('MONTHS_TO_SEARCH', '2'))
    )

if __name__ == '__main__':
    main() 