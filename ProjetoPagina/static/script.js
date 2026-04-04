function pagina_criarconta() {
    window.location.href = "/criarcontahtml";
}

function pagina_login() {
    window.location.href = "/";
}

async function criarconta(){
    const dados = {
	email: document.getElementById("email").value,
	senha: document.getElementById("senha").value,
    };

    confirma_senha = document.getElementById("confirma_senha").value;

    if(dados.senha !== confirma_senha){
	alert("Senhas diferem!");
	return;
    }

    const resposta = await fetch('/usuarios', {
	method: 'POST',
	headers: {
	    'Content-Type': 'application/json'
	},
	body: JSON.stringify(dados)
    });

    
    if (resposta.ok){
	const resultado = await resposta.json();
	alert("E-mail " + resultado.usuario + " criado!");
    } else {
	alert("E-mail já existente, tente outro!");
    }
}

async function login() {

    const email = document.getElementById('email').value;
    const senha = document.getElementById('senha').value;
    const resposta = await fetch('/login?email=' + email + '&senha=' + senha, {
	method: 'POST'
    });


    if (resposta.ok) {
	window.location.href = "/uspmail";
    } else {
	alert("Usuário ou senha incorretos.");
    }

}

