from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import pandas as pd
from typing import Dict, List, Optional

class EditalPNCPExtractor:
    def __init__(self, headless: bool = True, timeout: int = 10):
        """
        Inicializa o extrator de dados de editais do PNCP
        
        Args:
            headless: Se True, executa o navegador em modo headless
            timeout: Tempo limite para aguardar elementos (segundos)
        """
        self.timeout = timeout
        self.driver = self._setup_driver(headless)
        self.wait = WebDriverWait(self.driver, timeout)
    
    def _setup_driver(self, headless: bool) -> webdriver.Chrome:
        """Configura e retorna o driver do Chrome"""
        options = Options()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        
        return webdriver.Chrome(options=options)
    
    def extract_edital_data(self, url: str) -> Dict:
        """
        Extrai dados completos de um edital do PNCP
        
        Args:
            url: URL do edital no PNCP
            
        Returns:
            Dict com todos os dados extraídos do edital
        """
        try:
            self.driver.get(url)
            
            # Aguarda o carregamento da página - elemento principal correto
            self.wait.until(EC.presence_of_element_located((By.ID, "main-content")))
            
            edital_data = {}
            
            # Extrai informações básicas
            edital_data.update(self._extract_basic_info())
            
            # Extrai cronograma
            edital_data.update(self._extract_timeline())
            
            # Extrai identificação
            edital_data.update(self._extract_identification())
            
            # Extrai objeto
            edital_data['objeto'] = self._extract_object()
            
            # Extrai valor
            edital_data['valor_total_estimado'] = self._extract_total_value()
            
            # Extrai itens
            edital_data['itens'] = self._extract_items()
            
            # Extrai histórico
            edital_data['historico'] = self._extract_history()
            
            # Extrai contratos/empenhos
            edital_data['contratos_empenhos'] = self._extract_contracts()
            
            return edital_data
            
        except Exception as e:
            print(f"Erro ao extrair dados do edital: {str(e)}")
            return {}
    
    def _extract_basic_info(self) -> Dict:
        """Extrai informações básicas do edital"""
        basic_info = {}
        
        try:
            # Título do edital
            title_element = self.driver.find_element(By.TAG_NAME, "h1")
            basic_info['titulo'] = title_element.text.strip()
            
            # Extrai campos básicos usando estrutura real do DOM
            basic_info['local'] = self._extract_field_value('Local:')
            basic_info['orgao'] = self._extract_field_value('Órgão:')
            basic_info['unidade_compradora'] = self._extract_field_value('Unidade compradora:')
            basic_info['modalidade_contratacao'] = self._extract_field_value('Modalidade da contratação:')
            basic_info['amparo_legal'] = self._extract_field_value('Amparo legal:')
            basic_info['tipo'] = self._extract_field_value('Tipo:')
            basic_info['modo_disputa'] = self._extract_field_value('Modo de disputa:')
            basic_info['registro_preco'] = self._extract_field_value('Registro de preço:')
            basic_info['fonte_orcamentaria'] = self._extract_field_value('Fonte orçamentária:')
            
        except Exception as e:
            print(f"Erro ao extrair informações básicas: {str(e)}")
        
        return basic_info
    
    def _extract_field_value(self, field_label: str) -> str:
        """Extrai valor de um campo específico"""
        try:
            # Busca o strong que contém o label e pega o span seguinte
            element = self.driver.find_element(By.XPATH, f"//strong[contains(text(), '{field_label}')]/following-sibling::span")
            return element.text.strip()
        except NoSuchElementException:
            return "Não informado"
    
    def _extract_timeline(self) -> Dict:
        """Extrai informações de cronograma"""
        timeline = {}
        
        try:
            # Última atualização - classe correta do DOM
            update_element = self.driver.find_element(By.CLASS_NAME, "dtAtualizacao")
            timeline['ultima_atualizacao'] = update_element.text.replace("Última atualização ", "").strip()
            
            # Extrai campos de cronograma
            timeline['data_divulgacao_pncp'] = self._extract_field_value('Data de divulgação no PNCP:')
            timeline['situacao'] = self._extract_field_value('Situação:')
            timeline['data_inicio_propostas'] = self._extract_field_value('Data de início de recebimento de propostas:')
            timeline['data_fim_propostas'] = self._extract_field_value('Data fim de recebimento de propostas:')
                    
        except Exception as e:
            print(f"Erro ao extrair cronograma: {str(e)}")
        
        return timeline
    
    def _extract_identification(self) -> Dict:
        """Extrai informações de identificação"""
        identification = {}
        
        try:
            identification['id_contratacao_pncp'] = self._extract_field_value('Id contratação PNCP:')
            identification['fonte'] = self._extract_field_value('Fonte:')
                    
        except Exception as e:
            print(f"Erro ao extrair identificação: {str(e)}")
        
        return identification
    
    def _extract_object(self) -> str:
        """Extrai o objeto do edital"""
        try:
            # Busca pela classe correta no DOM
            object_element = self.driver.find_element(By.CLASS_NAME, "conteudo-objeto")
            return object_element.text.strip()
        except NoSuchElementException:
            return "Não informado"
    
    def _extract_total_value(self) -> str:
        """Extrai o valor total estimado"""
        try:
            # Busca na div com classe específica do DOM
            value_container = self.driver.find_element(By.XPATH, "//strong[contains(text(), 'VALOR TOTAL ESTIMADO')]/following-sibling::*//span")
            return value_container.text.strip()
        except NoSuchElementException:
            return "Não informado"
    
    def _extract_items(self) -> List[Dict]:
        """Extrai os itens do edital"""
        items = []
        
        try:
            # Verifica se a aba de itens está ativa, se não, clica nela
            items_tab = self.driver.find_element(By.XPATH, "//span[text()='Itens']/parent::button")
            if 'is-active' not in items_tab.get_attribute('class'):
                items_tab.click()
                time.sleep(2)
            
            # Aguarda a tabela de itens carregar - estrutura correta do DOM
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "datatable-body-row")))
            
            # Extrai todas as linhas da tabela de itens
            rows = self.driver.find_elements(By.CSS_SELECTOR, "datatable-body-row")
            
            for row in rows:
                try:
                    # Busca as células usando a estrutura correta do DOM
                    cells = row.find_elements(By.CSS_SELECTOR, "datatable-body-cell .datatable-body-cell-label span")
                    
                    if len(cells) >= 5:
                        item = {
                            'numero': cells[0].text.strip(),
                            'descricao': cells[1].text.strip(),
                            'quantidade': cells[2].text.strip(),
                            'valor_unitario': cells[3].text.strip(),
                            'valor_total': cells[4].text.strip()
                        }
                        items.append(item)
                except Exception as e:
                    print(f"Erro ao extrair item: {str(e)}")
                    continue
            
            # Tenta navegar pelas páginas se houver mais itens
            items.extend(self._extract_items_pagination())
            
        except Exception as e:
            print(f"Erro ao extrair itens: {str(e)}")
        
        return items
    
    def _extract_items_pagination(self) -> List[Dict]:
        """Extrai itens das páginas seguintes"""
        additional_items = []
        
        try:
            # Verifica se há botão de próxima página - ID correto do DOM
            next_button = self.driver.find_element(By.ID, "btn-next-page")
            
            while not next_button.get_attribute('disabled'):
                next_button.click()
                time.sleep(2)
                
                # Aguarda nova página carregar
                self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "datatable-body-row")))
                
                # Extrai itens da página atual
                rows = self.driver.find_elements(By.CSS_SELECTOR, "datatable-body-row")
                
                for row in rows:
                    try:
                        cells = row.find_elements(By.CSS_SELECTOR, "datatable-body-cell .datatable-body-cell-label span")
                        if len(cells) >= 5:
                            item = {
                                'numero': cells[0].text.strip(),
                                'descricao': cells[1].text.strip(),
                                'quantidade': cells[2].text.strip(),
                                'valor_unitario': cells[3].text.strip(),
                                'valor_total': cells[4].text.strip()
                            }
                            additional_items.append(item)
                    except Exception as e:
                        continue
                
                # Atualiza referência do botão
                next_button = self.driver.find_element(By.ID, "btn-next-page")
                
        except (NoSuchElementException, TimeoutException):
            pass  # Não há mais páginas
        
        return additional_items
    
    def _extract_history(self) -> List[Dict]:
        """Extrai o histórico do edital"""
        history = []
        
        try:
            # Clica na aba de histórico
            history_tab = self.driver.find_element(By.XPATH, "//span[text()='Histórico']/parent::button")
            history_tab.click()
            time.sleep(2)
            
            # Aguarda a tabela carregar
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "datatable-body-row")))
            
            rows = self.driver.find_elements(By.CSS_SELECTOR, "datatable-body-row")
            
            for row in rows:
                try:
                    cells = row.find_elements(By.CSS_SELECTOR, "datatable-body-cell .datatable-body-cell-label span")
                    if len(cells) >= 2:
                        event = {
                            'evento': cells[0].text.strip(),
                            'data_hora': cells[1].text.strip() if cells[1].text.strip() else 
                                       row.find_elements(By.CSS_SELECTOR, "datatable-body-cell .datatable-body-cell-label")[1].text.strip()
                        }
                        history.append(event)
                except Exception as e:
                    continue
                    
        except Exception as e:
            print(f"Erro ao extrair histórico: {str(e)}")
        
        return history
    
    def _extract_contracts(self) -> List[Dict]:
        """Extrai contratos/empenhos"""
        contracts = []
        
        try:
            # Clica na aba de contratos/empenhos
            contracts_tab = self.driver.find_element(By.XPATH, "//span[text()='Contratos/Empenhos']/parent::button")
            contracts_tab.click()
            time.sleep(2)
            
            # Aguarda a tabela carregar
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "datatable-body-row")))
            
            rows = self.driver.find_elements(By.CSS_SELECTOR, "datatable-body-row")
            
            for row in rows:
                try:
                    cells = row.find_elements(By.CSS_SELECTOR, "datatable-body-cell .datatable-body-cell-label")
                    if len(cells) >= 5:
                        # Extrai texto considerando diferentes estruturas
                        contract = {
                            'numero': self._get_cell_text(cells[0]),
                            'data_assinatura': self._get_cell_text(cells[1]),
                            'vigencia': self._get_cell_text(cells[2]),
                            'id_contrato_pncp': self._get_cell_text(cells[3]),
                            'valor_global': self._get_cell_text(cells[4])
                        }
                        contracts.append(contract)
                except Exception as e:
                    continue
                    
        except Exception as e:
            print(f"Erro ao extrair contratos: {str(e)}")
        
        return contracts
    
    def _get_cell_text(self, cell_element) -> str:
        """Extrai texto de uma célula, tratando diferentes estruturas"""
        try:
            # Tenta pegar span primeiro
            span = cell_element.find_element(By.TAG_NAME, "span")
            return span.text.strip()
        except NoSuchElementException:
            # Se não tem span, pega o texto direto
            return cell_element.text.strip()
    
   
            
        except Exception as e:
            print(f"Erro ao salvar arquivo Excel: {str(e)}")
    
    def close(self):
        """Fecha o navegador"""
        if self.driver:
            self.driver.quit()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# Exemplo de uso
if __name__ == '__main__':
    """Exemplo de como usar o extrator"""
    
    # URL do edital (substitua pela URL real)
    edital_url = "https://pncp.gov.br/editais/12075748000132/2025/7"
    
    # Usa o extrator
    with EditalPNCPExtractor(headless=False) as extractor:
        print("Extraindo dados do edital...")
        data = extractor.extract_edital_data(edital_url)
        
        if data:
            print("\nDados extraídos com sucesso!")
            print(f"Título: {data.get('titulo', 'N/A')}")
            print(f"Órgão: {data.get('orgao', 'N/A')}")
            print(f"Total de itens: {len(data.get('itens', []))}")
      
            
            # Exibe amostra dos dados
            print("\n--- Amostra dos dados extraídos ---")
            for key, value in data.items():
                if isinstance(value, list):
                    print(f"{key}: {len(value)} registros")
                else:
                    print(f"{key}: {value}")
        else:
            print("Falha na extração dos dados.")