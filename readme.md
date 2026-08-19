# Sistema de Agendamentos para Barbearia

Sistema de agendamento para barbearia desenvolvido inicialmente em Python pelo terminal e atualmente em evolução para uma aplicação web utilizando Flask.

O projeto tem como objetivo simular um sistema real de agendamentos, permitindo aplicar conceitos de programação, desenvolvimento web, regras de negócio e, futuramente, banco de dados.

---

## Sobre o projeto

A primeira versão do sistema foi desenvolvida inteiramente em Python e executada pelo terminal.

Nessa versão, o cliente pode escolher um serviço, selecionar um dia e horário disponível e realizar um agendamento.

Os agendamentos são armazenados em um arquivo JSON, utilizado como forma inicial de persistência de dados.

Após finalizar essa primeira etapa, o projeto começou a evoluir para uma aplicação web utilizando Flask, HTML, CSS e JavaScript.

A versão web está atualmente em desenvolvimento.

---

## Funcionalidades da versão em terminal

- Cadastro de novos agendamentos
- Escolha de serviço
- Escolha de dia
- Escolha de horário
- Validação do nome do cliente
- Verificação de horários já ocupados
- Cancelamento de agendamentos
- Visualização dos agendamentos
- Persistência dos dados em JSON

---

## Versão Web — Em desenvolvimento

A nova versão está sendo desenvolvida utilizando Flask como framework web.

Atualmente estão sendo desenvolvidas as seguintes funcionalidades:

- Página inicial da barbearia
- Modal para realização do agendamento
- Cadastro do nome do cliente
- Cadastro do celular
- Seleção de serviços através de cartões
- Destaque visual do serviço selecionado
- Geração dinâmica das datas disponíveis
- Funcionamento de terça-feira a sábado
- Limite de agendamento para até 14 dias à frente
- Interface adaptada para facilitar o uso do sistema

---

## Regras de negócio planejadas

O sistema deverá considerar algumas regras da barbearia durante o agendamento:

- Funcionamento padrão de terça-feira a sábado
- Domingo e segunda-feira não possuem atendimento
- Datas disponíveis são calculadas a partir da data atual
- Agendamentos podem ser realizados somente dentro do período permitido
- Horários disponíveis dependem dos agendamentos existentes
- Serviços podem possuir durações diferentes
- Alguns serviços poderão possuir tempo de espera durante o atendimento
- Horários ocupados não poderão ser selecionados
- Feriados e horários especiais poderão ser configurados pelo administrador

---

## Tecnologias utilizadas

### Back-end

- Python 3
- Flask
- JSON

### Front-end

- HTML5
- CSS3
- JavaScript

### Versionamento

- Git
- GitHub

---

## Estrutura atual do projeto

```text
AgendaBarbearia/
│
├── app.py
├── sistema_agendamento.py
├── agendamentos.json
├── requirements.txt
├── README.md
├── .gitignore
│
├── templates/
│   └── index.html
│
└── static/
    ├── css/
    │   └── style.css
    │
    ├── js/
    │   └── script.js
    │
    └── img/
        └── logo.png
```

---

## Como executar

Clone o repositório:

```bash
git clone https://github.com/PedroIRanz/AgendaBarbearia.git
```

Entre na pasta do projeto:

```bash
cd AgendaBarbearia
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Execute a aplicação Flask:

```bash
python app.py
```

Depois, acesse no navegador o endereço informado pelo Flask no terminal.

A versão original também pode ser executada pelo terminal:

```bash
python sistema_agendamento.py
```

---

## O que estou aprendendo com o projeto

Durante o desenvolvimento estou praticando conceitos como:

- Lógica de programação
- Funções
- Listas e dicionários
- Estruturas condicionais
- Estruturas de repetição
- Manipulação de arquivos JSON
- Persistência de dados
- Validação de dados
- Organização e modularização de código
- Desenvolvimento web com Flask
- HTML e CSS
- JavaScript
- Manipulação do DOM
- Eventos em JavaScript
- Manipulação de datas
- Regras de negócio
- Git e GitHub

---

## Próximas etapas

- Finalizar a seleção dinâmica de datas
- Criar seleção de horários disponíveis
- Considerar a duração de cada serviço
- Integrar o formulário web com o back-end Flask
- Substituir a persistência em JSON por banco de dados SQLite
- Criar login de administrador
- Permitir alteração e cancelamento de agendamentos
- Configurar feriados e horários especiais
- Criar pesquisa de clientes
- Criar relatórios
- Melhorar responsividade e acessibilidade da interface
- Implementar validações no front-end e no back-end

---

## Status do projeto

 **Em desenvolvimento**

A versão em terminal está funcional.

A versão web está sendo desenvolvida gradualmente, com novas funcionalidades sendo implementadas e testadas.

---

## Autor

Pedro Ranz

GitHub: https://github.com/PedroIRanz