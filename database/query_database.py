#!/usr/bin/env python3
"""
Script para consultar e visualizar dados do banco de licitações
"""

from database_config import DatabaseManager
import sqlite3

def view_all_licitacoes():
    """Mostra todas as licitações no banco"""
    db = DatabaseManager()
    licitacoes = db.get_all_licitacoes()
    
    print("="*80)
    print("TODAS AS LICITAÇÕES NO BANCO DE DADOS")
    print("="*80)
    
    if not licitacoes:
        print("Nenhuma licitação encontrada no banco.")
        return
    
    for licitacao in licitacoes:
        print(f"\nID: {licitacao[0]}")
        print(f"ID PNCP: {licitacao[1]}")
        print(f"URL: {licitacao[2]}")
        print(f"Local: {licitacao[3]}")
        print(f"Órgão: {licitacao[4]}")
        print(f"Objeto: {licitacao[17]}")
        print(f"Data de Captura: {licitacao[18]}")
        print("-" * 50)

def view_licitacao_details(licitacao_id):
    """Mostra detalhes completos de uma licitação específica"""
    db = DatabaseManager()
    
    # Buscar licitação
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM licitacoes WHERE id = ?', (licitacao_id,))
    licitacao = cursor.fetchone()
    
    if not licitacao:
        print(f"Licitação com ID {licitacao_id} não encontrada.")
        return
    
    print("="*80)
    print(f"DETALHES DA LICITAÇÃO {licitacao_id}")
    print("="*80)
    
    print(f"ID PNCP: {licitacao[1]}")
    print(f"URL: {licitacao[2]}")
    print(f"Local: {licitacao[3]}")
    print(f"Órgão: {licitacao[4]}")
    print(f"Unidade Compradora: {licitacao[5]}")
    print(f"Modalidade: {licitacao[6]}")
    print(f"Amparo Legal: {licitacao[7]}")
    print(f"Tipo: {licitacao[8]}")
    print(f"Modo de Disputa: {licitacao[9]}")
    print(f"Registro de Preço: {licitacao[10]}")
    print(f"Fonte Orçamentária: {licitacao[11]}")
    print(f"Data de Divulgação: {licitacao[12]}")
    print(f"Situação: {licitacao[13]}")
    print(f"Data Início Propostas: {licitacao[14]}")
    print(f"Data Fim Propostas: {licitacao[15]}")
    print(f"Fonte: {licitacao[16]}")
    print(f"Objeto: {licitacao[17]}")
    print(f"Data de Captura: {licitacao[18]}")
    
    # Buscar itens
    print("\n" + "="*50)
    print("ITENS DA LICITAÇÃO")
    print("="*50)
    
    cursor.execute('SELECT * FROM itens_licitacao WHERE id_licitacao = ?', (licitacao_id,))
    itens = cursor.fetchall()
    
    if itens:
        for i, item in enumerate(itens, 1):
            print(f"\nItem {i}:")
            print(f"  Descrição: {item[2]}")
            print(f"  Quantidade: {item[3]}")
            print(f"  Valor Unitário: {item[4]}")
            print(f"  Valor Total: {item[5]}")
    else:
        print("Nenhum item encontrado para esta licitação.")
    
    # Buscar editais
    print("\n" + "="*50)
    print("EDITAIS DA LICITAÇÃO")
    print("="*50)
    
    cursor.execute('SELECT * FROM editais WHERE id_licitacao = ?', (licitacao_id,))
    editais = cursor.fetchall()
    
    if editais:
        for i, edital in enumerate(editais, 1):
            print(f"\nEdital {i}:")
            print(f"  URL: {edital[2]}")
            print(f"  Data de Captura: {edital[3]}")
    else:
        print("Nenhum edital encontrado para esta licitação.")
    
    conn.close()

def get_database_stats():
    """Mostra estatísticas do banco de dados"""
    db = DatabaseManager()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    print("="*50)
    print("ESTATÍSTICAS DO BANCO DE DADOS")
    print("="*50)
    
    # Contar licitações
    cursor.execute('SELECT COUNT(*) FROM licitacoes')
    total_licitacoes = cursor.fetchone()[0]
    print(f"Total de Licitações: {total_licitacoes}")
    
    # Contar itens
    cursor.execute('SELECT COUNT(*) FROM itens_licitacao')
    total_itens = cursor.fetchone()[0]
    print(f"Total de Itens: {total_itens}")
    
    # Contar editais
    cursor.execute('SELECT COUNT(*) FROM editais')
    total_editais = cursor.fetchone()[0]
    print(f"Total de Editais: {total_editais}")
    
    # Licitações por órgão
    print("\nLicitações por Órgão:")
    cursor.execute('SELECT orgao, COUNT(*) FROM licitacoes GROUP BY orgao ORDER BY COUNT(*) DESC')
    orgaos = cursor.fetchall()
    
    for orgao, count in orgaos:
        print(f"  {orgao}: {count}")
    
    conn.close()

def search_licitacoes(termo):
    """Busca licitações por termo no objeto"""
    db = DatabaseManager()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, id_contratacao_pncp, orgao, objeto, data_captura 
        FROM licitacoes 
        WHERE objeto LIKE ? OR orgao LIKE ?
        ORDER BY data_captura DESC
    ''', (f'%{termo}%', f'%{termo}%'))
    
    resultados = cursor.fetchall()
    
    print(f"\nResultados para '{termo}':")
    print("="*80)
    
    if resultados:
        for resultado in resultados:
            print(f"ID: {resultado[0]} | PNCP: {resultado[1]}")
            print(f"Órgão: {resultado[2]}")
            print(f"Objeto: {resultado[3]}")
            print(f"Data: {resultado[4]}")
            print("-" * 50)
    else:
        print("Nenhuma licitação encontrada com esse termo.")
    
    conn.close()

if __name__ == "__main__":
    while True:
        print("\n" + "="*50)
        print("CONSULTA AO BANCO DE DADOS DE LICITAÇÕES")
        print("="*50)
        print("1. Ver todas as licitações")
        print("2. Ver detalhes de uma licitação específica")
        print("3. Ver estatísticas do banco")
        print("4. Buscar licitações por termo")
        print("5. Sair")
        
        opcao = input("\nEscolha uma opção (1-5): ").strip()
        
        if opcao == "1":
            view_all_licitacoes()
        
        elif opcao == "2":
            try:
                licitacao_id = int(input("Digite o ID da licitação: "))
                view_licitacao_details(licitacao_id)
            except ValueError:
                print("ID inválido. Digite um número.")
        
        elif opcao == "3":
            get_database_stats()
        
        elif opcao == "4":
            termo = input("Digite o termo para buscar: ").strip()
            if termo:
                search_licitacoes(termo)
            else:
                print("Termo não pode estar vazio.")
        
        elif opcao == "5":
            print("Saindo...")
            break
        
        else:
            print("Opção inválida. Tente novamente.") 