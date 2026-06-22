from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, movies, watchlist, reviews

app = FastAPI(title="SeenIt API")

# pozwól frontendowi (inny adres) wołać API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],   # dopisz tu adres frontendu z homelaba
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

# prosty sygnał, że API żyje
@app.get("/health")
def health():
    return {"status": "ok"}

# podłącz grupy endpointów
app.include_router(auth.router)
app.include_router(movies.router)
app.include_router(watchlist.router)
app.include_router(reviews.router)