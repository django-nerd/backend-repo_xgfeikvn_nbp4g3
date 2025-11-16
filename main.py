import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from bson import ObjectId

from database import create_document, get_documents, db
from schemas import Lead

app = FastAPI(title="PlumberPro API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "PlumberPro Backend Running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    return response

class LeadResponse(BaseModel):
    id: str

@app.post("/api/leads", response_model=LeadResponse)
async def create_lead(lead: Lead):
    try:
        inserted_id = create_document("lead", lead)
        return {"id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/services")
def get_services():
    services = [
        {
            "id": "emergency",
            "title": "24/7 Emergency Plumbing",
            "description": "Rapid response for leaks, bursts, and urgent repairs.",
            "icon": "zap"
        },
        {
            "id": "drain",
            "title": "Drain Cleaning",
            "description": "Clogged drains cleared fast with professional equipment.",
            "icon": "pipe"
        },
        {
            "id": "water-heater",
            "title": "Water Heater Repair & Install",
            "description": "Tank and tankless systems serviced and installed.",
            "icon": "flame"
        },
        {
            "id": "leak-detection",
            "title": "Leak Detection",
            "description": "Pinpoint hidden leaks with non-invasive diagnostics.",
            "icon": "droplet"
        }
    ]
    return {"services": services}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
