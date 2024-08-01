from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import WebDriverException, NoSuchElementException, ElementNotInteractableException
import pandas as pd
import time
import os
import smtplib
from email.message import EmailMessage
import mimetypes

# Configuração do driver do Chrome
options = Options()
# options.add_argument("--headless")  # Remova ou comente esta linha
options.add_argument('--ignore-certificate-errors')
options.add_argument('--disable-web-security')
options.add_argument('--allow-running-insecure-content')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--no-sandbox')
options.add_experimental_option('excludeSwitches', ['enable-logging'])

service = Service('CAMINHO PARA O CHROMEDRIVER')

output_dir = (r"CAMINHO PARA A PASTA OUTPUT")

def load_site(url, retries=3):
    while retries > 0:
        try:
            driver = webdriver.Chrome(service=service, options=options)
            driver.get(url)
            time.sleep(10)  # Aguarde o carregamento do site
            return driver
        except WebDriverException as e:
            print(f"Erro ao carregar o site: {e}")
            retries -= 1
            if retries == 0:
                with open("error_log.txt", "w") as log:
                    log.write("Site fora do ar")
                return None

def search_product(driver, search_query):
    search_box = driver.find_element(By.CSS_SELECTOR, "input[type='search']")
    search_box.send_keys(search_query)
    search_box.send_keys(Keys.RETURN)
    time.sleep(6)  # Aguarde os resultados

    all_data = []
    page_count = 0  # Contador de páginas

    while page_count < 20:  # Limita a 10 páginas
        time.sleep(4)  # Aguarde os resultados da página
        
        # Extraia dados da página atual
        data = extract_data(driver)
        all_data.extend(data)

        # Tente encontrar o botão "Próxima"
        try:
            next_button = driver.find_element(By.CSS_SELECTOR, "button[type='next']")
            if "disabled" in next_button.get_attribute("class"):
                break  # Se o botão estiver desabilitado, pare o loop

            ActionChains(driver).move_to_element(next_button).click().perform()
            time.sleep(4)  # Aguarde a nova página carregar
            page_count += 1  # Incrementa o contador de páginas
        except (NoSuchElementException, ElementNotInteractableException):
            break  # Sai do loop se não houver mais páginas

    return all_data

def extract_data(driver):
    try:
        products = driver.find_elements(By.CLASS_NAME, "sc-fTyFcS.iTkWie")
        data = []
        for product in products:
            try:
                name = product.find_element(By.CLASS_NAME, "sc-elxqWl.kWTxnF").text
                url = product.find_element(By.TAG_NAME, "a").get_attribute("href")

                try:
                    reviews = product.find_element(By.CLASS_NAME, "sc-epqpcT.jdMYPv").text
                    reviews = float(reviews.split()[0].replace(',', '.'))
                    reviews = int(reviews)
                except NoSuchElementException:
                    reviews = "ND"

                data.append([name, reviews, url])
                print(f"Produto: {name}, Avaliações: {reviews}, URL: {url}")
            except NoSuchElementException as e:
                print(f"Erro ao extrair informações de um produto: {e}")
                continue
        return data
    except NoSuchElementException as e:
        print(f"Erro ao extrair dados: {e}")
        return []

def save_to_excel(data):
    df = pd.DataFrame(data, columns=["PRODUTO", "QTD_AVAL", "URL"])
    df_with_reviews = df[df["QTD_AVAL"] != "ND"].copy()
    df_with_reviews["QTD_AVAL"] = pd.to_numeric(df_with_reviews["QTD_AVAL"])

    df_no_reviews = df[df["QTD_AVAL"] == "ND"]

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_path = os.path.join(output_dir, "Notebooks.xlsx")

    with pd.ExcelWriter(output_path) as writer:
        if not df_with_reviews[df_with_reviews["QTD_AVAL"] <= 3].empty:
            df_with_reviews[df_with_reviews["QTD_AVAL"] <= 3].to_excel(writer, sheet_name="Piores", index=False)
        if not df_with_reviews[df_with_reviews["QTD_AVAL"] > 3].empty:
            df_with_reviews[df_with_reviews["QTD_AVAL"] > 3].to_excel(writer, sheet_name="Melhores", index=False)
        if not df_no_reviews.empty:
            df_no_reviews.to_excel(writer, sheet_name="Sem Avaliação", index=False)

    print(f"Planilha salva em: {output_path}")
    return output_path

def send_email(filepath):
    msg = EmailMessage()
    msg['Subject'] = 'Relatório Notebooks'
    msg['From'] = 'SEUEMAIL@GMAIL.COM'  # Substitua pelo seu e-mail
    msg['To'] = 'CONTATOEMAIL@GMAIL.COM'
    msg.set_content('''Olá, aqui está o seu relatório dos notebooks extraídos da Magazine Luiza.

Atenciosamente,
Robô''')

    # Anexando o arquivo
    mime_type, _ = mimetypes.guess_type(filepath)
    mime_type, mime_subtype = mime_type.split('/')

    with open(filepath, 'rb') as file:
        msg.add_attachment(file.read(), maintype=mime_type, subtype=mime_subtype, filename=os.path.basename(filepath))

    # Enviando o e-mail
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login('SEUEMAIL@GMAIL.COM', 'SENHA')  # Substitua pelo seu e-mail e senha de aplicativo
        smtp.send_message(msg)
    print("E-mail enviado com sucesso!")

def main():
    url = "https://www.magazineluiza.com.br/"
    driver = load_site(url)
    if not driver:
        return
    
    all_data = search_product(driver, "notebooks")
    driver.quit()
    
    if all_data:
        filepath = save_to_excel(all_data)
        send_email(filepath)
    else:
        print("Nenhum dado extraído.")

if __name__ == "__main__":
    main()
