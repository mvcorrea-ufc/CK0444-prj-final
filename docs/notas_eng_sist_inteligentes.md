# Notas de Aula - Engenharia de Sistemas Inteligentes (CK0444)

Departamento de Computação - Bacharelado em Ciência de Dados  
Professor: Lincoln S. Rocha  
Semestre Letivo: 2025.1

---

## Aula 10 - Integração Contínua

### Build e Testes Automatizados com Poetry

**Poetry** é uma ferramenta moderna para gerenciamento de dependências, ambientes virtuais e empacotamento, substituindo `requirements.txt`, `setup.py` e `virtualenv`. Tem foco em reprodutibilidade e simplicidade.

#### Arquitetura:
- `pyproject.toml`: arquivo único de configuração.
- `poetry.lock`: bloqueia versões para consistência.
- Ambientes isolados por projeto (venv embutido).

#### Comandos Básicos:
```bash
$ pip install poetry
$ curl -sSL https://install.python-poetry.org | python3 -
$ poetry new projeto
$ poetry init
$ poetry add pacote
$ poetry remove pacote
$ poetry install
$ poetry env use python3.11
$ poetry run pytest tests/
$ poetry build
$ poetry publish
```

### Integração Contínua com GitHub Actions

**CI** (Integração Contínua) significa integrar o código com frequência, idealmente uma vez ao dia. Prática originada do XP (Extreme Programming).

#### Boas práticas:
- Programação em pares
- Testes automatizados
- Build automatizado

#### Componentes de um servidor CI:
1. Commit no repositório Git
2. Notificação ao servidor CI
3. Execução de build e testes

GitHub Actions é uma ferramenta popular para isso.

---

## Aula 11 - Introdução a DevOps, DataOps e MLOps

### O que mudou no desenvolvimento de software?

- Da entrega tradicional para entrega contínua.
- Foco em velocidade, qualidade e automação.

### Cultura DevOps, DataOps e MLOps
- Colaborativa
- Quebra de silos
- Automação como pilar

### DevOps
- Integração entre desenvolvimento e operações
- Objetivo: entrega rápida e confiável de software

#### Princípios:
- CI/CD
- Infraestrutura como código
- Monitoramento contínuo

### DataOps
- Aplicação de práticas DevOps a dados
- Foco em automação de pipelines, governança de dados

#### Princípios:
- Pipelines automatizados
- Versionamento de dados
- Testes automatizados em dados
- Monitoramento de qualidade

### MLOps
- Práticas DevOps aplicadas a ML
- Foco em automação do ciclo de vida do modelo

#### Princípios:
- Reprodutibilidade
- Automação de treino, validação, teste e deploy
- Monitoramento de performance e drift

### Comparação
| Aspecto     | DevOps      | DataOps     | MLOps       |
|-------------|-------------|-------------|-------------|
| Foco        | Software    | Dados       | Modelos     |
| Objetivo    | Entrega CI  | Qualidade   | Gestão ciclo ML |
| Ferramentas | Jenkins, Docker | Airflow, dbt | MLflow, Kubeflow |
| Desafios    | Integração Dev-Ops | Governança | Integração e retraining |

---

## Aula 12 - Predição de Defeitos de Software (PDS)

### Definições
- Sistema computacional interage com outros sistemas através de sua interface de serviço.
- Falta → Erro → Falha

### Glossário:
- **Defeito**: erro no código
- **Falha**: comportamento incorreto observável

### Objetivos da PDS:
- Estimar número de defeitos remanescentes
- Classificar módulos com propensão a defeitos
- Descobrir associações entre métricas e defeitos

### Métricas de Software
- Diretas e derivadas
- Objetivas e subjetivas
- Produto e processo

#### Classificação:
- Métricas de mudança
- Métricas de código (ex: WMC, DIT, CBO, RFC, LCOM)
- Métricas organizacionais
- Histórico de defeitos

### Machine Learning para PDS

Problema de Classificação:
- Entrada: métricas de software
- Saída: presença ou não de defeito

Modelos usados:
- SVM, Redes Neurais, Random Forest, etc.

Pipeline:
- ETL → extração de dados
- Construção do modelo
- Liberação do modelo

---

## Aula 13 - Pipeline de Dados - Parte I

### Estratégia de Identificação de Commits
- Foco em período entre releases (ex: 1.0.0 a 1.2.0)
- Identificar commits de bug-fixing
- Rótulo: arquivos afetados por esses commits = defeituosos

### Ferramentas
- Sistema de Bug Track (Jira, GitHub Issues)
- PyDriller: mineração de repositórios Git
- Tree-sitter e AST: extração de métricas
- GitHub API e Python-Jira: automação da mineração de dados

### Consulta de bugs
- Jira: `project = ... AND type = Bug AND status in (Closed)`
- GitHub: `is:issue state:closed label:kind:bug`

### Extração de Dados
- Mensagens de commit
- Issues associadas
- Cálculo de métricas
- Construção de datasets para ML

---

