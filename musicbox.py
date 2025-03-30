import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

# Setare pentru rulare vizuală sau în fundal
HEADLESS_MODE = False

def setup_browser():
    options = webdriver.ChromeOptions()
    if HEADLESS_MODE:
        options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def search_musicbox(artist, album):
    driver = setup_browser()
    search_url = "https://music-box.ro/"
    driver.get(search_url)
    time.sleep(2)

    try:
        # Activează bara de căutare ascunsă
        search_trigger = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.search-trigger"))
        )
        search_trigger.click()
        time.sleep(1)

        # Introduce căutarea în câmpul activ (cu strip pentru a evita spațiile în plus)
        search_box = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input.search-input.tt-input"))
        )
        search_box.clear()
        search_box.send_keys(f"{artist} {album}".strip())
        time.sleep(2)

        # Așteaptă ca rezultatele să apară și accesează primul rezultat
        first_result = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div.search-result.tt-suggestion a"))
        )
        product_url = first_result.get_attribute("href")
        print("Accesez:", product_url)
        driver.get(product_url)
        time.sleep(2)

        # Caută prețul în pagina produsului
        try:
            price_elem = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.price-group div.product-price"))
            )
            full_price = price_elem.text.strip()
        except Exception:
            full_price = "Preț indisponibil"

    except Exception as e:
        print(f"Eroare: {e}")
        full_price = "Eroare"

    driver.quit()
    return (artist, album, full_price)

def main():
    vinyl_list = [
        ("All Eyez On Me", ""),
        ("Abbey Road", ""),
    ]

    results = []
    for vinyl in vinyl_list:
        results.append(search_musicbox(*vinyl))

    print("\nRezultate Music-Box:")
    for result in results:
        print(f"{result[0]} - {result[1]}: {result[2]}")

if __name__ == "__main__":
    main()
