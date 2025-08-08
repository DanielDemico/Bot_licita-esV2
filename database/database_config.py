import sqlite3
import os
from datetime import datetime
import threading
import time

class DatabaseManager:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, db_path="database/licitacoes.db"):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(DatabaseManager, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, db_path="database/licitacoes.db"):
        if not self._initialized:
            self.db_path = db_path
            self.ensure_database_directory()
            self.create_tables()
            # Lock para garantir thread-safety
            self._lock = threading.Lock()
            self._initialized = True
    
    def ensure_database_directory(self):
        """Garante que o diretório do banco existe"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    def get_connection(self):
        """Retorna uma conexão com o banco de dados"""
        return sqlite3.connect(self.db_path, timeout=30.0)
    
    def create_tables(self):
        """Cria as tabelas do banco de dados"""
        with self._lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Tabela de licitações
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS licitacoes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_contratacao_pncp TEXT UNIQUE,
                    url TEXT,
                    local TEXT,
                    orgao TEXT,
                    unidade_compradora TEXT,
                    modalidade TEXT,
                    amparo_legal TEXT,
                    tipo TEXT,
                    modo_disputa TEXT,
                    registro_preco TEXT,
                    fonte_orcamentaria TEXT,
                    data_divulgacao TEXT,
                    situacao TEXT,
                    data_inicio_propostas TEXT,
                    data_fim_propostas TEXT,
                    fonte TEXT,
                    objeto TEXT,
                    data_captura TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabela de itens da licitação
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS itens_licitacao (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_licitacao INTEGER,
                    descricao TEXT,
                    quantidade TEXT,
                    valor_unitario_estimado TEXT,
                    valor_total_estimado TEXT,
                    data_captura TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (id_licitacao) REFERENCES licitacoes (id)
                )
            ''')
            
            # Tabela de editais
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS editais (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_licitacao INTEGER,
                    url_edital TEXT,
                    data_captura TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (id_licitacao) REFERENCES licitacoes (id)
                )
            ''')
            
            conn.commit()
            conn.close()
            print("Tabelas criadas com sucesso!")
    
    def insert_licitacao(self, licitacao_data):
        """Insere uma licitação no banco de forma thread-safe"""
        with self._lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO licitacoes (
                        id_contratacao_pncp, url, local, orgao, unidade_compradora,
                        modalidade, amparo_legal, tipo, modo_disputa, registro_preco,
                        fonte_orcamentaria, data_divulgacao, situacao, data_inicio_propostas,
                        data_fim_propostas, fonte, objeto
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    licitacao_data.get('id_contratacao_pncp'),
                    licitacao_data.get('url'),
                    licitacao_data.get('local'),
                    licitacao_data.get('orgao'),
                    licitacao_data.get('unidade_compradora'),
                    licitacao_data.get('modalidade'),
                    licitacao_data.get('amparo_legal'),
                    licitacao_data.get('tipo'),
                    licitacao_data.get('modo_disputa'),
                    licitacao_data.get('registro_preco'),
                    licitacao_data.get('fonte_orcamentaria'),
                    licitacao_data.get('data_divulgacao'),
                    licitacao_data.get('situacao'),
                    licitacao_data.get('data_inicio_propostas'),
                    licitacao_data.get('data_fim_propostas'),
                    licitacao_data.get('fonte'),
                    licitacao_data.get('objeto')
                ))
                
                licitacao_id = cursor.lastrowid
                conn.commit()
                print(f"Licitação inserida com ID: {licitacao_id}")
                return licitacao_id
                
            except Exception as e:
                print(f"Erro ao inserir licitação: {e}")
                conn.rollback()
                return None
            finally:
                conn.close()
    
    def insert_itens(self, licitacao_id, itens):
        """Insere itens de uma licitação de forma thread-safe"""
        with self._lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            try:
                for item in itens:
                    cursor.execute('''
                        INSERT INTO itens_licitacao (
                            id_licitacao, descricao, quantidade, 
                            valor_unitario_estimado, valor_total_estimado
                        ) VALUES (?, ?, ?, ?, ?)
                    ''', (
                        licitacao_id,
                        item.get('descricao'),
                        item.get('quantidade'),
                        item.get('valor_unitario_estimado'),
                        item.get('valor_total_estimado')
                    ))
                
                conn.commit()
                print(f"{len(itens)} itens inseridos para a licitação {licitacao_id}")
                
            except Exception as e:
                print(f"Erro ao inserir itens: {e}")
                conn.rollback()
            finally:
                conn.close()
    
    def insert_editais(self, licitacao_id, editais):
        """Insere editais de uma licitação de forma thread-safe"""
        with self._lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            try:
                for edital in editais:
                    cursor.execute('''
                        INSERT INTO editais (id_licitacao, url_edital)
                        VALUES (?, ?)
                    ''', (licitacao_id, edital.get('edital')))
                
                conn.commit()
                print(f"{len(editais)} editais inseridos para a licitação {licitacao_id}")
                
            except Exception as e:
                print(f"Erro ao inserir editais: {e}")
                conn.rollback()
            finally:
                conn.close()
    
    def get_licitacao_by_pncp_id(self, pncp_id):
        """Busca uma licitação pelo ID do PNCP de forma thread-safe"""
        with self._lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM licitacoes WHERE id_contratacao_pncp = ?', (pncp_id,))
            result = cursor.fetchone()
            
            conn.close()
            return result
    
    def get_all_licitacoes(self):
        """Retorna todas as licitações de forma thread-safe"""
        with self._lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM licitacoes ORDER BY data_captura DESC')
            results = cursor.fetchall()
            
            conn.close()
            return results
    
    def get_itens_by_licitacao(self, licitacao_id):
        """Retorna todos os itens de uma licitação de forma thread-safe"""
        with self._lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM itens_licitacao WHERE id_licitacao = ?', (licitacao_id,))
            results = cursor.fetchall()
            
            conn.close()
            return results
    
    def get_editais_by_licitacao(self, licitacao_id):
        """Retorna todos os editais de uma licitação de forma thread-safe"""
        with self._lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM editais WHERE id_licitacao = ?', (licitacao_id,))
            results = cursor.fetchall()
            
            conn.close()
            return results
    
    def get_database_stats(self):
        """Retorna estatísticas do banco de forma thread-safe"""
        with self._lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Contar licitações
            cursor.execute('SELECT COUNT(*) FROM licitacoes')
            total_licitacoes = cursor.fetchone()[0]
            
            # Contar itens
            cursor.execute('SELECT COUNT(*) FROM itens_licitacao')
            total_itens = cursor.fetchone()[0]
            
            # Contar editais
            cursor.execute('SELECT COUNT(*) FROM editais')
            total_editais = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'total_licitacoes': total_licitacoes,
                'total_itens': total_itens,
                'total_editais': total_editais
            }
    
    def is_initialized(self):
        """Verifica se a instância está inicializada"""
        return hasattr(self, '_initialized') and self._initialized
    
    def get_instance_info(self):
        """Retorna informações sobre a instância"""
        return {
            'initialized': self.is_initialized(),
            'db_path': self.db_path,
            'has_lock': hasattr(self, '_lock')
        } 