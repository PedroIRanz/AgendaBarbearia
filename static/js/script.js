let botao = document.getElementById("abrirModal");
let modal = document.getElementById("meuModal");
let botaoFechar = document.getElementById("fecharModal");
let datasDisponiveis = document.getElementById("datasDisponiveis");
let horariosDisponiveis = document.getElementById("horariosDisponiveis");
let botaoConfirmar = document.getElementById("confirmarAgendamento");
let nomeCliente = document.getElementById("nomeCliente");
let celularCliente = document.getElementById("celularCliente");

// =========================
// SERVIÇOS
// =========================

let servicos = {
    corte: {
        nome: "Corte",
        tempo: 30,
        valor: 30
    },
    barba: {
        nome: "Barba",
        tempo: 30,
        valor: 20
    },
    corte_barba: {
        nome: "Corte + Barba",
        tempo: 60,
        valor: 45
    }
};

let opcoesServico = document.querySelectorAll(
    'input[name="servico"]'
);

let servicoSelecionado = null;
let chaveServicoSelecionado = null;

opcoesServico.forEach(function(opcao) {
    opcao.addEventListener("change", function() {

        chaveServicoSelecionado = opcao.value;

        servicoSelecionado =
            servicos[chaveServicoSelecionado];

        if (dataSelecionada) {
            renderizarHorarios();
        }
    });
});

// =========================
// HORÁRIOS DE FUNCIONAMENTO
// =========================

// Aqui defini os períodos em que a barbearia funciona.
//
// Primeiro período:
// 09:00 até 12:00
//
// Segundo período:
// 14:00 até 20:00
//
// Separei em dois períodos porque existe
// o intervalo de almoço entre 12:00 e 14:00.

let periodosFuncionamento = [
    {
        inicio: 9,
        fim: 12
    },
    {
        inicio: 14,
        fim: 20
    }
];

// =========================
// GERAÇÃO DOS HORÁRIOS
// =========================

// Agora, em vez de só logar no console, essa função
// MONTA e DEVOLVE (return) um array com todos os
// horários do dia, tipo:
//
// ["09:00", "09:30", "10:00", ..., "19:30"]
//
// Assim consigo reaproveitar esse array tanto pra
// desenhar os botões na tela quanto, no futuro,
// pra comparar com o backend e ver quais já
// estão ocupados.

function gerarHorariosDoDia() {
    if (!servicoSelecionado) {
        alert("Escolha um serviço!");
        return [];
    }

    // Array vazio que vai guardar os horários
    // formatados, tipo "09:00", "09:30" etc.
    let horarios = [];

    // Uso o forEach para passar por cada período
    // de funcionamento da barbearia.
    //
    // Na primeira volta:
    // periodo = { inicio: 9, fim: 12 }
    //
    // Na segunda volta:
    // periodo = { inicio: 14, fim: 20 }
    periodosFuncionamento.forEach(function(periodo) {
        // Transformo as horas em minutos, pra
        // facilitar a conta de 30 em 30 minutos.
        let inicio = periodo.inicio * 60;
        let fim = periodo.fim * 60;

        for (
            let minutos = inicio;
            minutos < fim;
            minutos += 30
        ) {
            let fimServico = minutos + servicoSelecionado.tempo;

            if (fimServico > fim) {
                continue;
            }

            let hora = Math.floor(minutos / 60);
            let minuto = minutos % 60;

            let horaFormatada =
                String(hora).padStart(2, "0");

            let minutoFormatado =
                String(minuto).padStart(2, "0");

            let horarioFormatado =
                `${horaFormatada}:${minutoFormatado}`;

            // Em vez de console.log, agora eu
            // guardo no array.
            horarios.push(horarioFormatado);
        }
    });

    return horarios;
}

// =========================
// LÓGICA DAS DATAS DISPONÍVEIS
// =========================

// Pega a data atual do computador/celular.
let hoje = new Date();

// O getDay() retorna um número.
//
// 0 = Domingo
// 1 = Segunda
// 2 = Terça
// 3 = Quarta
// 4 = Quinta
// 5 = Sexta
// 6 = Sábado
//
// Essa lista permite transformar o número
// no nome que será mostrado para o cliente.
let nomesDias = [
    "Dom",
    "Seg",
    "Ter",
    "Qua",
    "Qui",
    "Sex",
    "Sáb"
];

// Enquanto o cliente não escolher uma data,
// a variável começa vazia.
let dataSelecionada = null;

// Percorre hoje e os próximos 14 dias.
//
// i = 0 → hoje
// i = 1 → amanhã
// i = 2 → daqui dois dias
// ...
// i = 14 → daqui 14 dias
for (let i = 0; i <= 14; i++) {
    // Crio uma cópia da data atual para não
    // modificar a variável "hoje".
    let data = new Date(hoje);

    // Avança a quantidade de dias representada por i.
    data.setDate(
        hoje.getDate() + i
    );

    // Descobre qual é o dia da semana.
    let diaDaSemana = data.getDay();

    // Domingo = 0
    // Segunda = 1
    //
    // Como a barbearia não funciona nesses dias,
    // uso continue para ignorá-los e passar
    // para a próxima repetição.
    if (
        diaDaSemana === 0 ||
        diaDaSemana === 1
    ) {
        continue;
    }

    // Pega o nome do dia da semana.
    //
    // Exemplo:
    //
    // diaDaSemana = 3
    //
    // nomesDias[3]
    // = "Quarta-feira"
    let nomeDia = nomesDias[diaDaSemana];

    // Monta o texto que aparecerá no botão.
    //
    // Exemplo:
    //
    // 20 - Quinta-feira
    let textoData =
        `${data.getDate()}${nomeDia}`;

    // Cria um botão pelo JavaScript.
    let botaoData =
        document.createElement("button");

    // Coloca o texto da data dentro do botão.
    botaoData.textContent = textoData;

    // Quando o cliente clicar em uma data,
    // guardo essa data na variável dataSelecionada
    // e mostro os horários disponíveis daquele dia.
    botaoData.addEventListener(
        "click",
        function() {
            dataSelecionada = data;

            console.log(
                "Data escolhida:",
                textoData
            );

            // Tira a marcação visual de todos os
            // botões de data...
            let todosBotoesData =
                datasDisponiveis.querySelectorAll("button");

            todosBotoesData.forEach(function(btn) {
                btn.classList.remove("selecionado");
            });

            // ...e marca só o botão que foi clicado.
            botaoData.classList.add("selecionado");

            // Desenha os horários disponíveis
            // para essa data na tela.
            renderizarHorarios();
        }
    );

    // Coloca o botão dentro da div
    // datasDisponiveis do HTML.
    datasDisponiveis.appendChild(
        botaoData
    );
}

// =========================
// RENDERIZAÇÃO DOS HORÁRIOS
// =========================

// Guarda qual horário o cliente escolheu.
// Começa vazio até ele clicar em algum.
let horarioSelecionado = null;

// Essa função desenha os botões de horário
// na div #horariosDisponiveis, com base na
// data que foi selecionada.
function horarioParaMinutos(horario) {
    let partes = horario.split(":");

    let hora = Number(partes[0]);
    let minuto = Number(partes[1]);

    return hora * 60 + minuto;
}

function renderizarHorarios() {

    horariosDisponiveis.innerHTML = "";
    horarioSelecionado = null;

    if (!dataSelecionada) {
        return;
    }

    if (!servicoSelecionado) {
        alert("Escolha um serviço!");
        return;
    }

    let horarios = gerarHorariosDoDia();

    let ano = dataSelecionada.getFullYear();

    let mes = String(
        dataSelecionada.getMonth() + 1
    ).padStart(2, "0");

    let dia = String(
        dataSelecionada.getDate()
    ).padStart(2, "0");

    let dataFormatada =
        `${ano}-${mes}-${dia}`;

    fetch(`/agendamentos/${dataFormatada}`)
        .then(function(resposta) {
            return resposta.json();
        })
        .then(function(agendamentos) {

            horarios.forEach(function(horario) {

                let inicioNovo =
                    horarioParaMinutos(horario);

                let agora = new Date();

                let mesmaData =
                    dataSelecionada.getFullYear() === agora.getFullYear()
                    &&
                    dataSelecionada.getMonth() === agora.getMonth()
                    &&
                    dataSelecionada.getDate() === agora.getDate();

                if (mesmaData) {

                    let minutosAgora =
                        agora.getHours() * 60
                        + agora.getMinutes();

                    let limiteMinimo =
                        minutosAgora + 30;

                    if (inicioNovo < limiteMinimo) {
                        return;
                    }
                }

                let fimNovo =
                    inicioNovo + servicoSelecionado.tempo;

                let temConflito = false;

                agendamentos.forEach(function(agendamento) {

                    let inicioExistente =
                        horarioParaMinutos(
                            agendamento.horario
                        );

                    let fimExistente =
                        inicioExistente
                        + agendamento.servico.tempo;

                    if (
                        inicioNovo < fimExistente &&
                        fimNovo > inicioExistente
                    ) {
                        temConflito = true;
                    }

                });

                if (temConflito) {
                    return;
                }

                let botaoHorario =
                    document.createElement("button");

                botaoHorario.textContent = horario;
                botaoHorario.type = "button";

                botaoHorario.addEventListener(
                    "click",
                    function() {

                        horarioSelecionado = horario;

                        console.log(
                            "Horário escolhido:",
                            horarioSelecionado
                        );

                        let todosBotoesHorario =
                            horariosDisponiveis
                            .querySelectorAll("button");

                        todosBotoesHorario.forEach(
                            function(btn) {
                                btn.classList.remove(
                                    "selecionado"
                                );
                            }
                        );

                        botaoHorario.classList.add(
                            "selecionado"
                        );
                    }
                );

                horariosDisponiveis.appendChild(
                    botaoHorario
                );
            });
        })
        .catch(function(erro) {
            console.log(
                "Erro ao buscar horários:",
                erro
            );
        });
}

// =========================
// MODAL DA PÁGINA
// =========================

// Abre o modal mudando o display
// de none para flex.
function abrir() {
    modal.style.display = "flex";
}

// Quando o botão de agendamento recebe
// um clique, executa a função abrir.
botao.addEventListener(
    "click",
    abrir
);

// Fecha o modal mudando novamente
// o display para none.
function fechar() {
    modal.style.display = "none";
}

// Quando clicar no X, executa fechar.
botaoFechar.addEventListener(
    "click",
    fechar
);

// =========================
// CONFIRMAR AGENDAMENTO
// =========================

// Por enquanto só valido se o cliente preencheu
// tudo. No próximo passo, aqui vamos enviar esses
// dados pro Flask salvar de verdade.
botaoConfirmar.addEventListener(
    "click",
    function() {
        let nome = nomeCliente.value.trim();
        let celular = celularCliente.value.trim();

        if (nome === "") {
            alert("Digite seu nome!");
            return;
        }

        let nomeSemEspacos = nome.replaceAll(" ", "");

        if (nomeSemEspacos.length < 3) {
            alert("Digite um nome válido!");
            return;
        }

        let nomeValido = /^[A-Za-zÀ-ÿ\s]+$/.test(nome);

        if (!nomeValido) {
            alert("O nome deve conter apenas letras!");
            return;
        }

        if (celular === "") {
            alert("Digite seu celular!");
            return;
        }

        let celularSomenteNumeros = celular.replace(/\D/g, "");

        if (celularSomenteNumeros.length !== 11) {
            alert("Digite um celular válido com DDD!");
            return;
        }

        if (!servicoSelecionado) {
            alert("Escolha um serviço!");
            return;
        }

        if (!dataSelecionada) {
            alert("Escolha uma data!");
            return;
        }

        if (!horarioSelecionado) {
            alert("Escolha um horário!");
            return;
        }

        console.log("Pronto para enviar ao backend:", {
            nome: nome,
            celular: celularSomenteNumeros,
            servico: chaveServicoSelecionado,
            data: dataSelecionada,
            horario: horarioSelecionado
        });

        let ano = dataSelecionada.getFullYear();
        let mes = String(dataSelecionada.getMonth() + 1).padStart(2, "0");
        let dia = String(dataSelecionada.getDate()).padStart(2, "0");
        let dataFormatada = `${ano}-${mes}-${dia}`;

        fetch("/agendar", {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                nome: nome,
                celular: celularSomenteNumeros,
                servico: chaveServicoSelecionado,
                data: dataFormatada,
                horario: horarioSelecionado
            })
        })
        .then(function(resposta) {
            return resposta.json().then(function(dadosResposta) {
                return {
                    ok: resposta.ok,
                    dados: dadosResposta
                };
            });
        })
        .then(function(resultado) {

            if (!resultado.ok) {
                alert(resultado.dados.erro);
                return;
            }

            alert(resultado.dados.mensagem);

            // Limpa nome e celular
            nomeCliente.value = "";
            celularCliente.value = "";

            // Desmarca o serviço
            opcoesServico.forEach(function(opcao) {
                opcao.checked = false;
            });

            servicoSelecionado = null;

            // Limpa a data selecionada
            dataSelecionada = null;

            let todosBotoesData =
                datasDisponiveis.querySelectorAll("button");

            todosBotoesData.forEach(function(botao) {
                botao.classList.remove("selecionado");
            });

            // Limpa o horário selecionado
            horarioSelecionado = null;
            horariosDisponiveis.innerHTML = "";

            // Fecha o modal
            fechar();
        })
        .catch(function(erro) {
            console.log("Erro ao enviar agendamento:", erro);

            alert(
                "Não foi possível realizar o agendamento."
            );
        });
    }
);
