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

        console.log(
            "Serviço selecionado:",
            servicoSelecionado
        );

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

// Essa função monta e devolve um array
// com os horários disponíveis de acordo
// com a duração do serviço.

function gerarHorariosDoDia() {

    if (!servicoSelecionado) {
        alert("Escolha um serviço!");
        return [];
    }

    let horarios = [];

    periodosFuncionamento.forEach(function(periodo) {

        let inicio = periodo.inicio * 60;
        let fim = periodo.fim * 60;

        for (
            let minutos = inicio;
            minutos < fim;
            minutos += 30
        ) {

            let fimServico =
                minutos + servicoSelecionado.tempo;

            // O serviço precisa terminar
            // antes do fechamento do período.
            if (fimServico > fim) {
                continue;
            }

            let hora =
                Math.floor(minutos / 60);

            let minuto =
                minutos % 60;

            let horaFormatada =
                String(hora).padStart(2, "0");

            let minutoFormatado =
                String(minuto).padStart(2, "0");

            let horarioFormatado =
                `${horaFormatada}:${minutoFormatado}`;

            horarios.push(
                horarioFormatado
            );
        }
    });

    return horarios;
}


// =========================
// DATAS DISPONÍVEIS
// =========================

let hoje = new Date();


let nomesDias = [
    "Dom",
    "Seg",
    "Ter",
    "Qua",
    "Qui",
    "Sex",
    "Sáb"
];


let dataSelecionada = null;


// Mostra hoje e os próximos 14 dias.
for (let i = 0; i <= 14; i++) {

    let data = new Date(hoje);

    data.setDate(
        hoje.getDate() + i
    );

    let diaDaSemana =
        data.getDay();

    let ano =
        data.getFullYear();

    let mes = String(
        data.getMonth() + 1
    ).padStart(2, "0");

    let dia = String(
        data.getDate()
    ).padStart(2, "0");

    let dataFormatada =
        `${ano}-${mes}-${dia}`;


    fetch(`/dia-especial/${dataFormatada}`)

        .then(function(resposta) {
            return resposta.json();
        })

        .then(function(diaEspecial) {

            // =========================
            // DECIDE SE O DIA APARECE
            // =========================

            let deveMostrar = false;


            // Se existe uma configuração especial,
            // ela manda na decisão.
            if (diaEspecial.especial) {

                deveMostrar =
                    diaEspecial.aberto;

            } else {

                // Se não existe configuração especial,
                // usa o funcionamento normal:
                // terça até sábado.

                if (
                    diaDaSemana !== 0 &&
                    diaDaSemana !== 1
                ) {
                    deveMostrar = true;
                }
            }


            // Se a barbearia não funciona nesse dia,
            // não cria botão.
            if (!deveMostrar) {
                return;
            }


            // =========================
            // CRIA O BOTÃO DA DATA
            // =========================

            let nomeDia =
                nomesDias[diaDaSemana];

            let textoData =
                `${data.getDate()} ${nomeDia}`;

            let botaoData =
                document.createElement(
                    "button"
                );

            botaoData.textContent =
                textoData;

            botaoData.type =
                "button";


            botaoData.addEventListener(
                "click",
                function() {

                    dataSelecionada =
                        data;

                    console.log(
                        "Data escolhida:",
                        textoData
                    );


                    let todosBotoesData =
                        datasDisponiveis
                            .querySelectorAll(
                                "button"
                            );


                    todosBotoesData.forEach(
                        function(btn) {

                            btn.classList.remove(
                                "selecionado"
                            );
                        }
                    );


                    botaoData.classList.add(
                        "selecionado"
                    );


                    renderizarHorarios();
                }
            );


            datasDisponiveis.appendChild(
                botaoData
            );
        })

        .catch(function(erro) {

            console.log(
                "Erro ao verificar dia:",
                dataFormatada,
                erro
            );
        });
}


// =========================
// HORÁRIO PARA MINUTOS
// =========================

function horarioParaMinutos(horario) {

    let partes =
        horario.split(":");

    let hora =
        Number(partes[0]);

    let minuto =
        Number(partes[1]);

    return hora * 60 + minuto;
}


// =========================
// HORÁRIO SELECIONADO
// =========================

let horarioSelecionado = null;


// =========================
// RENDERIZAÇÃO DOS HORÁRIOS
// =========================

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


    // Primeiro gera os horários
    // normais da barbearia.
    let horarios =
        gerarHorariosDoDia();


    // Transforma a data selecionada
    // para o formato YYYY-MM-DD.
    let ano =
        dataSelecionada.getFullYear();

    let mes = String(
        dataSelecionada.getMonth() + 1
    ).padStart(2, "0");

    let dia = String(
        dataSelecionada.getDate()
    ).padStart(2, "0");

    let dataFormatada =
        `${ano}-${mes}-${dia}`;


    // Primeiro pergunta ao Flask
    // se essa data possui uma regra especial.
    fetch(`/dia-especial/${dataFormatada}`)

        .then(function(resposta) {

            return resposta.json();
        })

        .then(function(diaEspecial) {

            let horariosDoDia =
                horarios;


            // Se for um dia especial aberto,
            // descartamos os horários normais
            // e montamos os horários especiais.
            if (
                diaEspecial.especial &&
                diaEspecial.aberto
            ) {

                horariosDoDia = [];


                diaEspecial.periodos.forEach(
                    function(periodo) {

                        let inicioPeriodo =
                            horarioParaMinutos(
                                periodo.inicio
                            );

                        let fimPeriodo =
                            horarioParaMinutos(
                                periodo.fim
                            );


                        for (
                            let minutos = inicioPeriodo;
                            minutos < fimPeriodo;
                            minutos += 30
                        ) {

                            let fimServico =
                                minutos +
                                servicoSelecionado.tempo;


                            // O serviço precisa caber
                            // completamente dentro
                            // do período especial.
                            if (
                                fimServico > fimPeriodo
                            ) {
                                continue;
                            }


                            let hora =
                                Math.floor(
                                    minutos / 60
                                );

                            let minuto =
                                minutos % 60;


                            let horaFormatada =
                                String(hora)
                                    .padStart(2, "0");

                            let minutoFormatado =
                                String(minuto)
                                    .padStart(2, "0");


                            let horarioFormatado =
                                `${horaFormatada}:${minutoFormatado}`;


                            horariosDoDia.push(
                                horarioFormatado
                            );
                        }
                    }
                );
            }


            // Se existe uma regra especial
            // dizendo que o dia está fechado,
            // não mostramos nenhum horário.
            if (
                diaEspecial.especial &&
                !diaEspecial.aberto
            ) {

                horariosDoDia = [];
            }


            // Depois de descobrir os horários
            // possíveis daquele dia, buscamos
            // os agendamentos já existentes.
            return fetch(
                `/agendamentos/${dataFormatada}`
            )

                .then(function(resposta) {

                    return resposta.json();
                })

                .then(function(agendamentos) {

                    return {
                        horarios: horariosDoDia,
                        agendamentos: agendamentos
                    };
                });
        })


        .then(function(resultado) {

            let horariosDoDia =
                resultado.horarios;

            let agendamentos =
                resultado.agendamentos;


            horariosDoDia.forEach(
                function(horario) {


                    // =========================
                    // HORÁRIO NOVO
                    // =========================

                    let inicioNovo =
                        horarioParaMinutos(
                            horario
                        );


                    // =========================
                    // ANTECEDÊNCIA DE 30 MIN
                    // =========================

                    let agora =
                        new Date();


                    let mesmaData =
                        dataSelecionada.getFullYear()
                            === agora.getFullYear()
                        &&
                        dataSelecionada.getMonth()
                            === agora.getMonth()
                        &&
                        dataSelecionada.getDate()
                            === agora.getDate();


                    // Só precisamos verificar
                    // antecedência se o cliente
                    // estiver agendando para hoje.
                    if (mesmaData) {

                        let minutosAgora =
                            agora.getHours() * 60
                            +
                            agora.getMinutes();


                        let limiteMinimo =
                            minutosAgora + 30;


                        // Se faltar menos de 30 minutos,
                        // o horário nem aparece.
                        if (
                            inicioNovo < limiteMinimo
                        ) {
                            return;
                        }
                    }


                    let fimNovo =
                        inicioNovo +
                        servicoSelecionado.tempo;


                    // =========================
                    // VERIFICA CONFLITOS
                    // =========================

                    let temConflito =
                        false;


                    agendamentos.forEach(
                        function(agendamento) {


                            let inicioExistente =
                                horarioParaMinutos(
                                    agendamento.horario
                                );


                            let fimExistente =
                                inicioExistente
                                +
                                agendamento.servico.tempo;


                            if (
                                inicioNovo < fimExistente
                                &&
                                fimNovo > inicioExistente
                            ) {

                                temConflito = true;
                            }
                        }
                    );


                    // Se existe conflito,
                    // não cria o botão.
                    if (temConflito) {
                        return;
                    }


                    // =========================
                    // CRIA BOTÃO DO HORÁRIO
                    // =========================

                    let botaoHorario =
                        document.createElement(
                            "button"
                        );


                    botaoHorario.textContent =
                        horario;


                    botaoHorario.type =
                        "button";


                    botaoHorario.addEventListener(
                        "click",
                        function() {


                            horarioSelecionado =
                                horario;


                            console.log(
                                "Horário escolhido:",
                                horarioSelecionado
                            );


                            let todosBotoesHorario =
                                horariosDisponiveis
                                    .querySelectorAll(
                                        "button"
                                    );


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
                }
            );
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

function abrir() {

    modal.style.display =
        "flex";
}


botao.addEventListener(
    "click",
    abrir
);


function fechar() {

    modal.style.display =
        "none";
}


botaoFechar.addEventListener(
    "click",
    fechar
);


// =========================
// CONFIRMAR AGENDAMENTO
// =========================

botaoConfirmar.addEventListener(
    "click",
    function() {


        // =========================
        // NOME E CELULAR
        // =========================

        let nome =
            nomeCliente.value.trim();

        let celular =
            celularCliente.value.trim();


        if (nome === "") {

            alert(
                "Digite seu nome!"
            );

            return;
        }


        let nomeSemEspacos =
            nome.replaceAll(
                " ",
                ""
            );


        if (
            nomeSemEspacos.length < 3
        ) {

            alert(
                "Digite um nome válido!"
            );

            return;
        }


        let nomeValido =
            /^[A-Za-zÀ-ÿ\s]+$/.test(
                nome
            );


        if (!nomeValido) {

            alert(
                "O nome deve conter apenas letras!"
            );

            return;
        }


        if (celular === "") {

            alert(
                "Digite seu celular!"
            );

            return;
        }


        let celularSomenteNumeros =
            celular.replace(
                /\D/g,
                ""
            );


        if (
            celularSomenteNumeros.length !== 11
        ) {

            alert(
                "Digite um celular válido com DDD!"
            );

            return;
        }


        // =========================
        // SERVIÇO
        // =========================

        if (!servicoSelecionado) {

            alert(
                "Escolha um serviço!"
            );

            return;
        }


        // =========================
        // DATA
        // =========================

        if (!dataSelecionada) {

            alert(
                "Escolha uma data!"
            );

            return;
        }


        // =========================
        // HORÁRIO
        // =========================

        if (!horarioSelecionado) {

            alert(
                "Escolha um horário!"
            );

            return;
        }


        // =========================
        // FORMATA DATA
        // =========================

        let ano =
            dataSelecionada.getFullYear();

        let mes = String(
            dataSelecionada.getMonth() + 1
        ).padStart(2, "0");

        let dia = String(
            dataSelecionada.getDate()
        ).padStart(2, "0");


        let dataFormatada =
            `${ano}-${mes}-${dia}`;


        console.log(
            "Pronto para enviar ao backend:",
            {
                nome: nome,
                celular:
                    celularSomenteNumeros,
                servico:
                    chaveServicoSelecionado,
                data:
                    dataFormatada,
                horario:
                    horarioSelecionado
            }
        );


        // =========================
        // ENVIA PARA O FLASK
        // =========================

        fetch(
            "/agendar",
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    nome: nome,

                    celular:
                        celularSomenteNumeros,

                    servico:
                        chaveServicoSelecionado,

                    data:
                        dataFormatada,

                    horario:
                        horarioSelecionado
                })
            }
        )


        .then(function(resposta) {

            return resposta
                .json()
                .then(
                    function(dadosResposta) {

                        return {
                            ok:
                                resposta.ok,

                            dados:
                                dadosResposta
                        };
                    }
                );
        })


        .then(function(resultado) {


            // Se o Flask rejeitou,
            // mostra a mensagem de erro.
            if (!resultado.ok) {

                alert(
                    resultado.dados.erro
                );

                return;
            }


            // =========================
            // SUCESSO
            // =========================

            alert(
                resultado.dados.mensagem
            );


            // Limpa nome e celular.
            nomeCliente.value = "";
            celularCliente.value = "";


            // Desmarca o serviço.
            opcoesServico.forEach(
                function(opcao) {

                    opcao.checked = false;
                }
            );


            servicoSelecionado = null;

            chaveServicoSelecionado = null;


            // Limpa a data.
            dataSelecionada = null;


            let todosBotoesData =
                datasDisponiveis
                    .querySelectorAll(
                        "button"
                    );


            todosBotoesData.forEach(
                function(botao) {

                    botao.classList.remove(
                        "selecionado"
                    );
                }
            );


            // Limpa horário.
            horarioSelecionado = null;

            horariosDisponiveis.innerHTML =
                "";


            // Fecha o modal.
            fechar();
        })


        .catch(function(erro) {

            console.log(
                "Erro ao enviar agendamento:",
                erro
            );


            alert(
                "Não foi possível realizar o agendamento."
            );
        });
    }
);