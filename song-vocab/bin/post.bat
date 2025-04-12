@echo off
curl -X POST http://localhost:8004/api/agent ^
-H "Content-Type: application/json" ^
-d "{\"song_title\": \"Lemon\", \"artist\": \"Kenshi Yonezu\", \"language\": \"Japanese\"}"
