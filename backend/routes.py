from fastapi import APIRouter, HTTPException
from .scraper import PropertyScraper

router = APIRouter()
scraper = PropertyScraper()

@router.get("/scrape")
async def scrape_property(url: str):
    try:
        data = scraper.scrape(url)
        return {
            "status": "success",
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 