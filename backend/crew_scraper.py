from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
from langchain.tools import tool
import requests
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import os
import time

class PropertyCrewScraper:
    def __init__(self, api_key):
        self.api_key = api_key
        os.environ["OPENAI_API_KEY"] = api_key
        
    @tool
    def fetch_webpage(self, url: str) -> str:
        """Fetch a webpage content using undetected-chromedriver."""
        try:
            options = uc.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            driver = uc.Chrome(options=options)
            
            print(f"Accessing URL: {url}")
            driver.get(url)
            time.sleep(10)
            
            content = driver.page_source
            driver.quit()
            return content
        except Exception as e:
            return f"Error fetching webpage: {str(e)}"

    @tool
    def extract_property_data(self, html_content: str) -> dict:
        """Extract property information from HTML content."""
        try:
            # Implementar extracción básica
            data = {
                "price": self._extract_price(html_content),
                "location": self._extract_location(html_content),
                "description": self._extract_description(html_content)
            }
            return data
        except Exception as e:
            return f"Error extracting data: {str(e)}"

    def scrape(self, url):
        # Crear agentes con herramientas específicas
        bypass_agent = Agent(
            role='Bypass Specialist',
            goal='Evadir detección de Cloudflare y sistemas anti-bot',
            backstory='Experto en evasión de sistemas de seguridad web y manejo de sesiones',
            tools=[self.fetch_webpage],
            verbose=True,
            llm=ChatOpenAI(model='gpt-4')
        )
        
        scraper_agent = Agent(
            role='Data Extractor',
            goal='Extraer información detallada de propiedades inmobiliarias',
            backstory='Especialista en extracción y análisis de datos inmobiliarios',
            tools=[self.extract_property_data],
            verbose=True,
            llm=ChatOpenAI(model='gpt-4')
        )
        
        # Definir tareas
        bypass_task = Task(
            description=f"Acceder a {url} evadiendo sistemas de seguridad. Retornar el contenido HTML.",
            agent=bypass_agent
        )
        
        extract_task = Task(
            description="Analizar el HTML y extraer datos estructurados de la propiedad.",
            agent=scraper_agent
        )
        
        # Crear y ejecutar el crew
        crew = Crew(
            agents=[bypass_agent, scraper_agent],
            tasks=[bypass_task, extract_task],
            verbose=True
        )
        
        result = crew.kickoff()
        return result

    def _extract_price(self, html):
        # Implementar extracción de precio
        return "Precio pendiente"

    def _extract_location(self, html):
        # Implementar extracción de ubicación
        return "Ubicación pendiente"

    def _extract_description(self, html):
        # Implementar extracción de descripción
        return "Descripción pendiente" 