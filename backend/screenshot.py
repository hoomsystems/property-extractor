from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

def capture_full_page(url):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--start-maximized')
    
    driver = webdriver.Chrome(options=options)
    try:
        driver.get(url)
        time.sleep(5)  # Esperar a que cargue la página
        
        # Obtener altura total
        total_height = driver.execute_script("return document.body.scrollHeight")
        
        # Configurar ventana
        driver.set_window_size(1920, total_height)
        
        # Tomar screenshot
        screenshot = driver.get_screenshot_as_png()
        return screenshot
    finally:
        driver.quit() 