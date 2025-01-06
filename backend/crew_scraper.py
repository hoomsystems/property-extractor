from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
import os

class PropertyCrewScraper:
    def __init__(self, api_key):
        self.api_key = api_key
        os.environ["OPENAI_API_KEY"] = api_key
        
        # Crear agentes especializados
        self.bypass_agent = Agent(
            role='Bypass Specialist',
            goal='Evadir detección de Cloudflare y sistemas anti-bot',
            backstory='Experto en evasión de sistemas de seguridad web y manejo de sesiones',
            allow_delegation=False,
            llm=ChatOpenAI(model='gpt-4')
        )
        
        self.scraper_agent = Agent(
            role='Data Extractor',
            goal='Extraer información detallada de propiedades inmobiliarias',
            backstory='Especialista en extracción y análisis de datos inmobiliarios',
            allow_delegation=True,
            llm=ChatOpenAI(model='gpt-4')
        )
        
        self.validator_agent = Agent(
            role='Data Validator',
            goal='Validar y estructurar la información extraída',
            backstory='Experto en validación y normalización de datos inmobiliarios',
            allow_delegation=True,
            llm=ChatOpenAI(model='gpt-4')
        )
    
    def scrape(self, url):
        # Definir tareas
        bypass_task = Task(
            description=f"Acceder a {url} evadiendo sistemas de seguridad",
            agent=self.bypass_agent
        )
        
        extract_task = Task(
            description="Extraer datos de la propiedad incluyendo precio, ubicación, características",
            agent=self.scraper_agent
        )
        
        validate_task = Task(
            description="Validar y estructurar los datos extraídos",
            agent=self.validator_agent
        )
        
        # Crear y ejecutar el crew
        crew = Crew(
            agents=[self.bypass_agent, self.scraper_agent, self.validator_agent],
            tasks=[bypass_task, extract_task, validate_task],
            verbose=True
        )
        
        result = crew.kickoff()
        return result 