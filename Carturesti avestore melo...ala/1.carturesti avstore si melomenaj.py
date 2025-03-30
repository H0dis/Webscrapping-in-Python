import time
import multiprocessing
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

#  browserul să fie vizibil sau să ruleze în fundal
HEADLESS_MODE = False  # Setează pe True pentru a rula în fundal (mai rapid)

def setup_browser():
    """ Inițializează browserul Chrome cu opțiunile necesare. """
    options = webdriver.ChromeOptions()
    
    if HEADLESS_MODE:
        options.add_argument("--headless")  # Rularea în fundal
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    return driver

def search_carturesti(album, driver):
    """ Caută un album pe Cărturești și returnează prețul. """
    search_url = "https://carturesti.ro/"
    
    try:
        driver.get(search_url)
        time.sleep(1)
        
        search_box = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "search-input"))
        )
        search_box.clear()
        search_box.send_keys(album)
        search_box.send_keys(Keys.RETURN)
        
        time.sleep(2)
        
        try:
            product_element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "productPrice"))
            )
            price_main = product_element.find_element(By.CLASS_NAME, "suma").text.strip()
            price_cents = product_element.find_element(By.CLASS_NAME, "bani").text.strip()
            full_price = f"{price_main}.{price_cents} lei (Cărturești)"
        except Exception:
            full_price = "Preț indisponibil"
    
    except Exception:
        full_price = "Eroare"
    
    return (album, full_price)

def search_avstore(album, driver):
    """ Caută un album pe AVstore și returnează prețul. """
    search_url = "https://www.avstore.ro/viniluri/"
    
    driver.get(search_url)
    time.sleep(2)
    
    try:
        search_box = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.NAME, "q"))
        )
        search_box.clear()
        search_box.send_keys(album)
        search_box.send_keys(Keys.RETURN)
        
        time.sleep(3)
        
        try:
            price_element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "span.pret-nou"))
            )
            full_price = price_element.text.strip() + " lei (AVstore)"
        except Exception:
            full_price = "Preț indisponibil"
    
    except Exception:
        full_price = "Eroare"
    
    return (album, full_price)

def search_melomelanj(album, driver):
    """ Caută un album pe Melomelanj și returnează prețul. """
    search_url = "https://melomelanj.ro/"
    
    driver.get(search_url)
    time.sleep(2)
    
    try:
        search_box = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input.navbar-search-input"))
        )
        search_box.clear()
        search_box.send_keys(album)
        search_box.send_keys(Keys.RETURN)
        
        time.sleep(3)
        
        # Derulăm pagina în jos pentru a vedea produsele
        driver.execute_script("window.scrollBy(0, 1000);")  
        time.sleep(2)

        product_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.product"))
        )

        for product in product_elements:
            try:
                title_element = product.find_element(By.CSS_SELECTOR, "h2.woocommerce-loop-product__title")
                product_title = title_element.text.strip()

                if album.lower() in product_title.lower():
                    try:
                        price_element = product.find_element(By.CSS_SELECTOR, "span.woocommerce-Price-amount bdi")
                        full_price = price_element.text.strip() + " (Melomelanj)"
                        return (album, full_price)
                    except:
                        return (album, "Preț indisponibil")
            except:
                continue
    except Exception:
        return (album, "Eroare")
    
    return (album, "Preț indisponibil")

def process_site(site_function, album):
    """ Procesează căutarea pentru un site folosind un browser unic per proces. """
    driver = setup_browser()  # Inițializăm browserul o singură dată pentru proces
    result = site_function(album, driver)
    driver.quit()  # Închidem browserul după ce am terminat
    return result

def main():
    """ Execută căutările în paralel pentru toate site-urile și albumele. """
    vinyl_list = [
        "All Eyez On Me",
        "Abbey Road",
        "The Dark Side of the Moon",
        "Nevermind",
        "Back in Black"
    ]
    
    with multiprocessing.Pool(processes=3) as pool:
        carturesti_results = pool.starmap(process_site, [(search_carturesti, album) for album in vinyl_list])
        avstore_results = pool.starmap(process_site, [(search_avstore, album) for album in vinyl_list])
        melomelanj_results = pool.starmap(process_site, [(search_melomelanj, album) for album in vinyl_list])
    
    print("\n🔹 Rezultate finale:")
    for result in carturesti_results + avstore_results + melomelanj_results:
        print(f"{result[0]}: {result[1]}")

if __name__ == "__main__":
    main()
