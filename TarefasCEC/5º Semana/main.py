from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()

contador = 0

templates = Jinja2Templates(directory=["Templates", "Templates/Partials"])

@app.get("/",response_class=HTMLResponse)
async def root(request: Request):
    
    return templates.TemplateResponse(request, "index.html", {"contador": "0"})


@app.post("/curtir", response_class=HTMLResponse)
async def curtir(request : Request):
    global contador
    contador+=1
    if (not "HX-Request" in request.headers):
        return templates.TemplateResponse(request, "index.html")
    return str(contador)

