import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

def setup_browser():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Rulează în fundal
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def search_avstore(artist, album):
    driver = setup_browser()
    search_url = "https://www.avstore.ro/viniluri/"
    
    driver.get(search_url)
    time.sleep(2)
    
    try:
        # Găsim bara de căutare și introducem numele vinilului
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "q"))
        )
        search_box.clear()
        search_box.send_keys(f"{artist} {album}")
        search_box.send_keys(Keys.RETURN)
        
        # Așteptăm să fim redirecționați către pagina produsului
        time.sleep(3)
        print(f"Căutare efectuată pe AVstore pentru: {artist} - {album}")
        
        # Extragem URL-ul curent
        product_url = driver.current_url
        print(f"Pagina produsului: {product_url}")
        
        # Căutăm prețul pe pagina produsului
        try:
            price_element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "span.pret-nou"))
            )
            full_price = price_element.text.strip() + " lei"
        except Exception:
            full_price = "Preț indisponibil"
        
    except Exception as e:
        full_price = "Eroare"
    
    print(f"Preț găsit: {full_price}")
    driver.quit()
    return full_price

def main():
    vinyl_list = [
        ("2PAC", "All Eyez On Me"),
        ("The Beatles", "Abbey Road"),
        ("Pink Floyd", "The Dark Side of the Moon"),
        ("Nirvana", "Nevermind"),
        ("AC/DC", "Back in Black")
    ]  # Lista de test, înlocuiește cu cele 500+ de căutări
    
    print("\nRezultate AVstore:")
    for vinyl in vinyl_list:
        price = search_avstore(vinyl[0], vinyl[1])
        print(f"{vinyl[0]} - {vinyl[1]}: {price}")

if __name__ == "__main__":
    main()
