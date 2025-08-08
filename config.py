#!/usr/bin/env python3
"""
Configurações do sistema de scraping de licitações
"""

import os
from datetime import datetime

class Config:
    """Classe de configurações do sistema"""
    
    # Configurações do banco de dados
    DATABASE_PATH = "database/licitacoes.db"
    
    # Configurações de multithreading
    MAX_WORKERS = 3  # Número máximo de threads paralelas
    THREAD_TIMEOUT = 300  # Timeout em segundos para cada thread
    RETRY_ATTEMPTS = 3  # Número de tentativas em caso de falha
    
    # Lista de termos de busca
    SEARCH_TERMS = [
        "Pulverizador",
        "Trator",
        "Máquina agrícola",
        "Implemento agrícola",
        "Fertilizante",
        "Semente",
        "Defensivo agrícola",
        "Irrigação",
        "Colheitadeira",
        "Plantadeira"
    ]
    
    # Configurações do Chrome/Selenium
    CHROME_OPTIONS = [
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-gpu",
        "--window-size=1920,1080",
        "--disable-blink-features=AutomationControlled",
        "--disable-extensions",
        "--disable-plugins",
        "--disable-images",  # Carregar mais rápido
        #"--disable-javascript",  # Opcional: desabilitar JS se não necessário
    ]
    
    # Configurações de timeout
    PAGE_LOAD_TIMEOUT = 30
    ELEMENT_WAIT_TIMEOUT = 10
    IMPLICIT_WAIT = 5
    
    # Configurações de busca
    DEFAULT_SEARCH_TERM = "Pulverizador"
    MAX_PAGES_TO_SEARCH = 5  # Máximo de páginas para buscar licitações
    
    # Configurações de logging
    LOG_LEVEL = "INFO"
    LOG_FILE = "scraper.log"
    
    # Configurações de retry
    RETRY_DELAY = 2  # Segundos entre tentativas
    
    @classmethod
    def get_chrome_options(cls):
        """Retorna as opções do Chrome"""
        from selenium.webdriver.chrome.options import Options
        
        options = Options()
        for option in cls.CHROME_OPTIONS:
            options.add_argument(option)
        
        return options
    
    @classmethod
    def get_database_config(cls):
        """Retorna configurações do banco de dados"""
        return {
            'db_path': cls.DATABASE_PATH,
            'timeout': 30.0
        }
    
    @classmethod
    def get_threading_config(cls):
        """Retorna configurações de multithreading"""
        return {
            'max_workers': cls.MAX_WORKERS,
            'timeout': cls.THREAD_TIMEOUT,
            'retry_attempts': cls.RETRY_ATTEMPTS
        }
    
    @classmethod
    def get_timeout_config(cls):
        """Retorna configurações de timeout"""
        return {
            'page_load': cls.PAGE_LOAD_TIMEOUT,
            'element_wait': cls.ELEMENT_WAIT_TIMEOUT,
            'implicit_wait': cls.IMPLICIT_WAIT
        }
    
    @classmethod
    def get_search_terms(cls):
        """Retorna a lista de termos de busca"""
        return cls.SEARCH_TERMS

class DevelopmentConfig(Config):
    """Configurações para desenvolvimento"""
    MAX_WORKERS = 2
    LOG_LEVEL = "DEBUG"
    CHROME_OPTIONS = [
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-gpu",
        "--window-size=1920,1080",
    ]
    # Lista reduzida para desenvolvimento
    SEARCH_TERMS = [
        "Pulverizador",
        "Trator",
        "Máquina agrícola"
    ]

class ProductionConfig(Config):
    """Configurações para produção"""
    MAX_WORKERS = 5
    LOG_LEVEL = "WARNING"
    CHROME_OPTIONS = [
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-gpu",
        "--window-size=1920,1080",
        "--headless",  # Executar sem interface gráfica
        "--disable-blink-features=AutomationControlled",
        "--disable-extensions",
        "--disable-plugins",
        "--disable-images",
    ]

class TestConfig(Config):
    """Configurações para testes"""
    MAX_WORKERS = 1
    LOG_LEVEL = "DEBUG"
    DATABASE_PATH = "database/test_licitacoes.db"
    MAX_PAGES_TO_SEARCH = 1
    # Lista mínima para testes
    SEARCH_TERMS = [
        "Pulverizador"
    ]

# Configuração padrão baseada no ambiente
def get_config():
    """Retorna a configuração apropriada baseada no ambiente"""
    env = os.getenv('SCRAPER_ENV', 'development').lower()
    
    if env == 'production':
        return ProductionConfig()
    elif env == 'test':
        return TestConfig()
    else:
        return DevelopmentConfig()

# Instância global de configuração
config = get_config() 