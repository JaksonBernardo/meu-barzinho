from fastapi import FastAPI, status
from api.core.settings import Settings
from fastapi.middleware.cors import CORSMiddleware
from api.routers import auth, users, companies, clients


app = FastAPI()

origins = [
    Settings().URL_CORS,
]

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"]
)

app.include_router(auth.router)
app.include_router(companies.router)
app.include_router(users.router)
app.include_router(clients.router)



@app.get(
    path = "/api/health",
    status_code = status.HTTP_200_OK,
    summary = "Verificando status da API...",
    tags = ["Health API"]
)
def health_check(): return {"status": "OK.."}
