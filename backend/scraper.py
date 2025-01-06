import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
import os
from datetime import datetime

class PropertyScraper:
    def __init__(self):
        self.options = uc.ChromeOptions()
        self.options.add_argument('--headless')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        
        # Crear directorio para debug si no existe
        self.debug_dir = '/var/www/proyectos/hoomextractor/debug'
        os.makedirs(self.debug_dir, exist_ok=True)

    def scrape(self, url):
        driver = uc.Chrome(options=self.options)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        try:
            print(f"Iniciando scraping de: {url}")
            driver.get(url)
            
            # Esperar más tiempo y verificar que la página cargó
            time.sleep(20)
            
            # Guardar el HTML para debug
            debug_html = os.path.join(self.debug_dir, f'debug_page_{timestamp}.html')
            with open(debug_html, 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            print(f"HTML guardado en: {debug_html}")
            
            # Guardar screenshot inicial
            screenshot_path = os.path.join(self.debug_dir, f'page_{timestamp}.png')
            driver.save_screenshot(screenshot_path)
            print(f"Screenshot guardado en: {screenshot_path}")
            
            print("Página cargada, verificando contenido...")
            page_text = driver.page_source.lower()
            
            # Verificar si estamos en la página correcta
            if "cloudflare" in page_text:
                print("Detectada protección de Cloudflare, esperando...")
                time.sleep(15)
            elif "robot" in page_text or "captcha" in page_text:
                print("Detectada página de verificación, esperando...")
                time.sleep(15)
            
            print("Extrayendo datos...")
            
            # Intentar extraer datos con diferentes métodos
            data = {
                'url': url,
                'html_length': len(driver.page_source),
                'page_title': driver.title,
                'data_found': {}
            }
            
            # Extraer datos con manejo de errores individual
            try:
                data['title'] = self._get_title(driver)
                data['data_found']['title'] = True
            except Exception as e:
                print(f"Error al extraer título: {str(e)}")
                data['data_found']['title'] = False
            
            try:
                data['price'] = self._get_price(driver)
                data['data_found']['price'] = True
            except Exception as e:
                print(f"Error al extraer precio: {str(e)}")
                data['data_found']['price'] = False
            
            try:
                data['location'] = self._get_location(driver)
                data['data_found']['location'] = True
            except Exception as e:
                print(f"Error al extraer ubicación: {str(e)}")
                data['data_found']['location'] = False
            
            try:
                data['description'] = self._get_description(driver)
                data['data_found']['description'] = True
            except Exception as e:
                print(f"Error al extraer descripción: {str(e)}")
                data['data_found']['description'] = False
            
            try:
                data['features'] = self._get_features(driver)
                data['data_found']['features'] = True
            except Exception as e:
                print(f"Error al extraer características: {str(e)}")
                data['data_found']['features'] = False
            
            try:
                data['images'] = self._get_images(driver)
                data['data_found']['images'] = True
            except Exception as e:
                print(f"Error al extraer imágenes: {str(e)}")
                data['data_found']['images'] = False
            
            print("Datos extraídos:", data)
            return data
            
        except Exception as e:
            print(f"Error durante el scraping: {str(e)}")
            # Guardar screenshot de error
            error_screenshot = os.path.join(self.debug_dir, f'error_{timestamp}.png')
            try:
                driver.save_screenshot(error_screenshot)
                print(f"Screenshot de error guardado en: {error_screenshot}")
            except:
                print("No se pudo guardar el screenshot de error")
            raise
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
        try:
            print("Intentando obtener ubicación...")
            
            # Esperar a que la página cargue completamente
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Imprimir el título y URL actual para debug
            print(f"Título de la página: {driver.title}")
            print(f"URL actual: {driver.current_url}")
            
            # Guardar el HTML actual para debug
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            debug_html = os.path.join(self.debug_dir, f'location_debug_{timestamp}.html')
            with open(debug_html, 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            print(f"HTML guardado en: {debug_html}")
            
            # Tomar screenshot específico para debug de ubicación
            location_screenshot = os.path.join(self.debug_dir, f'location_{timestamp}.png')
            driver.save_screenshot(location_screenshot)
            print(f"Screenshot guardado en: {location_screenshot}")
            
            # Resto del código igual...
            
            # Intentar diferentes estrategias de XPath
            location_xpaths = [
                # Buscar por texto en etiquetas
                "//*[contains(text(), 'Ubicado en') or contains(text(), 'Ubicación')]/following-sibling::*",
                "//*[contains(text(), 'Dirección') or contains(text(), 'Colonia')]/following-sibling::*",
                
                # Buscar por atributos comunes
                "//*[@data-qa='POSTING_CARD_LOCATION']",
                "//*[contains(@class, 'location') or contains(@class, 'ubicacion')]",
                "//*[contains(@class, 'address') or contains(@class, 'direccion')]",
                
                # Buscar por estructura común de inmuebles24
                "//div[contains(@class, 'posting-location')]",
                "//div[contains(@class, 'location-container')]",
                
                # Buscar por metadatos
                "//*[@itemprop='address']",
                "//*[@property='og:street-address']"
            ]
            
            # Intentar cada XPath
            for xpath in location_xpaths:
                try:
                    print(f"Probando XPath: {xpath}")
                    elements = driver.find_elements(By.XPATH, xpath)
                    if elements:
                        location = elements[0].text.strip()
                        print(f"Ubicación encontrada: {location}")
                        return location
                except Exception as e:
                    print(f"Error con XPath {xpath}: {str(e)}")
                    continue
            
            # Si no encontramos nada con XPath, intentar buscar en el HTML
            print("Intentando búsqueda en HTML completo...")
            html = driver.page_source.lower()
            location_patterns = [
                r'ubicado en[:\s]+([^\.]+)',
                r'ubicación[:\s]+([^\.]+)',
                r'dirección[:\s]+([^\.]+)',
                r'colonia[:\s]+([^\.]+)',
                r'(?:calle|avenida|av\.|blvd\.)[:\s]+([^\.]+)'
            ]
            
            for pattern in location_patterns:
                match = re.search(pattern, html)
                if match:
                    location = match.group(1).strip()
                    print(f"Ubicación encontrada por patrón: {location}")
                    return location
            
            print("No se encontró ubicación")
            return "Ubicación no encontrada"
            
        except Exception as e:
            print(f"Error al obtener ubicación: {str(e)}")
            return "Error al obtener ubicación"

    def _get_description(self, driver):
        try:
            # Lista de selectores para descripción
            description_selectors = [
                '[class*="description"]',
                '[class*="descripcion"]',
                '[itemprop="description"]',
                '[class*="detail"]',
                # Selectores específicos de inmuebles24
                '[data-qa="POSTING_DESCRIPTION"]',
                '.posting-description',
                '#description-container'
            ]
            
            # Intentar cada selector
            for selector in description_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        return elements[0].text.strip()
                except:
                    continue
            
            return "Descripción no encontrada"
        except Exception as e:
            print(f"Error al obtener descripción: {str(e)}")
            return "Error al obtener descripción" 