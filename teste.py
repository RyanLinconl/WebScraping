from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# Definindo as opções do Chrome
chrome_options = Options()
chrome_options.add_argument("--headless")  # Executa o Chrome em modo headless
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Iniciando o serviço do ChromeDriver
service = Service(executable_path="CAMINHO PARA O CHROMEDRIVER")
driver = webdriver.Chrome(service=service, options=chrome_options)

# Acessando a página da Magazine Luiza
driver.get("https://www.magazineluiza.com.br/busca/notebook/")

# Esperando a página carregar completamente
driver.implicitly_wait(10)

# Extraindo informações dos produtos
produtos = driver.find_elements(By.CLASS_NAME, "sc-kOPcWz iWSguL sc-bJBgwP kfukcU sc-doohEh fhSPNy")

for produto in produtos:
    nome = produto.find_element(By.CLASS_NAME, "sc-ijtseF jCSvaQ").text
    avaliacao = produto.find_element(By.CLASS_NAME, "sc-rPWID jLacQQ").text
    link = produto.find_element(By.TAG_NAME, "a").get_attribute("href")
    print(f"Nome: {nome}, Avaliação: {avaliacao}, Link: {link}")

# Fechando o navegador
driver.quit()

