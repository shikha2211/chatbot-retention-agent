# Retention Strategy Agent using ADK

An AI agent that recommends personalized customer retention strategies using Google ADK, FastAPI, and RAG.

###  Features
- Fetches customer data from external API
- Retrieves retention strategies via RAG
- Generates recommendations using LLM
- Exposed as REST API for chatbot integration

###  Prerequisites
- Python 3.11+
- pip package manager
- Basic understanding of REST APIs

###  Setup & Installation


Create a virtual env (only one time ) and activate it everytime you run the app.
Install the dependencies 

```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```


## Running the AGENT as fast API

Run following commands to run the fast api server
```
source .venv/bin/activate
python start_server.py
```

## Docker Build

Build and run
Build: 
`docker build -t retention-agent:latest /Users/lalnegi/Documents/CODE/CHAT_BOT/chat-bot/agents-adk/retention-agent`

Run:
`docker run --rm -p 9000:9000 --env PORT=9000 --env HOST=0.0.0.0 retention-agent:latest`

Optional: mount a .env file
`docker run --rm -p 9000:9000 --env-file /path/to/.env retention-agent:latest`

#### Endpoints
Docs: http://localhost:9000/docs
Chat: http://localhost:9000/api/chat
Health: http://localhost:9000/api/chat/health
Summary
Added `agents-adk/retention-agent/Dockerfile` to containerize and serve the FastAPI app on port 9000 using start_server.py.


###  Troubleshooting
- **Dependency Issues**: Ensure using Python 3.9+ and latest pip
- **API Errors**: Verify mock API/RAG endpoints are accessible
- **ADK Installation**: Check [Google ADK docs](https://github.com/google/agent-development-kit) if package names differ

###  License
MIT License - See [LICENSE](LICENSE)

###  Contribution
Contributions welcome! Please open an issue first to discuss proposed changes.  


###  References 

https://www.youtube.com/watch?v=P4VFL9nIaIA

https://www.youtube.com/watch?v=bPtKnDIVEsg&t=403s 

https://github.com/bhancockio/agent-development-kit-crash-course




##  NOT In use but for reference : 

#### for Running ADK Web 
NOTE: every time run : 
```
source .venv/bin/activate 

adk web
```




