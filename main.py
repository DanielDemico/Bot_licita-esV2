from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import time
from datetime import datetime
from database.database_config import DatabaseManager

def setup_driver():
    """Configura e retorna o driver do Chrome"""
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def scroll_down(driver):
    """Rola a página para baixo"""
    driver.execute_script("window.scrollTo(0, 1000);")

def catch_especifique_information(driver, element_string) -> str:
    """Pega informações específicas da página"""
    wait = WebDriverWait(driver, 10)
    try:
        x = wait.until(EC.presence_of_element_located((By.XPATH, f'//strong[contains(.,"{element_string}")]/following-sibling::span'))).text
    except (TimeoutException, NoSuchElementException):
        x = f'{element_string.replace(":","")} Não encontrado'
    except Exception as e:
        x = 'Não encontrado'
        print(f"Erro ao buscar {element_string}: {e}")
    return x

def catch_bid_items(driver, id_licitacao) -> list:
    """Pega os itens da licitação"""
    pattern_path = '//*[@id="main-content"]/pncp-item-detail/div/pncp-tab-set/div/pncp-tab[1]/div/div/pncp-table/div/ngx-datatable/div/datatable-body/datatable-selection/datatable-scroller'
    wait = WebDriverWait(driver, 10)
    items = []
    linha = 1

    while True:
        time.sleep(0.2)
        try:
            desc_path = f'{pattern_path}/datatable-row-wrapper[{linha}]/datatable-body-row/div[2]/datatable-body-cell[2]/div/span'
            desc = wait.until(EC.presence_of_element_located((By.XPATH, desc_path))).text
            
            quant_path = f'{pattern_path}/datatable-row-wrapper[{linha}]/datatable-body-row/div[2]/datatable-body-cell[3]/div/span'
            quant = wait.until(EC.presence_of_element_located((By.XPATH, quant_path))).text

            valor_unit_path = f'{pattern_path}/datatable-row-wrapper[{linha}]/datatable-body-row/div[2]/datatable-body-cell[4]/div/span'
            valor_unit = wait.until(EC.presence_of_element_located((By.XPATH, valor_unit_path))).text

            valor_est_path = f'{pattern_path}/datatable-row-wrapper[{linha}]/datatable-body-row/div[2]/datatable-body-cell[4]/div/span'
            valor_est = wait.until(EC.presence_of_element_located((By.XPATH, valor_est_path))).text

            linha += 1

            item_data = {
                'id_licitacao': id_licitacao,
                'descricao': desc,
                'quantidade': quant,
                'valor_unitario_estimado': valor_unit,
                'valor_total_estimado': valor_est
            }
            items.append(item_data)

            if linha == 6:
                scroll_down(driver)
                button = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(@aria-label,"Ir para próxima página")]')))
                button.click()
                linha = 1
                
        except (TimeoutException, NoSuchElementException):
            print('Acabaram os itens')
            break
        except Exception as e:
            print('Erro ao processar item:', e)
            break

    return items

def catch_bid_archs(driver, id_licitacao) -> list:
    """Pega os editais da licitação"""
    wait = WebDriverWait(driver, 10)
    pattern_path = '//*[@id="main-content"]/pncp-item-detail/div/pncp-tab-set/div/pncp-tab[2]/div/div/pncp-table/div/ngx-datatable/div/datatable-body/datatable-selection/datatable-scroller'
    linha = 1
    editais = []
    pagina = 1

    while True:
        time.sleep(0.5)
        try:
            tipo_path = f'{pattern_path}/datatable-row-wrapper[{linha}]/datatable-body-row/div[2]/datatable-body-cell[3]/div/span'
            tipo = wait.until(EC.presence_of_element_located((By.XPATH, tipo_path))).get_attribute('title')
            
            if tipo != 'Edital':
                linha += 1
                continue
            else:
                edital_path = f'{pattern_path}/datatable-row-wrapper[{linha}]/datatable-body-row/div[2]/datatable-body-cell[4]/div/div/a'
                edital_element = wait.until(EC.presence_of_element_located((By.XPATH, edital_path)))
                edital = edital_element.get_attribute('href')
                
                if edital:
                    editais.append({'id_licitacao': id_licitacao, "edital": edital})
                
                linha += 1
                
        except (TimeoutException, NoSuchElementException):
            try:
                scroll_down(driver)
                time.sleep(1)
                
                next_button = driver.find_elements(By.XPATH, '//button[contains(@aria-label,"Ir para próxima página")]')
                
                if next_button and next_button[0].is_enabled():
                    next_button[0].click()
                    pagina += 1
                    linha = 1
                    time.sleep(2)
                else:
                    break
                    
            except Exception:
                break
                
        except Exception as e:
            linha += 1
            time.sleep(1)
    
    return editais

def catch_bids_links(driver, termo) -> list:
    """Busca links de licitações"""
    driver.get("https://pncp.gov.br/app/editais?q=&status=recebendo_proposta&pagina=1")
    
    input_camp = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="keyword"]'))
    )
    input_camp.send_keys(termo)
    input_camp.send_keys(Keys.ENTER)

    licitacoes_extraidas = []
    pagina = 1
    i = 1
    
    while True:
        pattern_path = f'//*[@id="main-content"]/pncp-list/pncp-results-panel/pncp-tab-set/div/pncp-tab[1]/div/div[2]/div/div[2]/pncp-items-list/div/div[{i}]/a'
        data_licitacao_path = f'{pattern_path}/div/div[1]/div/div/div[2]/div[3]/div[2]'
        data_hoje = datetime.today().strftime('%d/%m/%Y')
        
        try:
            licitacao_a = WebDriverWait(driver, 5).until(          
                EC.presence_of_element_located((By.XPATH, pattern_path))
            )   
            try: 
                data_licitacao = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, data_licitacao_path))
                ).text
                data_licitacao = data_licitacao.split(' ')[-1]
                
                if data_hoje == data_licitacao:
                    licitacoes_extraidas.append(licitacao_a.get_attribute('href'))
                    print(f"Licitação de hoje encontrada: {licitacao_a.get_attribute('href')}")
                else:
                    print(f"Licitação não é de hoje: {data_licitacao}")
                    break
                    
            except NoSuchElementException:
                print('Data não encontrada')
            except Exception as e:
                print('Erro ao buscar data:', e)

        except (TimeoutException, NoSuchElementException):
            print("Acabaram as licitações da página")
            try: 
                scroll_down(driver)
                button_page = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, f'//button[text()=" {pagina + 1} "]'))
                )
                button_page.click()
                pagina += 1
                i = 1
            except (TimeoutException, NoSuchElementException):
                print('Acabaram todas as licitações')
                break
            except Exception as e:
                print('Erro ao navegar:', e)
                break
        except Exception as e:
            print(f"Erro geral: {e}")
            break
            
        i += 1
        if i > 11:
            i = 1
            
    return licitacoes_extraidas

def process_licitacao(driver, url):
    """Processa uma licitação completa"""
    driver.get(url)
    wait = WebDriverWait(driver, 10)
    db = DatabaseManager()

    # Informações da licitação
    local = catch_especifique_information(driver, 'Local:')
    orgao = catch_especifique_information(driver, 'Órgão:')
    un_compradora = catch_especifique_information(driver, 'Unidade compradora:')
    modalidade = catch_especifique_information(driver, 'Modalidade da contratação:')
    amparo_legal = catch_especifique_information(driver, 'Amparo legal:')
    tipo = catch_especifique_information(driver, 'Tipo:')
    modo_disputa = catch_especifique_information(driver, 'Modo de disputa:')
    registro_preco = catch_especifique_information(driver, 'Registro de preço:')
    fonte_orc = catch_especifique_information(driver, 'Fonte orçamentária:')
    data_divulg = catch_especifique_information(driver, 'Data de divulgação no PNCP:')
    situacao = catch_especifique_information(driver, 'Situação:')
    data_inicio_propostas = catch_especifique_information(driver, 'Data de início de recebimento de propostas:')
    data_fim_propostas = catch_especifique_information(driver, 'Data fim de recebimento de propostas:')
    id_contratacao_pncp = catch_especifique_information(driver, 'Id contratação PNCP:')
    fonte = catch_especifique_information(driver, 'Fonte:')
    objeto = wait.until(EC.presence_of_element_located((By.XPATH, "//strong[contains(., 'Objeto:')]/following::span[1]"))).text

    # Preparar dados da licitação
    licitacao_data = {
        'id_contratacao_pncp': id_contratacao_pncp,
        'url': url,
        'local': local,
        'orgao': orgao,
        'unidade_compradora': un_compradora,
        'modalidade': modalidade,
        'amparo_legal': amparo_legal,
        'tipo': tipo,
        'modo_disputa': modo_disputa,
        'registro_preco': registro_preco,
        'fonte_orcamentaria': fonte_orc,
        'data_divulgacao': data_divulg,
        'situacao': situacao,
        'data_inicio_propostas': data_inicio_propostas,
        'data_fim_propostas': data_fim_propostas,
        'fonte': fonte,
        'objeto': objeto
    }

    # Inserir licitação no banco
    licitacao_id = db.insert_licitacao(licitacao_data)
    
    if licitacao_id:
        # Itens da licitação
        itens = catch_bid_items(driver, id_contratacao_pncp)
        print(f"Itens encontrados: {len(itens)}")
        
        if itens:
            db.insert_itens(licitacao_id, itens)
        
        # Buscar editais
        arquivos = catch_bid_archs(driver, id_contratacao_pncp)
        print(f"Editais encontrados: {len(arquivos)}")
        
        if arquivos:
            db.insert_editais(licitacao_id, arquivos)
        
        print(f"Licitação {id_contratacao_pncp} salva com sucesso!")
    else:
        print("Erro ao salvar licitação no banco de dados")

# CÓDIGO PRINCIPAL
if __name__ == "__main__":
    print("="*60)
    print("SCRAPER DE LICITAÇÕES - VERSÃO SIMPLIFICADA")
    print("="*60)
    
    # Configurar driver
    driver = setup_driver()
    
    try:
        # Termo de busca
        termo = "Pulverizador"
        print(f"Buscando licitações com termo: '{termo}'")
        
        # Buscar links de licitações
        licitacoes = catch_bids_links(driver, termo)
        
        if not licitacoes:
            print("Nenhuma licitação encontrada!")
        else:
            print(f"Encontradas {len(licitacoes)} licitações")
            
            # Processar cada licitação
            for i, url in enumerate(licitacoes, 1):
                try:
                    print(f"\nProcessando licitação {i}/{len(licitacoes)}")
                    process_licitacao(driver, url)
                except Exception as e:
                    print(f"Erro ao processar {url}: {e}")
                    continue
        
        print("\nProcessamento concluído!")
        
    except Exception as e:
        print(f"Erro geral: {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()
