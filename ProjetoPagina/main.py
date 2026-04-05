
# imports necessários para o funcionamento do projeto

from fastapi import FastAPI, Request,Depends, HTTPException, status, Cookie, Response, Form
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Annotated
from sqlmodel import SQLModel, create_engine, Session, select
from models import Usuario, Email, RespostaEmail

# setup do Fastapi 
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# setup do SQL
arquivo_sqlite = "database.db"
url_sqlite = f"sqlite:///{arquivo_sqlite}"
engine = create_engine(url_sqlite)

def create_db():
    SQLModel.metadata.create_all(engine)

@app.on_event("startup")
def on_startup() -> None:
    create_db()

# rota root que abre a página de login
@app.get("/")
def login(request : Request):
    return templates.TemplateResponse(
        request=request, name="login.html"
    )

# rota para abertura da página de criação de contas
@app.get("/criarcontahtml", response_class=HTMLResponse)
def criarcontahtml(request: Request):
    return templates.TemplateResponse(
        request=request, name="criarconta.html"
    )
    
# rota para criação de contas no banco de dados
@app.post("/usuarios")
def criar_usuario(user : Usuario):
    with Session(engine) as session:
        
        busca = session.exec(select(Usuario).where(Usuario.email == user.email)).first()
        if busca:
            raise HTTPException(status_code=404, detail="Email já existente.")

        session.add(user)
        session.commit()
        session.refresh(user)
        
    return {"usuario": user.email}

# rota para logar e setar o cookie
@app.post("/login")
def logar(email: str, senha: str, response: Response):

    with Session(engine) as session:
        user = select(Usuario).where(Usuario.email == email)
        usuario_encontrado = session.exec(user).first()
        
        if not usuario_encontrado:
            raise HTTPException(status_code=404, detail="Email não encontrado")
        
        if usuario_encontrado.senha != senha:
            raise HTTPException(status_code=404, detail="Senha incorreta")
        
        response.set_cookie(key="session_user", value=email)
        return {"message": "Logado com sucesso"}

# função auxiliar que captura o usuário logado no cookie
def get_active_user(session_user: Annotated[str | None, Cookie()] = None):

    if not session_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Acesso negado: você não está logado."
        )

    with Session(engine) as session:
        busca = select(Usuario).where(Usuario.email == session_user)
        user = session.exec(busca).first()

        if not user:
            raise HTTPException(status_code=401, detail="Sessão inválida")

        return user

# rota para o acesso à pagina do email
@app.get("/uspmail")
def show_profile(request: Request, user: Usuario = Depends(get_active_user)):
    return templates.TemplateResponse(
        request=request,
        name="email.html",
        context={"email": user.email}
    ) 

# rota para o acesso aos emails recebidos do usuário
@app.get("/lista_recebidos", response_class=HTMLResponse)
def lista(request: Request, user: Usuario = Depends(get_active_user)):

    with Session(engine) as session:
        query = select(Email).where(Email.destinatario_id == user.id).order_by(Email.criado_em.desc())
        emails = session.exec(query).all()

        # lista com os emails e informações relevantes a serem acessadas do email
        emailsfinal = []
        for e in emails:
            emailsfinal.append({
                "id": e.id,
                "titulo": e.titulo,
                "remetente": e.remetente.email,
                "tempo": str(e.criado_em)[:16]
            })
        
        return templates.TemplateResponse(request, "emailsrecebidos.html", {"emails": emailsfinal})

# rota para o acesso aos emails enviados do usuário
@app.get("/lista_enviados", response_class=HTMLResponse)
def lista2(request: Request, user: Usuario = Depends(get_active_user)):
    
    with Session(engine) as session:        
        query = select(Email).where(Email.remetente_id == user.id).order_by(Email.criado_em.desc())
        emails = session.exec(query).all()

        # lista com os emails e informações relevantes a serem acessadas do email
        emailsfinal = []
        for e in emails:
            emailsfinal.append({
                "id": e.id,
                "titulo": e.titulo,
                "destinatario": e.destinatario.email,
                "tempo": str(e.criado_em)[:16]
            })
    
        return templates.TemplateResponse(request, "emailsenviados.html", {"emails": emailsfinal})

# rota para acesso à pagina de escrever email
@app.get("/escrever_email", response_class=HTMLResponse)
def escrever(request: Request):
    return templates.TemplateResponse(request, "escreveremail.html")

# rota para o envio de emails
@app.post("/enviar_email")
def enviar(titulo: str = Form(...), destino: str = Form(...), mensagem: str = Form(...), user: Usuario = Depends(get_active_user)):
    
    with Session(engine) as session:
        destinatario = session.exec(
            select(Usuario).where(Usuario.email == destino)
        ).first()

        if not destinatario:
            return HTMLResponse("<h1>Destinatário não encontrado.</h1>");
        
        email = Email(
            titulo=titulo,
            mensagem=mensagem,
            remetente_id = user.id,
            destinatario_id = destinatario.id)

        session.add(email)
        session.commit()

    return HTMLResponse("<h1> Email enviado! </h1>")

# rota para visualizar um email específico selecionado pelo usuário
@app.get("/email/{email_id}", response_class=HTMLResponse)
def ver_email(request: Request, email_id: int):
    with Session(engine) as session:
        query = select(Email).where(Email.id == email_id)
        busca = session.exec(query).first()

        # informações relevantes do email a serem acessadas
        email = {
            "id": busca.id,
            "titulo": busca.titulo,
            "remetente": busca.remetente.email,
            "destinatario": busca.destinatario.email,
            "mensagem": busca.mensagem,
            "data": str(busca.criado_em)[:10],
            "tempo": str(busca.criado_em)[11:16]
        }

        # lista de respostas e informações a serem acessadas
        respostas = []
        for r in busca.respostas:
            respostas.append({
                "mensagem": r.mensagem,
                "autor": r.dono.email,
                "tempo": str(r.criado_em)[11:16],
                "data": str(r.criado_em)[:10]
            })
        
        return templates.TemplateResponse(request, "visualizaremail.html", {"email": email, "respostas": respostas})

# rota para realizar busca de emails e retornar o html
@app.get("/buscaremails", response_class=HTMLResponse)
def buscar(request: Request, busca: str | None=''):

    with Session(engine) as session:
        query = select(Email).where(Email.titulo.contains(busca)).order_by(Email.criado_em.desc())
        emails = session.exec(query).all()

        # lista de email com as informações relevantes a serem mostradas
        emailsfinal = []
        for e in emails:
            emailsfinal.append({
                "id": e.id,
                "titulo": e.titulo,
                "destinatario": e.destinatario.email,
                "remetente": e.remetente.email,
                "tempo": str(e.criado_em)[:16]
            })
    
    return templates.TemplateResponse(request, "emailsbuscados.html", {"emails": emailsfinal})
        
# rota para deleção de emails
@app.delete("/emails/{email_id}", response_class=HTMLResponse)
def deletar_email(email_id: int, request : Request):
    with Session(engine) as session:
        email = session.get(Email, email_id)

        session.delete(email)
        session.commit()

    # retorno da string nula para atualizar diretamente na lista de emails enviados
    return ''

# rota para acesso a página de edição de emails
@app.get("/emails/{email_id}/editar", response_class=HTMLResponse)
def editar(request: Request, email_id: int):
    with Session(engine) as session:
        email = session.get(Email, email_id)

    return templates.TemplateResponse(request, "editoremail.html", {"request": request, "email": email})

# rota para efetuar a edição do email
@app.put("/emails/{email_id}", response_class=HTMLResponse)
def atualizar_email(request: Request, email_id: int, titulo: str = Form(...), mensagem: str = Form(...),  user: Usuario = Depends(get_active_user)):
    
    with Session(engine) as session:
        email = session.get(Email, email_id)

        email.titulo = titulo
        email.mensagem = mensagem

        session.add(email)
        session.commit()

        query = select(Email).where(Email.remetente_id == user.id).order_by(Email.criado_em.desc())
        emails = session.exec(query).all()

        # lista de emails enviados para, ao editar, retornar a página com os emails enviados
        emailsfinal = []
        for e in emails:
            emailsfinal.append({
                "id": e.id,
                "titulo": e.titulo,
                "destinatario": e.destinatario.email,
                "tempo": str(e.criado_em)[:16]
            })
    
    return templates.TemplateResponse(request, "emailsenviados.html", {"emails": emailsfinal})

# rota para adicionar respostas de emails
@app.post("/emails/{email_id}/responder", response_class=HTMLResponse)
def responder(request: Request,  email_id: int, user: Usuario = Depends(get_active_user), mensagem: str = Form(...)):
    with Session(engine) as session:
        resposta = RespostaEmail(
            mensagem=mensagem,
            dono_id=user.id,
            email_id=email_id
        )

        session.add(resposta)
        session.commit()

        query = select(Email).where(Email.id == email_id)
        busca = session.exec(query).first()

        # lista de respostas do email respondido
        respostas = []
        for r in busca.respostas:
            respostas.append({
                "mensagem": r.mensagem,
                "autor": r.dono.email,
                "tempo": str(r.criado_em)[11:16],
                "data": str(r.criado_em)[:10]
            })

        # informações do email a serem retornadas para, assim que responder, retornar o html com o email + respostas
        email = {
            "id": busca.id,
            "titulo": busca.titulo,
            "remetente": busca.remetente.email,
            "destinatario": busca.destinatario.email,
            "mensagem": busca.mensagem,
            "data": str(busca.criado_em)[:10],
            "tempo": str(busca.criado_em)[11:16],
        }

    return templates.TemplateResponse(request, "visualizaremail.html", {"email": email, "respostas": respostas})
            
