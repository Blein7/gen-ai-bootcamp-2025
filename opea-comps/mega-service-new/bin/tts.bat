@echo off
setlocal EnableDelayedExpansion

set "input=%~1"
if "%input%"=="" (
    echo Usage: tts "Your text here" [voice]
    echo Example: tts "Hello, how are you?" male
    exit /b 1
)

set "voice=%~2"
if "%voice%"=="" set "voice=male"

curl http://localhost:9088/v1/audio/speech -XPOST -d "{\"input\":\"%input%\", \"voice\": \"%voice%\"}" -H "Content-Type: application/json" --output speech.wav

if %ERRORLEVEL% EQU 0 (
    echo Speech generated successfully as speech.wav
) else (
    echo Error generating speech
)
