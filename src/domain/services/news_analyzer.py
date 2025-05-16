import re
from typing import Tuple
import string
import unicodedata
from src.domain.entities.news import News

class NewsAnalyzer:
    @staticmethod
    def remove_accents(text: str) -> str:
        return ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')

    @staticmethod
    def analyze_news(title: str, description: str, search_phrase: str) -> Tuple[int, bool]:
        # Loga os textos originais para depuração
        NewsAnalyzer._log_original_texts(title, description, search_phrase)
        # Cria um tradutor para remover pontuação
        translator = str.maketrans('', '', string.punctuation)
        # Limpa e normaliza os textos (minúsculas, sem acentos, sem pontuação)
        title_clean = NewsAnalyzer._clean_text(title, translator)
        description_clean = NewsAnalyzer._clean_text(description, translator)
        phrase_clean = NewsAnalyzer._clean_text(search_phrase, translator)
        # Loga os textos processados para depuração
        NewsAnalyzer._log_processed_texts(title_clean, description_clean, phrase_clean)
        # Conta quantas vezes a frase de busca aparece no título e descrição
        search_count = NewsAnalyzer._count_phrase(title_clean, description_clean, phrase_clean)
        print(f"[DEBUG] Contagem total para este artigo: {search_count}")
        # Verifica se há menção a valores monetários usando regex
        has_money = NewsAnalyzer._has_money(title, description)
        return search_count, has_money

    @staticmethod
    def _log_original_texts(title, description, search_phrase):
        print(f"[DEBUG] Titulo original: {NewsAnalyzer.remove_accents(title)}")
        print(f"[DEBUG] Frase de busca: {search_phrase}")

    @staticmethod
    def _clean_text(text, translator):
        return NewsAnalyzer.remove_accents(text.lower()).translate(translator)

    @staticmethod
    def _log_processed_texts(title_clean, description_clean, phrase_clean):
        print(f"[DEBUG] Titulo processado: {title_clean}")
        print(f"[DEBUG] Descricao processada: {description_clean}")
        print(f"[DEBUG] Frase de pesquisa processada: {phrase_clean}")

    @staticmethod
    def _count_phrase(title_clean, description_clean, phrase_clean):
        count_title = title_clean.count(phrase_clean)
        count_desc = description_clean.count(phrase_clean)
        print(f"[DEBUG] Frase '{phrase_clean}' - no titulo: {count_title}, na descricao: {count_desc}")
        return count_title + count_desc

    @staticmethod
    def _has_money(title, description):
        # Padrões para identificar valores monetários em diferentes formatos (ex: $ 10, US$ 100, 20 dólares)
        money_patterns = [
            r'\$\s*\d+[.,]\d+',  # $ 11,1
            r'US\$\s*\d+[.,]\d+',  # US$ 111.111,11
            r'\d+\s*dólares?',  # 11 dólares
            r'\d+\s*dollars?'  # 11 dollars
        ]
        return any(
            re.search(pattern, title, re.IGNORECASE) or 
            re.search(pattern, description, re.IGNORECASE)
            for pattern in money_patterns
        ) 