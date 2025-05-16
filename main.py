"""
###############################################################
# DESAFIO TÉCNICO - Cliente de API do NYT                    #
#                                                           #
# Este script segue as etapas do desafio:                   #
# 1. Lê variáveis de configuração (.env):                   #
#    - Frase de pesquisa                                    #
#    - Categorias/seções de notícias                        #
#    - Número de meses para buscar notícias                 #
# 2. Realiza busca no NYT via API oficial                    #
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

def main():
    # 1. Carregar variáveis de ambiente (.env)
    load_dotenv()
    # Log de todas as variáveis para depuração
    print(f"[DEBUG MAIN] NYT_API_KEY: '{os.getenv('NYT_API_KEY')}'")
    print(f"[DEBUG MAIN] NYT_API_URL: '{os.getenv('NYT_API_URL')}'")
    print(f"[DEBUG MAIN] NYT_IMAGE_BASE_URL: '{os.getenv('NYT_IMAGE_BASE_URL')}'")
    print(f"[DEBUG MAIN] EXCEL_PATH: '{os.getenv('EXCEL_PATH')}'")
    print(f"[DEBUG MAIN] IMAGES_DIR: '{os.getenv('IMAGES_DIR')}'")
    print(f"[DEBUG MAIN] SEARCH_PHRASE: '{os.getenv('SEARCH_PHRASE')}'")
    print(f"[DEBUG MAIN] CATEGORIES: '{os.getenv('CATEGORIES')}'")
    print(f"[DEBUG MAIN] MONTHS_TO_SEARCH: '{os.getenv('MONTHS_TO_SEARCH')}'")    

    # 2. Configurar repositório para salvar Excel e imagens
    repository = ExcelNewsRepository(
        excel_path=os.getenv('EXCEL_PATH', 'nytimes_results.xlsx'),
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

if __name__ == "__main__":
    main() 