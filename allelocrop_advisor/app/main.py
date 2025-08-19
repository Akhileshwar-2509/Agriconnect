from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .routers import predict, classify, recommend, optimize, explain, export

app = FastAPI(title="AlleloCrop Advisor", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")

@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Include routers
app.include_router(predict.router)
app.include_router(classify.router)
app.include_router(recommend.router)
app.include_router(optimize.router)
app.include_router(explain.router)
app.include_router(export.router)
