import re
from typing import Tuple
import string
import unicodedata
from src.domain.entities.news import News
from src.infrastructure.logging.logger import logger

class NewsAnalyzer:
    @staticmethod
    def remove_accents(text: str) -> str:
        return ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')

    @staticmethod
    def analyze_news(title: str, description: str, search_phrase: str) -> Tuple[int, bool]:
        # Loga os textos originais para depuracao
        NewsAnalyzer._log_original_texts(title, description, search_phrase)
        # Cria um tradutor para remover pontuacao
        translator = str.maketrans('', '', string.punctuation)
        # Limpa e normaliza os textos (minusculas, sem acentos, sem pontuacao)
        title_clean = NewsAnalyzer._clean_text(title, translator)
        description_clean = NewsAnalyzer._clean_text(description, translator)
        phrase_clean = NewsAnalyzer._clean_text(search_phrase, translator)
        # Loga os textos processados para depuracao
        NewsAnalyzer._log_processed_texts(title_clean, description_clean, phrase_clean)
        # Conta quantas vezes a frase de busca aparece no titulo e descricao
        search_count = NewsAnalyzer._count_phrase(title_clean, description_clean, phrase_clean)
        logger.debug(f"Contagem total para este artigo: {search_count}")
        # Verifica se ha mencao a valores monetarios usando regex
        has_money = NewsAnalyzer._has_money(title, description)
        return search_count, has_money

    @staticmethod
    def _log_original_texts(title, description, search_phrase):
        logger.debug(f"Titulo original: {NewsAnalyzer.remove_accents(title)}")
        logger.debug(f"Frase de busca: {search_phrase}")

    @staticmethod
    def _clean_text(text, translator):
        return NewsAnalyzer.remove_accents(text.lower()).translate(translator)

    @staticmethod
    def _log_processed_texts(title_clean, description_clean, phrase_clean):
        logger.debug(f"Titulo processado: {title_clean}")
        logger.debug(f"Descricao processada: {description_clean}")
        logger.debug(f"Frase de pesquisa processada: {phrase_clean}")

    @staticmethod
    def _count_phrase(title_clean, description_clean, phrase_clean):
        count_title = title_clean.count(phrase_clean)
        count_desc = description_clean.count(phrase_clean)
        logger.debug(f"Frase '{phrase_clean}' - no titulo: {count_title}, na descricao: {count_desc}")
        return count_title + count_desc

    @staticmethod
    def _has_money(title, description):
        # Padroes para identificar valores monetarios conforme especificado no desafio
        money_patterns = [
            r'\$\s*\d+[.,]\d+',  # $ 11,1
            r'US\$\s*\d+[.,]\d+',  # US$ 111.111,11
            r'\d+\s*dolares?',  # 11 dolares
            r'\d+\s*dollars?'  # 11 dollars
        ]
        return any(
            re.search(pattern, title, re.IGNORECASE) or 
            re.search(pattern, description, re.IGNORECASE)
            for pattern in money_patterns
        ) 