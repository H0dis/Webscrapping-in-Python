import time
import multiprocessing
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

HEADLESS_MODE = False
WAIT_SHORT = 1
WAIT_MEDIUM = 2
WAIT_LONG = 3

def setup_browser():
    options = webdriver.ChromeOptions()
    if HEADLESS_MODE:
        options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

def search_carturesti(album, driver):
    driver.get("https://carturesti.ro/")
    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "search-input"))).send_keys(album + Keys.RETURN)
        time.sleep(WAIT_MEDIUM)
        product_element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "productPrice")))
        price_main = product_element.find_element(By.CLASS_NAME, "suma").text.strip()
        price_cents = product_element.find_element(By.CLASS_NAME, "bani").text.strip()
        return (album, f"{price_main}.{price_cents} lei (Carturesti)")
    except Exception:
        return (album, "Eroare sau Preț indisponibil")

def search_avstore(album, driver):
    driver.get("https://www.avstore.ro/viniluri/")
    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.NAME, "q"))).send_keys(album + Keys.RETURN)
        time.sleep(WAIT_MEDIUM)
        price_element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "span.pret-nou")))
        return (album, price_element.text.strip() + " lei (AVstore)")
    except Exception:
        return (album, "Eroare sau Preț indisponibil")

def search_melomelanj(album, driver):
    driver.get("https://melomelanj.ro/")
    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input.navbar-search-input"))).send_keys(album + Keys.RETURN)
        time.sleep(WAIT_LONG)
        driver.execute_script("window.scrollBy(0, 1000);")
        products = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.product")))
        for product in products:
            try:
                title = product.find_element(By.CSS_SELECTOR, "h2.woocommerce-loop-product__title").text.strip()
                if album.lower() in title.lower():
                    price = product.find_element(By.CSS_SELECTOR, "span.woocommerce-Price-amount bdi").text.strip()
                    return (album, price + " (Melomelanj)")
            except:
                continue
        return (album, "Preț indisponibil")
    except Exception:
        return (album, "Eroare")

def search_musicbox(album, driver):
    driver.get("https://music-box.ro/")
    try:
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.search-trigger"))).click()
        time.sleep(WAIT_SHORT)
        box = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input.search-input.tt-input")))
        box.clear()
        box.send_keys(album)
        time.sleep(WAIT_MEDIUM)
        link = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.search-result.tt-suggestion a"))).get_attribute("href")
        driver.get(link)
        time.sleep(WAIT_MEDIUM)
        price = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.price-group div.product-price")))
        return (album, price.text.strip() + " (Music-Box)")
    except Exception:
        return (album, "Eroare sau Preț indisponibil")

def process_site(site_function, album):
    driver = setup_browser()
    result = site_function(album, driver)
    driver.quit()
    return result

def main():
    df = pd.read_excel("Searchrecords.xlsx", sheet_name="Sheet1")
    vinyl_list = [f"{row[1]} {row[2]}" for row in df.itertuples(index=False) if not pd.isna(row[1]) and not pd.isna(row[2])]

    with multiprocessing.Pool(processes=4) as pool:
        carturesti_results = pool.starmap(process_site, [(search_carturesti, album) for album in vinyl_list])
        avstore_results = pool.starmap(process_site, [(search_avstore, album) for album in vinyl_list])
        melomelanj_results = pool.starmap(process_site, [(search_melomelanj, album) for album in vinyl_list])
        musicbox_results = pool.starmap(process_site, [(search_musicbox, album) for album in vinyl_list])

    print("Rezultate finale:")
    for result in carturesti_results + avstore_results + melomelanj_results + musicbox_results:
        print(f"{result[0]}: {result[1]}")

if __name__ == "__main__":
    main()
