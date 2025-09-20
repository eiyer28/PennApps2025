from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import Query
from fastapi.responses import JSONResponse
import requests

import uvicorn

app = FastAPI()

# Mount static directory (if needed for assets)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up templates directory
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
	return templates.TemplateResponse("index.html", {"request": request})

# --- COUNTRIES ENDPOINT ---
@app.get("/search_countries")
async def search_countries():
    try:
        response = requests.get("https://v17.api.carbonmark.com/countries")
        response.raise_for_status()
        data = response.json()
        # Unpack the JSON to return a list of country names
        countries = [country["id"] for country in data]
        return JSONResponse(content={"countries": countries})
    except requests.RequestException as e:
        return JSONResponse(content={"error": "Failed to fetch countries"}, status_code=500)
    
# --- METHODOLOGIES ENDPOINT ---
@app.get("/search_categories")
async def search_categories():
    try:
        response = requests.get("https://v17.api.carbonmark.com/categories")
        response.raise_for_status()
        data = response.json()
        # Unpack the JSON to return a list of category names
        categories = [category["id"] for category in data]
        return JSONResponse(content={"categories": categories})
    except requests.RequestException as e:
        return JSONResponse(content={"error": "Failed to fetch categories"}, status_code=500)

# --- SEARCH ENDPOINT ---
@app.get("/search")
async def search_projects(
	country: str = Query(None),
	methodology: str = Query(None),
	name: str = Query(None)
    ):
	parameters = {"limit": 100}
	if country: parameters['country'] = country
	if methodology: parameters['category'] = methodology
	if name: parameters['name'] = name
	# Stub: return dummy data
	result = requests.get("https://v17.api.carbonmark.com/carbonProjects", params=parameters)

	return JSONResponse(content=result.json())



if __name__ == "__main__":
	uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
