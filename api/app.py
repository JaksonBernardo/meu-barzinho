from fastapi import FastAPI, status
from api.core.settings import Settings
from fastapi.middleware.cors import CORSMiddleware
from api.routers import auth, users, companies, clients, categories, items, entries, exits, orders, stock


app = FastAPI()

origins = [
    "http://127.0.0.1:4200",
    "http://localhost:4200"
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
app.include_router(categories.router)
app.include_router(items.router)
app.include_router(entries.router)
app.include_router(exits.router)
app.include_router(orders.router)
app.include_router(stock.router)




@app.get(
    path = "/api/health",
    status_code = status.HTTP_200_OK,
    summary = "Verificando status da API...",
    tags = ["Health API"]
)
def health_check(): return {"status": "OK.."}
