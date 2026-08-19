let botao = document.getElementById("abrirModal");
let modal = document.getElementById("meuModal");
let botaoFechar = document.getElementById("fecharModal");


// =========================
// LOGICA DAS DATAS DISPONIVEIS
// =========================

let hoje = new Date();

let nomesDias = [
    "Domingo",
    "Segunda-feira",
    "Terça-feira",
    "Quarta-feira",
    "Quinta-feira",
    "Sexta-feira",
    "Sábado"
];

for (let i = 0; i <= 14; i++) {

    let data = new Date(hoje);

    data.setDate(hoje.getDate() + i);

    let diaDaSemana = data.getDay();

    if (diaDaSemana === 0 || diaDaSemana === 1) {
        continue;
    }

    let nomeDia = nomesDias[diaDaSemana];

    console.log(nomeDia);
}


// =========================
// MODAL DA PAGINA
// =========================

function abrir() {
    modal.style.display = "flex";
}

botao.addEventListener("click", abrir);


function fechar() {
    modal.style.display = "none";
}

botaoFechar.addEventListener("click", fechar);