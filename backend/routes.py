from fastapi import APIRouter, HTTPException
from .crew_scraper import PropertyCrewScraper
import os

router = APIRouter()
scraper = PropertyCrewScraper(api_key=os.getenv('OPENAI_API_KEY'))

@router.get("/api/scrape")
async def scrape_property(url: str):
    try:
        result = scraper.scrape(url)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 