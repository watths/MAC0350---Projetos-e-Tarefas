
# imports necessários

from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel
from datetime import datetime
from zoneinfo import ZoneInfo

# classe Usuário
class Usuario(SQLModel, table=True):

    # informações do usuário
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    senha: str

    # lista de emails enviados, recebidos e respostas de emails efetuadas
    emails_enviados: List["Email"] = Relationship(
        back_populates="remetente", 
        sa_relationship_kwargs={"foreign_keys": lambda: [Email.remetente_id]}
    )

    emails_recebidos: List["Email"] = Relationship(
        back_populates="destinatario",
        sa_relationship_kwargs={"foreign_keys": lambda: [Email.destinatario_id]}
    )

    respostas: List["RespostaEmail"] = Relationship(
        back_populates="dono",
        sa_relationship_kwargs={"foreign_keys": lambda: [RespostaEmail.dono_id]}
    )

# classe Email
class Email(SQLModel, table=True):

    # informações de um email
    id: Optional[int] = Field(default=None, primary_key=True)
    titulo: str
    mensagem: str
    criado_em: datetime = Field(default_factory=lambda: datetime.now(ZoneInfo("America/Sao_Paulo")))

    # informações dos Usuários associados ao email
    remetente_id: int = Field(foreign_key="usuario.id")
    destinatario_id: int = Field(foreign_key="usuario.id")

    remetente: "Usuario" = Relationship(
        back_populates="emails_enviados",
        sa_relationship_kwargs={"foreign_keys": lambda: [Email.remetente_id]}
    )

    destinatario: "Usuario" = Relationship(
        back_populates="emails_recebidos",
        sa_relationship_kwargs={"foreign_keys": lambda: [Email.destinatario_id]}
    )

    # respostas do email
    respostas: List["RespostaEmail"] = Relationship(
        back_populates="email",
        sa_relationship_kwargs={"foreign_keys": lambda: [RespostaEmail.email_id], "cascade": "all, delete"}
    )

class RespostaEmail(SQLModel, table=True):

    # informações de uma resposta do email
    id: Optional[int] = Field(default=None, primary_key=True)
    mensagem: str
    criado_em: datetime = Field(default_factory=lambda: datetime.now(ZoneInfo("America/Sao_Paulo")))

    # informações do usuário que respondeu e do email associado
    dono_id: int = Field(foreign_key="usuario.id")
    email_id: int = Field(foreign_key="email.id")
    
    
    dono: "Usuario" = Relationship(
        back_populates="respostas",
        sa_relationship_kwargs={"foreign_keys": lambda: [RespostaEmail.dono_id]}
    )
    

    email: "Email" = Relationship(
        back_populates="respostas",
        sa_relationship_kwargs={"foreign_keys": lambda: [RespostaEmail.email_id]}
    )
   
# pelas 3 classes terem relação, realiza um update_forward_refs
Usuario.update_forward_refs()
Email.update_forward_refs()
RespostaEmail.update_forward_refs()
