from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import os
import json
from agent import LyricsAgent

app = FastAPI(title="Song Vocabulary Assistant")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request models
class LyricsRequest(BaseModel):
    song_title: str
    artist: str
    language: str = "Japanese"

class VocabularyPart(BaseModel):
    kanji: str
    romaji: List[str]

class VocabularyItem(BaseModel):
    kanji: str
    romaji: str
    english: str
    parts: List[VocabularyPart]

class LyricsResponse(BaseModel):
    song_id: str
    language: str
    lyrics: str
    vocabulary: List[VocabularyItem]
    source_url: str

# Initialize agent
lyrics_agent = LyricsAgent()

@app.post("/api/agent", response_model=LyricsResponse)
async def get_lyrics(request: LyricsRequest):
    try:
        print(f"[API] Received request for song: {request.song_title} by {request.artist}")
        
        # Call agent to process the request
        print("[API] Calling lyrics agent...")
        result = lyrics_agent.process_request(
            song_title=request.song_title,
            artist=request.artist,
            language=request.language
        )
        print(f"[API] Agent returned result: {result}")
        
        # Check if the result indicates an error
        if isinstance(result, str) and result.startswith("Error:"):
            print(f"[API] Error from agent: {result}")
            raise HTTPException(status_code=500, detail=result)
            
        if not result or not isinstance(result, dict):
            print("[API] Invalid result format from agent")
            raise HTTPException(status_code=500, detail="Invalid result format from agent")
            
        if 'error' in result:
            print(f"[API] Error in result: {result['error']}")
            raise HTTPException(status_code=500, detail=result['error'])
            
        if 'final_response' not in result:
            print("[API] Missing final_response in result")
            raise HTTPException(status_code=500, detail="Missing final response data")
            
        # Return the full response data
        return JSONResponse(content=result['final_response'], media_type="application/json")
        
    except Exception as e:
        print(f"[API] Exception type: {type(e)}")
        print(f"[API] Exception args: {e.args}")
        print(f"[API] Full exception: {str(e)}")
        print(f"[API] API Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"API Error: {str(e)}")
        
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
