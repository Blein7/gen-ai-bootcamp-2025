@echo off
curl -X POST http://localhost:8000/v1/chat/completions ^
-H "Content-Type: application/json" ^
-d "{\"model\":\"gpt-3.5-turbo\",\"messages\":[{\"role\":\"user\",\"content\":\"Hello\"}],\"temperature\":0.7}"
pause
