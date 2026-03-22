
from fastapi import FastAPI, Request,Depends, HTTPException, status, Cookie, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Annotated

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

class Usuario(BaseModel):
    nome: str
    senha: str
    bio: str

usuarios_db = []

@app.get("/")
def login1(request: Request):
    return templates.TemplateResponse(
        request=request, name="perfil.html"
    )

@app.post("/usuarios")
def criar_usuario(user: Usuario):
    usuarios_db.append(user.dict())
    return {"usuario": user.nome}

@app.get("/login")
def login(request: Request):
    return templates.TemplateResponse(
        request=request, name="login.html"
    )

@app.post("/login")
def login(username: str, response: Response):

    usuario_encontrado = None
    for u in usuarios_db:
        if u["nome"] == username:
            usuario_encontrado = u
            break
    
    if not usuario_encontrado:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    response.set_cookie(key="session_user", value=username)
    return {"message": "Logado com sucesso"}

def get_active_user(session_user: Annotated[str | None, Cookie()] = None):

    if not session_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Acesso negado: você não está logado."
        )
    
    user = next((u for u in usuarios_db if u["nome"] == session_user), None)
    if not user:
        raise HTTPException(status_code=401, detail="Sessão inválida")
    
    return user

# 3. Rota Protegida
@app.get("/home")
def show_profile(request: Request, user: dict = Depends(get_active_user)):
    return templates.TemplateResponse(
        request=request, 
        name="profile.html", 
        context={"nome": user["nome"], "bio": user["bio"]}
    )
