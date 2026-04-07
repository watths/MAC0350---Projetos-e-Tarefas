from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI()

contador = 0

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory=["Templates", "Templates/Partials"])

@app.get("/",response_class=HTMLResponse)
async def root(request: Request):
    
    return templates.TemplateResponse(request, "index.html")


@app.post("/curtir", response_class=HTMLResponse)
async def curtir(request : Request):
    global contador
    contador+=1
    if (not "HX-Request" in request.headers):
        return templates.TemplateResponse(request, "index.html")
    return str(contador)

@app.put("/zerar", response_class=HTMLResponse)
async def zerar(request : Request):
    global contador
    contador=0
    if (not "HX-Request" in request.headers):
        return templates.TemplateResponse(request, "index.html")
    return str(contador)

@app.get("/curtidas", response_class=HTMLResponse)
async def curtidas(request : Request):
    global contador
    return templates.TemplateResponse(request, "contador.html",  {"contador": contador, "ativo": 'curtidas'})

@app.get("/professor", response_class=HTMLResponse)
async def prof(request : Request):
    return templates.TemplateResponse(request, "paginaprofessor.html", {"ativo": 'professor'})

@app.get("/jupiter", response_class=HTMLResponse)
async def jup(request : Request):
    return templates.TemplateResponse(request, "jupiter.html", {"ativo": 'jupiter'})
