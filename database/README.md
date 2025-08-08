# Banco de Dados de Licitações

Este diretório contém o banco de dados SQLite para armazenar informações de licitações extraídas do PNCP (Portal Nacional de Contratações Públicas).

## Estrutura do Banco

### Tabela: `licitacoes`
Armazena as informações principais de cada licitação.

**Campos:**
- `id` (INTEGER PRIMARY KEY AUTOINCREMENT): ID único da licitação
- `id_contratacao_pncp` (TEXT UNIQUE): ID da contratação no PNCP
- `url` (TEXT): URL da página da licitação
- `local` (TEXT): Local da licitação
- `orgao` (TEXT): Órgão responsável
- `unidade_compradora` (TEXT): Unidade compradora
- `modalidade` (TEXT): Modalidade da contratação
- `amparo_legal` (TEXT): Amparo legal
- `tipo` (TEXT): Tipo da licitação
- `modo_disputa` (TEXT): Modo de disputa
- `registro_preco` (TEXT): Registro de preço
- `fonte_orcamentaria` (TEXT): Fonte orçamentária
- `data_divulgacao` (TEXT): Data de divulgação no PNCP
- `situacao` (TEXT): Situação da licitação
- `data_inicio_propostas` (TEXT): Data de início de recebimento de propostas
- `data_fim_propostas` (TEXT): Data fim de recebimento de propostas
- `fonte` (TEXT): Fonte da licitação
- `objeto` (TEXT): Objeto da licitação
- `data_captura` (TIMESTAMP): Data e hora da captura

### Tabela: `itens_licitacao`
Armazena os itens de cada licitação.

**Campos:**
- `id` (INTEGER PRIMARY KEY AUTOINCREMENT): ID único do item
- `id_licitacao` (INTEGER): ID da licitação (chave estrangeira)
- `descricao` (TEXT): Descrição do item
- `quantidade` (TEXT): Quantidade solicitada
- `valor_unitario_estimado` (TEXT): Valor unitário estimado
- `valor_total_estimado` (TEXT): Valor total estimado
- `data_captura` (TIMESTAMP): Data e hora da captura

### Tabela: `editais`
Armazena os editais de cada licitação.

**Campos:**
- `id` (INTEGER PRIMARY KEY AUTOINCREMENT): ID único do edital
- `id_licitacao` (INTEGER): ID da licitação (chave estrangeira)
- `url_edital` (TEXT): URL do edital
- `data_captura` (TIMESTAMP): Data e hora da captura

## Arquivos

### `database_config.py`
Contém a classe `DatabaseManager` que gerencia todas as operações do banco de dados:
- Criação das tabelas
- Inserção de dados
- Consultas
- Gerenciamento de conexões

### `query_database.py`
Script interativo para consultar e visualizar os dados do banco:
- Listar todas as licitações
- Ver detalhes de uma licitação específica
- Estatísticas do banco
- Busca por termo

## Como Usar

### 1. Inicializar o Banco
```python
from database.database_config import DatabaseManager

# Criar instância do banco (cria as tabelas automaticamente)
db = DatabaseManager()
```

### 2. Inserir Dados
```python
# Inserir licitação
licitacao_data = {
    'id_contratacao_pncp': '123456',
    'url': 'https://pncp.gov.br/...',
    'local': 'São Paulo',
    # ... outros campos
}
licitacao_id = db.insert_licitacao(licitacao_data)

# Inserir itens
itens = [
    {'descricao': 'Item 1', 'quantidade': '10', ...},
    {'descricao': 'Item 2', 'quantidade': '5', ...}
]
db.insert_itens(licitacao_id, itens)

# Inserir editais
editais = [
    {'edital': 'https://example.com/edital1.pdf'},
    {'edital': 'https://example.com/edital2.pdf'}
]
db.insert_editais(licitacao_id, editais)
```

### 3. Consultar Dados
```python
# Todas as licitações
licitacoes = db.get_all_licitacoes()

# Itens de uma licitação
itens = db.get_itens_by_licitacao(licitacao_id)

# Editais de uma licitação
editais = db.get_editais_by_licitacao(licitacao_id)
```

### 4. Usar o Script de Consulta
```bash
cd database
python query_database.py
```

## Integração com o Scraper

O banco de dados está integrado ao scraper principal (`main.py`). A função `catch_bids_information()` agora:
1. Coleta as informações da licitação
2. Salva automaticamente no banco de dados
3. Coleta e salva os itens
4. Coleta e salva os editais

## Localização do Banco

O arquivo do banco SQLite está localizado em:
```
database/licitacoes.db
```

## Backup e Manutenção

Para fazer backup do banco:
```bash
cp database/licitacoes.db database/licitacoes_backup_$(date +%Y%m%d).db
```

Para verificar a integridade do banco:
```bash
sqlite3 database/licitacoes.db "PRAGMA integrity_check;"
``` 