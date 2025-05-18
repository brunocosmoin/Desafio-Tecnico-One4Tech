import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

def setup_logger():
    # Cria o diretório de logs se não existir
    log_dir = os.getenv('LOG_DIR', 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Configura o logger
    logger = logging.getLogger('news_extractor')
    logger.setLevel(logging.DEBUG)
    
    # Formato do log
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Handler para arquivo
    log_file = os.path.join(log_dir, f'news_extractor_{datetime.now().strftime("%Y%m%d")}.log')
    file_handler = RotatingFileHandler(log_file, maxBytes=10485760, backupCount=5)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Handler para console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Adiciona os handlers ao logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Cria o logger global
logger = setup_logger() 