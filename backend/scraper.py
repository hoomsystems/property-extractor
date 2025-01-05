from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class PropertyScraper:
    def __init__(self):
        self.options = Options()
        self.options.add_argument('--headless')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--window-size=1920,1080')
        # Importante: usar un User-Agent realista
        self.options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    def scrape(self, url):
        driver = webdriver.Chrome(options=self.options)
        try:
            driver.get(url)
            # Esperar a que la página cargue completamente
            time.sleep(5)  # Esperar que pase la protección de Cloudflare
            
            # Extraer datos
            data = {
                'url': url,
                'title': self._get_title(driver),
                'price': self._get_price(driver),
                'location': self._get_location(driver),
                'description': self._get_description(driver),
                'features': self._get_features(driver),
                'images': self._get_images(driver)
            }
            
            return data
        finally:
            driver.quit()

    def _get_title(self, driver):
        try:
            # Esperar a que el título esté presente
            title = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "h1"))
            )
            return title.text.strip()
        except:
            return driver.title

    def _get_price(self, driver):
        # Buscar precio con patrones comunes
        price_patterns = [
            r'\$[\d,]+\.?\d*',
            r'[\d,]+\s*mil',
            r'[\d,]+\s*mdp',
            r'[\d,]+\s*millones'
        ]
        
        # Buscar en elementos con clases específicas
        price_selectors = [
            '[class*="price"]',
            '[class*="precio"]',
            '[id*="price"]',
            '[id*="precio"]'
        ]
        
        for selector in price_selectors:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            for element in elements:
                text = element.text.strip()
                for pattern in price_patterns:
                    match = re.search(pattern, text)
                    if match:
                        return match.group()
        return ''

    def _get_images(self, driver):
        images = set()
        # Esperar a que las imágenes carguen
        time.sleep(2)
        
        # Buscar imágenes en carruseles y galerías
        selectors = [
            'img[src*="original"]',
            'img[src*="large"]',
            '[class*="gallery"] img',
            '[class*="slider"] img'
        ]
        
        for selector in selectors:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            for img in elements:
                src = img.get_attribute('src') or img.get_attribute('data-src')
                if src:
                    images.add(src)
        
        return list(images)

    def _is_valid_image(self, url):
        return bool(re.search(r'\.(jpg|jpeg|png|webp)($|\?)', url.lower()))

    def _get_features(self, driver):
        features = {
            'rooms': None,
            'bathrooms': None,
            'construction_area': None,
            'land_area': None
        }
        
        # Buscar características en el texto
        text = driver.page_source.lower()
        
        # Patrones para cada característica
        patterns = {
            'rooms': r'(\d+)\s*(?:rec[aá]maras?|habitaciones?|dormitorios?)',
            'bathrooms': r'(\d+)\s*(?:ba[ñn]os?|wc)',
            'construction_area': r'(\d+)\s*m2?\s*(?:construcci[oó]n|construidos?)',
            'land_area': r'(\d+)\s*m2?\s*(?:terreno|lote)'
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, text)
            if match:
                features[key] = int(match.group(1))
        
        return features

    def _get_location(self, driver):
        location_selectors = [
            '[class*="location"]',
            '[class*="address"]',
            '[class*="ubicacion"]',
            '[itemprop="address"]'
        ]
        
        for selector in location_selectors:
            element = driver.find_element(By.CSS_SELECTOR, selector)
            if element:
                return element.text.strip()
        return ''

    def _get_description(self, driver):
        description_selectors = [
            '[class*="description"]',
            '[class*="descripcion"]',
            '[itemprop="description"]',
            '[class*="detail"]'
        ]
        
        for selector in description_selectors:
            element = driver.find_element(By.CSS_SELECTOR, selector)
            if element:
                return element.text.strip()
        return '' 