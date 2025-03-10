## Running Ollama Third-Party Service

## Choosing a Model

You can get the model_id that ollama will launch from the Ollama Library.

https://ollama.com/library/llama3.2

eg. LLM_MODEL_ID="llama3.2:1b"

## Getting the Host IP
# Linux
''' sh
sudo apt install net-tools
ifconfig
'''
Alternatively you can Use the following command HOST_IP=$(hostname -I | awk '{print $1}') to fetch your Host IP address
Current port mapped from 0.0.0.0:9000->11434/tcp

## Running Ollama
HOST_IP=$(hostname -I | awk '{print $1}') NO_PROXY=localhost LLM_ENDPOINT_PORT=9000 LLM_MODEL_ID="llama3.2:1b" docker compose up


## Ollama API

Once the Ollama server is running we can make API calls to the ollama API

https://github.com/ollama/ollama/blob/main/docs/api.md

## Download (Pull) a model
curl http://localhost:9000/api/pull -d '{ "model": "llama3.2:1b" }'

## Generate a Request
curl http://localhost:9000/api/generate -d '{ "model": "llama3.2:1b", "prompt": "Why is the sky blue?" }'

## Technical Uncertainty
Q: Does bridge mode mean we can only access Ollama API with another model in the docker compose?

A: No, the host machine will be able to access it

Q: Which port is being mapped 9000->11434

A: In this case 8008 is the port that host machine will access. the other other in the guest port (the port of the service inside container)

Q: If we pass the LLM_MODEL_Id to the ollama server will it download the model when on start?

A: It does not appear so. The ollama CLI might be running multiple APIs so you need to call the /pull API before trying to generate text

Q: Will the model be downloaded in the container? does that mean the ml model will be deleted when the container stops running?

A: The model will download into the container, and vanish when the container stop running. You need to mount a local drive and there is probably more work to be done.

