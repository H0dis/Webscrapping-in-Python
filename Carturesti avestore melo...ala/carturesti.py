import time
import multiprocessing
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

def search_carturesti(artist, album):
    driver = setup_browser()  # Fiecare proces își creează WebDriver-ul propriu
    search_query = f"{artist} {album}"
    search_url = "https://carturesti.ro/"
    
    try:
        driver.get(search_url)
        time.sleep(1)
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "search-input"))
        )
        
        search_box = driver.find_element(By.ID, "search-input")
        search_box.clear()
        search_box.send_keys(search_query)
        search_box.send_keys(Keys.RETURN)
        
        time.sleep(3)  # Reducem timpul de așteptare
        
        # Verificăm dacă există produse
        try:
            product_element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "productPrice"))
            )
            
            price_main = product_element.find_element(By.CLASS_NAME, "suma").text.strip()
            price_cents = product_element.find_element(By.CLASS_NAME, "bani").text.strip()
            full_price = f"{price_main}.{price_cents} lei".replace(".00.00", ".00").replace(".99.99", ".99").replace(".59.59", ".59").replace("..", ".")
        except Exception:
            full_price = "Preț indisponibil"
        
    except Exception as e:
        full_price = "Eroare"
    
    driver.quit()  # Închidem WebDriver-ul după fiecare proces
    return (artist, album, full_price)

def main():
    vinyl_list = [
        ("2PAC", "All Eyez On Me"),
        ("The Beatles", "Abbey Road"),
       
    ]  # Lista de test, înlocuiește cu cele 500+ de căutări
    
    with multiprocessing.Pool(processes=4) as pool:
        results = pool.starmap(search_carturesti, vinyl_list)
    
    print("\nRezultate finale:")
    for result in results:
        print(f"{result[0]} - {result[1]}: {result[2]}")

if __name__ == "__main__":
    main()
