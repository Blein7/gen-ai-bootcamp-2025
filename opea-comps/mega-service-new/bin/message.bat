@echo off
curl -X POST ^
  http://localhost:8000/james-is-great ^
  -H "Content-Type: application/json" ^
  -d "{\"model\":\"llama3.2:1b\",\"messages\":[{\"role\":\"user\",\"content\":\"Hello, how are you?\"}],\"temperature\":0.7,\"max_tokens\":100}"
