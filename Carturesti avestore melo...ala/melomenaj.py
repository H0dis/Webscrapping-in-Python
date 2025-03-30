import time
import multiprocessing
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

DEBUG_MODE = True  # 🔥 Schimbă în `False` pentru rulare normală

def setup_browser():
    options = webdriver.ChromeOptions()
    if not DEBUG_MODE:
        options.add_argument("--headless")  # ❌ DOAR în mod non-debug
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def search_melomelanj(album):
    driver = setup_browser()
    search_url = "https://melomelanj.ro/"
    driver.get(search_url)
    time.sleep(2)

    try:
        print("🔍 Pas 1: Căutăm bara de căutare și introducem textul...")
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input.navbar-search-input"))
        )
        search_box.clear()
        search_box.send_keys(album)  # Cautăm DOAR după numele albumului!
        search_box.send_keys(Keys.RETURN)

        time.sleep(3)
        driver.execute_script("window.scrollBy(0, 1000);")  
        time.sleep(2)

        print("🔎 Pas 2: Căutăm produsul corect pe pagină...")
        products = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.product"))
        )
        print(f"🔎 Am găsit {len(products)} produse pe pagină!")

        final_price = "Preț indisponibil"

        for product in products:
            try:
                title_element = product.find_element(By.CSS_SELECTOR, "h2.woocommerce-loop-product__title")
                product_title = title_element.text.strip()
                
                if album.lower() in product_title.lower():  # 🔥 Verificăm doar numele albumului
                    print(f"✅ Produs găsit: {product_title}")

                    # Rescroll pentru a ne asigura că prețul este vizibil
                    driver.execute_script("arguments[0].scrollIntoView();", title_element)
                    time.sleep(2)

                    try:
                        price_element = product.find_element(By.CSS_SELECTOR, "span.woocommerce-Price-amount bdi")
                        full_price = price_element.text.strip() + " RON"
                        print(f"💰 Preț găsit: {full_price}")  

                        if DEBUG_MODE:
                            print("🔵 Debug Mode: Las browserul deschis! Închide manual când vrei.")
                            while True:
                                time.sleep(1)  # Menține fereastra deschisă
                        else:
                            driver.quit()
                        return (album, full_price)

                    except:
                        print("⚠️ Nu am putut extrage prețul!")
                        final_price = "Preț indisponibil"
            except:
                continue

    except Exception as e:
        print(f"⚠️ Eroare la căutare: {e}")
        final_price = "Eroare"
    
    if not DEBUG_MODE:
        driver.quit()
    return (album, final_price)

def main():
    vinyl_list = [
        "All Eyez On Me",  
    ]
    
    with multiprocessing.Pool(processes=1) as pool:
        melomelanj_results = pool.map(search_melomelanj, vinyl_list)
    
    print("\n🔹 Rezultate Melomelanj:")
    for result in melomelanj_results:
        print(f"{result[0]}: {result[1]}")

if __name__ == "__main__":
    main()
