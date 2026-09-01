# Sistema de Agendamento para Barbearia

Sistema web de agendamento para barbearia desenvolvido com **Python, Flask, SQLite, HTML, CSS e JavaScript**.

O projeto nasceu como uma aplicação executada pelo terminal e evoluiu para um sistema web com autenticação, perfis de acesso, agendas individuais por profissional, regras de disponibilidade e gerenciamento da equipe.

O objetivo é simular um sistema real de agendamentos e aplicar, na prática, conceitos de desenvolvimento web, banco de dados, segurança, regras de negócio e versionamento de código.

---

## Sobre o projeto

A primeira versão do sistema foi desenvolvida inteiramente em Python e executada pelo terminal.

Essa etapa inicial permitiu praticar a lógica principal de um sistema de agendamentos, como escolha de serviço, seleção de horários, validações e persistência em JSON.

Com a evolução do projeto, a aplicação passou a utilizar **Flask** no back-end e **HTML, CSS e JavaScript** no front-end.

Atualmente, a versão web possui suporte a múltiplos profissionais, autenticação individual, diferentes níveis de acesso e armazenamento dos principais dados em **SQLite**.

---

## Funcionalidades atuais

### Agendamento do cliente

- Cadastro do nome e celular do cliente
- Formatação automática do número de celular
- Escolha do serviço
- Escolha do profissional
- Geração dinâmica das datas disponíveis
- Geração dos horários disponíveis de acordo com o profissional escolhido
- Bloqueio de horários ocupados
- Verificação da duração do serviço
- Confirmação do agendamento
- Validação dos dados no front-end e no back-end

### Agenda por profissional

Cada profissional possui sua própria agenda.

Isso permite, por exemplo:

```text
Pedro → 14:00 → Cliente A
João  → 14:00 → Cliente B
```

Os dois atendimentos podem acontecer ao mesmo tempo porque pertencem a profissionais diferentes.

Por outro lado, o sistema impede conflitos dentro da agenda do mesmo profissional.

### Área interna

Cada integrante da equipe possui login individual.

Os perfis disponíveis são:

- **Proprietário**
- **Líder**
- **Colaborador**

O sistema controla o acesso às funcionalidades de acordo com o perfil do usuário.

### Minha Agenda

O profissional pode visualizar seus próximos agendamentos com informações como:

- Data
- Horário
- Nome do cliente
- Celular
- Serviço
- Valor

Também é possível cancelar um agendamento.

O cancelamento não remove definitivamente o registro do banco, permitindo preservar o histórico.

### Agendas da equipe

O **Proprietário** e o **Líder** podem:

- Visualizar os próximos agendamentos da barbearia
- Filtrar a agenda por profissional
- Consultar os dados necessários para o atendimento
- Cancelar agendamentos quando necessário

### Gerenciamento da equipe

O **Proprietário** pode:

- Adicionar colaboradores
- Editar nome e login
- Definir o perfil como Líder ou Colaborador
- Redefinir senha
- Remover o acesso de um usuário
- Reativar um usuário
- Controlar se um profissional está disponível para receber novos agendamentos

Os usuários são desativados em vez de apagados definitivamente, preservando a relação com registros históricos.

### Disponibilidade dos profissionais

O acesso ao sistema e a disponibilidade para receber clientes são tratados separadamente.

Por exemplo, um profissional pode continuar com acesso ao painel, mas ficar temporariamente indisponível para novos agendamentos durante:

- Férias
- Folgas
- Ausências temporárias

Quando um profissional está indisponível, ele deixa de aparecer para o cliente na etapa de escolha do profissional.

### Dias e horários especiais

O sistema permite configurar dias diferentes do funcionamento normal, como:

- Feriados
- Aberturas excepcionais
- Dias fechados
- Horários especiais
- Períodos diferentes de atendimento no mesmo dia

Antes de alterar um dia especial, o back-end verifica se a mudança deixaria algum agendamento existente fora do horário permitido.

---

## Perfis e permissões

| Funcionalidade | Colaborador | Líder | Proprietário |
| --- | :---: | :---: | :---: |
| Acessar o sistema | ✅ | ✅ | ✅ |
| Visualizar a própria agenda | ✅ | ✅ | ✅ |
| Cancelar o próprio agendamento | ✅ | ✅ | ✅ |
| Visualizar agendas da equipe | ❌ | ✅ | ✅ |
| Cancelar agendamento de outro profissional | ❌ | ✅ | ✅ |
| Configurar dias e horários especiais | ❌ | ✅ | ✅ |
| Gerenciar colaboradores | ❌ | ❌ | ✅ |
| Alterar cargos | ❌ | ❌ | ✅ |
| Redefinir senha de colaboradores | ❌ | ❌ | ✅ |
| Controlar disponibilidade dos profissionais | ❌ | ✅ | ✅ |

---

## Regras de negócio implementadas

O sistema considera regras reais de funcionamento da barbearia.

- Funcionamento padrão de **terça-feira a sábado**
- Domingo e segunda-feira ficam fechados na regra normal
- Datas disponíveis são calculadas a partir da data atual
- O cliente pode agendar até **14 dias à frente**
- O agendamento deve possuir pelo menos **30 minutos de antecedência**
- Os horários são trabalhados em intervalos de 30 minutos
- Cada serviço possui duração própria
- Um serviço só pode ser iniciado se couber completamente no período de funcionamento
- Horários ocupados são calculados por profissional
- Dois profissionais podem atender clientes diferentes no mesmo horário
- Um profissional não pode possuir atendimentos conflitantes
- Dias especiais substituem as regras normais daquele dia
- Alterações administrativas não podem invalidar agendamentos existentes

### Serviços cadastrados atualmente

| Serviço | Duração | Valor |
| --- | ---: | ---: |
| Corte | 30 min | R$ 30,00 |
| Barba | 30 min | R$ 20,00 |
| Corte + Barba | 60 min | R$ 45,00 |

---

## Tecnologias utilizadas

### Back-end

- Python 3
- Flask
- SQLite
- Biblioteca `sqlite3`
- Sessões do Flask
- Hash de senhas

### Front-end

- HTML5
- CSS3
- JavaScript
- Manipulação do DOM
- Fetch API
- Layout responsivo

### Persistência

- **SQLite** para usuários e agendamentos
- **JSON** para dias e horários especiais
- Suporte à migração dos agendamentos antigos em JSON para SQLite

### Versionamento

- Git
- GitHub

---

## Banco de dados

O arquivo principal do banco é:

```text
barbearia.db
```

Ele é criado localmente e **não deve ser enviado ao GitHub**.

O SQLite armazena dados como:

- Usuários
- Perfis de acesso
- Hash das senhas
- Status dos usuários
- Disponibilidade para receber agendamentos
- Agendamentos
- Profissional responsável
- Status do agendamento
- Informações de cancelamento

O sistema também possui suporte para migrar registros do antigo `agendamentos.json` para o SQLite.

---

## Estrutura atual do projeto

```text
AgendaBarbearia/
│
├── app.py
├── banco.py
├── sistema_agendamento.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── agendamentos.json       # arquivo legado/local
├── dias_especiais.json     # configurações locais
├── barbearia.db            # banco SQLite local
│
├── templates/
│   ├── index.html
│   ├── login.html
│   ├── painel.html
│   ├── minha_agenda.html
│   ├── agendas_equipe.html
│   ├── equipe.html
│   └── admin.html
│
└── static/
    ├── css/
    │   └── style.css
    │
    ├── js/
    │   ├── script.js
    │   └── admin.js
    │
    └── img/
        └── logo.png
```

> Os arquivos `barbearia.db`, `agendamentos.json` e `dias_especiais.json` armazenam dados locais e podem ser ignorados pelo Git conforme a configuração do `.gitignore`.

---

## Como executar

### 1. Clone o repositório

```bash
git clone https://github.com/PedroIRanz/AgendaBarbearia.git
```

### 2. Entre na pasta do projeto

```bash
cd AgendaBarbearia
```

### 3. Crie um ambiente virtual

No Windows:

```bash
python -m venv venv
```

Ative o ambiente:

```bash
venv\Scripts\activate
```

### 4. Instale as dependências

```bash
pip install -r requirements.txt
```

### 5. Crie o banco e o primeiro Proprietário

Como o banco local não é enviado para o GitHub, execute:

```bash
python banco.py
```

O terminal solicitará:

- Nome do Proprietário
- Login
- Senha
- Confirmação da senha

A senha não é armazenada em texto puro.

### 6. Execute a aplicação Flask

```bash
python app.py
```

Depois, abra no navegador o endereço informado pelo Flask, normalmente:

```text
http://127.0.0.1:5000
```

---

## Segurança e dados locais

Alguns arquivos não devem ser enviados ao repositório porque podem conter dados locais ou informações sensíveis.

Exemplo de `.gitignore`:

```gitignore
__pycache__/
*.pyc

venv/
.venv/

agendamentos.json
dias_especiais.json
barbearia.db
.env

pasta/
```

As senhas dos usuários são armazenadas utilizando **hash**, e não em texto puro.

Em um ambiente de produção, a chave secreta utilizada pelas sessões do Flask deve ser configurada por variável de ambiente.

---

## Evolução do projeto

O projeto começou com:

```text
Python
↓
Aplicação no terminal
↓
Persistência em JSON
```

E atualmente possui:

```text
Python + Flask
↓
HTML + CSS + JavaScript
↓
SQLite
↓
Autenticação
↓
Controle de permissões
↓
Múltiplos profissionais
↓
Agendas independentes
↓
Painel administrativo
```

Essa evolução faz parte do objetivo do projeto: desenvolver novas funcionalidades gradualmente enquanto os conceitos são estudados e aplicados.

---

## O que estou aprendendo com o projeto

Durante o desenvolvimento estou praticando conceitos como:

- Lógica de programação
- Funções
- Listas e dicionários
- Estruturas condicionais
- Estruturas de repetição
- Manipulação de arquivos JSON
- SQLite e banco de dados relacional
- Persistência de dados
- Relacionamento entre registros
- Validação de dados
- Organização e modularização de código
- Desenvolvimento web com Flask
- Rotas HTTP
- Sessões e autenticação
- Controle de acesso por perfil
- Armazenamento seguro de senhas
- HTML e CSS
- JavaScript
- Manipulação do DOM
- Eventos em JavaScript
- Fetch API
- Manipulação de datas
- Regras de negócio
- Git e GitHub
- Desenvolvimento responsivo

---

## Próximas etapas

Algumas melhorias planejadas para as próximas versões:

- Permitir que cada usuário altere a própria senha
- Melhorar o fluxo de redefinição de senha
- Criar pesquisa e histórico de clientes
- Criar relatórios da barbearia
- Criar indicadores de atendimentos e faturamento
- Migrar dias especiais de JSON para SQLite
- Melhorar testes automatizados
- Reforçar as proteções de segurança para ambiente de produção
- Continuar melhorando acessibilidade e responsividade
- Preparar a aplicação para publicação em um servidor

---

## Status do projeto

**Em desenvolvimento**

A versão web já possui o fluxo principal de agendamento e gerenciamento funcionando, mas novas funcionalidades e melhorias continuam sendo implementadas e testadas.

A versão original em terminal permanece como parte do histórico de evolução do projeto.

---

## Autor

**Pedro Ranz**

GitHub: https://github.com/PedroIRanz
