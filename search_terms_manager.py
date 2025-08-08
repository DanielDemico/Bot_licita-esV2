#!/usr/bin/env python3
"""
Gerenciador de termos de busca para o scraper de licitações
"""

import json
import os
from datetime import datetime
from config import config

class SearchTermsManager:
    """Gerenciador de termos de busca"""
    
    def __init__(self, terms_file="search_terms.json"):
        self.terms_file = terms_file
        self.terms = self.load_terms()
    
    def load_terms(self):
        """Carrega termos do arquivo ou usa padrão"""
        if os.path.exists(self.terms_file):
            try:
                with open(self.terms_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('terms', config.get_search_terms())
            except Exception as e:
                print(f"Erro ao carregar termos do arquivo: {e}")
                return config.get_search_terms()
        else:
            return config.get_search_terms()
    
    def save_terms(self):
        """Salva termos no arquivo"""
        try:
            data = {
                'terms': self.terms,
                'last_updated': datetime.now().isoformat(),
                'total_terms': len(self.terms)
            }
            
            with open(self.terms_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"Termos salvos em {self.terms_file}")
        except Exception as e:
            print(f"Erro ao salvar termos: {e}")
    
    def add_term(self, term):
        """Adiciona um novo termo"""
        if term not in self.terms:
            self.terms.append(term)
            print(f"Termo '{term}' adicionado")
            return True
        else:
            print(f"Termo '{term}' já existe")
            return False
    
    def remove_term(self, term):
        """Remove um termo"""
        if term in self.terms:
            self.terms.remove(term)
            print(f"Termo '{term}' removido")
            return True
        else:
            print(f"Termo '{term}' não encontrado")
            return False
    
    def list_terms(self):
        """Lista todos os termos"""
        print(f"\nTermos de busca ({len(self.terms)}):")
        for i, term in enumerate(self.terms, 1):
            print(f"  {i}. {term}")
    
    def clear_terms(self):
        """Limpa todos os termos"""
        self.terms = []
        print("Todos os termos foram removidos")
    
    def get_terms(self):
        """Retorna a lista de termos"""
        return self.terms
    
    def get_terms_by_category(self):
        """Agrupa termos por categoria"""
        categories = {
            'Maquinário': ['Trator', 'Colheitadeira', 'Plantadeira', 'Máquina agrícola'],
            'Implementos': ['Pulverizador', 'Implemento agrícola'],
            'Insumos': ['Fertilizante', 'Semente', 'Defensivo agrícola'],
            'Sistemas': ['Irrigação']
        }
        
        grouped = {}
        for category, terms in categories.items():
            grouped[category] = [term for term in self.terms if term in terms]
        
        # Termos não categorizados
        categorized_terms = [term for terms in grouped.values() for term in terms]
        uncategorized = [term for term in self.terms if term not in categorized_terms]
        if uncategorized:
            grouped['Outros'] = uncategorized
        
        return grouped
    
    def show_categories(self):
        """Mostra termos agrupados por categoria"""
        grouped = self.get_terms_by_category()
        
        print("\nTermos por categoria:")
        for category, terms in grouped.items():
            if terms:
                print(f"\n{category} ({len(terms)}):")
                for term in terms:
                    print(f"  - {term}")

def interactive_terms_manager():
    """Interface interativa para gerenciar termos"""
    manager = SearchTermsManager()
    
    while True:
        print("\n" + "="*50)
        print("GERENCIADOR DE TERMOS DE BUSCA")
        print("="*50)
        print("1. Listar termos")
        print("2. Adicionar termo")
        print("3. Remover termo")
        print("4. Ver categorias")
        print("5. Limpar todos os termos")
        print("6. Salvar termos")
        print("7. Carregar termos padrão")
        print("8. Sair")
        
        opcao = input("\nEscolha uma opção (1-8): ").strip()
        
        if opcao == "1":
            manager.list_terms()
        
        elif opcao == "2":
            term = input("Digite o termo a adicionar: ").strip()
            if term:
                manager.add_term(term)
            else:
                print("Termo não pode estar vazio.")
        
        elif opcao == "3":
            manager.list_terms()
            try:
                index = int(input("Digite o número do termo a remover: ")) - 1
                if 0 <= index < len(manager.terms):
                    term = manager.terms[index]
                    manager.remove_term(term)
                else:
                    print("Índice inválido.")
            except ValueError:
                print("Digite um número válido.")
        
        elif opcao == "4":
            manager.show_categories()
        
        elif opcao == "5":
            confirm = input("Tem certeza que deseja limpar todos os termos? (s/n): ").strip().lower()
            if confirm == 's':
                manager.clear_terms()
        
        elif opcao == "6":
            manager.save_terms()
        
        elif opcao == "7":
            manager.terms = config.get_search_terms()
            print("Termos padrão carregados")
        
        elif opcao == "8":
            print("Saindo...")
            break
        
        else:
            print("Opção inválida. Tente novamente.")

def create_sample_terms():
    """Cria arquivo de exemplo com termos"""
    sample_terms = {
        "terms": [
            "Pulverizador",
            "Trator",
            "Máquina agrícola",
            "Implemento agrícola",
            "Fertilizante",
            "Semente",
            "Defensivo agrícola",
            "Irrigação",
            "Colheitadeira",
            "Plantadeira",
            "Arado",
            "Grade",
            "Enxada rotativa",
            "Sulfatadora",
            "Adubadora"
        ],
        "last_updated": datetime.now().isoformat(),
        "total_terms": 15
    }
    
    with open("search_terms.json", 'w', encoding='utf-8') as f:
        json.dump(sample_terms, f, indent=2, ensure_ascii=False)
    
    print("Arquivo search_terms.json criado com termos de exemplo")

if __name__ == "__main__":
    print("="*60)
    print("GERENCIADOR DE TERMOS DE BUSCA")
    print("="*60)
    
    if not os.path.exists("search_terms.json"):
        print("Arquivo search_terms.json não encontrado.")
        create = input("Deseja criar um arquivo de exemplo? (s/n): ").strip().lower()
        if create == 's':
            create_sample_terms()
    
    interactive_terms_manager() 