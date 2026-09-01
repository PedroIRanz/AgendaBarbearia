let dataEspecial =
    document.getElementById("dataEspecial");

let botaoSalvar =
    document.getElementById("salvarDiaEspecial");

let listaPeriodos =
    document.getElementById("listaPeriodos");

let botaoAdicionarPeriodo =
    document.getElementById("adicionarPeriodo");

let opcoesFuncionamento =
    document.querySelectorAll(
        'input[name="funcionamento"]'
    );

let botaoRemoverDia =
    document.getElementById(
        "removerDiaEspecial"
    );


// =========================
// CONVERTE HORÁRIO
// =========================

function horarioParaMinutosAdmin(horario) {

    let partes =
        horario.split(":");

    let hora =
        Number(partes[0]);

    let minuto =
        Number(partes[1]);

    return hora * 60 + minuto;
}


// =========================
// CRIA UMA LINHA DE PERÍODO
// =========================

function criarPeriodo(
    inicio = "",
    fim = ""
) {

    let novaLinha =
        document.createElement("div");

    novaLinha.classList.add(
        "periodo"
    );

    novaLinha.innerHTML = `
        <label>
            Das:
        </label>

        <input
            type="time"
            class="horaInicio"
            step="1800"
            value="${inicio}"
        >

        <label>
            até:
        </label>

        <input
            type="time"
            class="horaFim"
            step="1800"
            value="${fim}"
        >

        <button
            type="button"
            class="removerPeriodo"
        >
            Remover
        </button>
    `;


    let botaoRemover =
        novaLinha.querySelector(
            ".removerPeriodo"
        );


    botaoRemover.addEventListener(
        "click",
        function() {

            let funcionamento =
                document.querySelector(
                    'input[name="funcionamento"]:checked'
                );

            let aberto =
                funcionamento &&
                funcionamento.value === "aberto";


            let linhas =
                document.querySelectorAll(
                    ".periodo"
                );


            // Se o dia estiver aberto,
            // precisa existir pelo menos
            // um período.
            if (
                aberto &&
                linhas.length <= 1
            ) {

                alert(
                    "O dia aberto precisa ter pelo menos um período!"
                );

                return;
            }


            novaLinha.remove();
        }
    );


    listaPeriodos.appendChild(
        novaLinha
    );
}


// =========================
// ABERTO / FECHADO
// =========================

function atualizarFuncionamento() {

    let funcionamento =
        document.querySelector(
            'input[name="funcionamento"]:checked'
        );

    if (!funcionamento) {
        return;
    }


    let aberto =
        funcionamento.value === "aberto";


    if (aberto) {

        listaPeriodos.style.display =
            "block";

        botaoAdicionarPeriodo.style.display =
            "inline-block";


        // Se não existir nenhum período,
        // cria um vazio.
        let linhas =
            document.querySelectorAll(
                ".periodo"
            );


        if (linhas.length === 0) {

            criarPeriodo(
                "",
                ""
            );
        }

    } else {

        listaPeriodos.style.display =
            "none";

        botaoAdicionarPeriodo.style.display =
            "none";
    }
}


// =========================
// ALTERAR ABERTO / FECHADO
// =========================

for (
    let opcao of opcoesFuncionamento
) {

    opcao.addEventListener(
        "change",
        atualizarFuncionamento
    );
}


atualizarFuncionamento();


// =========================
// ADICIONAR PERÍODO
// =========================

botaoAdicionarPeriodo.addEventListener(
    "click",
    function() {

        criarPeriodo(
            "",
            ""
        );
    }
);


// =========================
// CARREGAR DIA ESCOLHIDO
// =========================

dataEspecial.addEventListener(
    "change",
    function() {

        if (!dataEspecial.value) {
            return;
        }


        fetch(
            "/dia-especial/"
            + dataEspecial.value
        )

        .then(function(resposta) {

            return resposta.json();
        })

        .then(function(dados) {

            // Mostra o botão de remover
            // somente se a data já for
            // um dia especial.
            botaoRemoverDia.hidden =
                !dados.especial;


            // Limpa os períodos
            // que estavam na tela.
            listaPeriodos.innerHTML =
                "";


            // =========================
            // DIA NORMAL
            // =========================

            if (!dados.especial) {

                document.querySelector(
                    'input[name="funcionamento"][value="aberto"]'
                ).checked = true;


                criarPeriodo(
                    "",
                    ""
                );


                atualizarFuncionamento();

                return;
            }


            // =========================
            // DIA ESPECIAL ABERTO
            // =========================

            if (dados.aberto) {

                document.querySelector(
                    'input[name="funcionamento"][value="aberto"]'
                ).checked = true;


                for (
                    let periodo of dados.periodos
                ) {

                    criarPeriodo(
                        periodo.inicio,
                        periodo.fim
                    );
                }


                // Segurança caso exista
                // um registro antigo aberto
                // sem nenhum período.
                if (
                    dados.periodos.length === 0
                ) {

                    criarPeriodo(
                        "",
                        ""
                    );
                }


            // =========================
            // DIA ESPECIAL FECHADO
            // =========================

            } else {

                document.querySelector(
                    'input[name="funcionamento"][value="fechado"]'
                ).checked = true;


                // Cria um período vazio.
                // Como o dia está fechado,
                // ele ficará escondido.
                criarPeriodo(
                    "",
                    ""
                );
            }


            atualizarFuncionamento();
        })

        .catch(function(erro) {

            console.log(
                "Erro ao carregar dia especial:",
                erro
            );

            alert(
                "Não foi possível carregar os dados dessa data."
            );
        });
    }
);


// =========================
// SALVAR DIA ESPECIAL
// =========================

botaoSalvar.addEventListener(
    "click",
    function() {

        let funcionamento =
            document.querySelector(
                'input[name="funcionamento"]:checked'
            );


        if (!dataEspecial.value) {

            alert(
                "Escolha uma data!"
            );

            return;
        }


        if (!funcionamento) {

            alert(
                "Escolha se o dia estará aberto ou fechado!"
            );

            return;
        }


        let aberto =
            funcionamento.value === "aberto";

        let periodos = [];


        // =========================
        // COLETA OS PERÍODOS
        // =========================

        if (aberto) {

            let linhasPeriodos =
                document.querySelectorAll(
                    ".periodo"
                );


            if (
                linhasPeriodos.length === 0
            ) {

                alert(
                    "O dia aberto precisa ter pelo menos um período!"
                );

                return;
            }


            for (
                let linha of linhasPeriodos
            ) {

                let inicio =
                    linha.querySelector(
                        ".horaInicio"
                    ).value;

                let fim =
                    linha.querySelector(
                        ".horaFim"
                    ).value;


                // =========================
                // CAMPOS VAZIOS
                // =========================

                if (
                    !inicio ||
                    !fim
                ) {

                    alert(
                        "Preencha todos os horários!"
                    );

                    return;
                }


                // =========================
                // INÍCIO / FIM
                // =========================

                if (
                    fim <= inicio
                ) {

                    alert(
                        "O horário final deve ser maior que o horário inicial!"
                    );

                    return;
                }


                periodos.push({
                    inicio: inicio,
                    fim: fim
                });
            }


            // =========================
            // VERIFICA SOBREPOSIÇÃO
            // =========================

            for (
                let i = 0;
                i < periodos.length;
                i++
            ) {

                let inicio1 =
                    horarioParaMinutosAdmin(
                        periodos[i].inicio
                    );

                let fim1 =
                    horarioParaMinutosAdmin(
                        periodos[i].fim
                    );


                for (
                    let j = i + 1;
                    j < periodos.length;
                    j++
                ) {

                    let inicio2 =
                        horarioParaMinutosAdmin(
                            periodos[j].inicio
                        );

                    let fim2 =
                        horarioParaMinutosAdmin(
                            periodos[j].fim
                        );


                    if (
                        inicio1 < fim2 &&
                        fim1 > inicio2
                    ) {

                        alert(
                            "Os períodos de funcionamento não podem se sobrepor!"
                        );

                        return;
                    }
                }
            }
        }


        // =========================
        // ENVIA PARA O FLASK
        // =========================

        fetch(
            "/admin/dia-especial",
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    data:
                        dataEspecial.value,

                    aberto:
                        aberto,

                    periodos:
                        periodos
                })
            }
        )

        .then(function(resposta) {

            return resposta
                .json()
                .then(function(dados) {

                    return {
                        ok: resposta.ok,
                        dados: dados
                    };
                });
        })

        .then(function(resultado) {

            if (!resultado.ok) {

                alert(
                    resultado.dados.erro
                );

                return;
            }


            alert(
                resultado.dados.mensagem
            );


            // Depois de salvar,
            // essa data passa a ser
            // um dia especial.
            botaoRemoverDia.hidden =
                false;
        })

        .catch(function(erro) {

            console.log(
                "Erro ao salvar dia especial:",
                erro
            );

            alert(
                "Não foi possível salvar o dia especial."
            );
        });
    }
);


// =========================
// REMOVER DIA ESPECIAL
// =========================

botaoRemoverDia.addEventListener(
    "click",
    function() {

        if (!dataEspecial.value) {

            alert(
                "Escolha uma data!"
            );

            return;
        }


        let confirmar =
            confirm(
                "Tem certeza que deseja remover esse dia especial?"
            );


        if (!confirmar) {
            return;
        }


        fetch(
            "/admin/dia-especial/"
            + dataEspecial.value,
            {
                method: "DELETE"
            }
        )

        .then(function(resposta) {

            return resposta
                .json()
                .then(function(dados) {

                    return {
                        ok: resposta.ok,
                        dados: dados
                    };
                });
        })

        .then(function(resultado) {

            if (!resultado.ok) {

                alert(
                    resultado.dados.erro
                );

                return;
            }


            alert(
                resultado.dados.mensagem
            );


            // A data deixou de ser
            // um dia especial.
            botaoRemoverDia.hidden =
                true;


            // Volta para aberto,
            // pois agora o dia volta
            // a seguir a regra normal.
            document.querySelector(
                'input[name="funcionamento"][value="aberto"]'
            ).checked = true;


            // Limpa os horários
            // especiais da tela.
            listaPeriodos.innerHTML =
                "";


            criarPeriodo(
                "",
                ""
            );


            atualizarFuncionamento();
        })

        .catch(function(erro) {

            console.log(
                "Erro ao remover dia especial:",
                erro
            );

            alert(
                "Não foi possível remover o dia especial."
            );
        });
    }
);