# Extrator de Notícias

Automação para extração, análise e armazenamento de notícias via API oficial, seguindo princípios de SOLID, Clean Architecture e Object Calisthenics.

---

## 📋 Sobre o Projeto

Este projeto realiza:
- Busca automatizada de notícias via API oficial
- Filtro por frase de pesquisa, categorias e período
- Análise de ocorrência da frase e detecção de valores monetários
- Download das imagens das notícias
- Armazenamento dos resultados em Excel e imagens em pasta

Tudo isso de forma configurável via `.env` e com arquitetura robusta para manutenção e evolução.

---

## 📚 Sobre o Desafio

Este projeto foi desenvolvido como parte de um desafio técnico, com os seguintes requisitos:
- Buscar notícias via API
- Filtrar por frase, categoria e período
- Salvar resultados em Excel
- Baixar imagens das notícias
- Usar Docker, WSL2 e boas práticas de arquitetura

> 📄 O documento completo do desafio está disponível no arquivo `Desafio técnico Python.pdf` na raiz do projeto.

---

## 🏆 Diferenciais do Projeto
- 100% configurável via `.env`
- Download automático de imagens
- Análise de texto robusta (contagem de frase, detecção de valores monetários)
- Logs detalhados para depuração
- Pronto para extensão (novas fontes de API, novos formatos de saída)

---

## 📁 Estrutura do Projeto

```
src/
├── application/
│   └── use_cases/
│       └── fetch_news_use_case.py
├── domain/
│   ├── entities/
│   │   └── news.py
│   ├── repositories/
│   │   └── news_repository.py
│   └── services/
│       └── news_analyzer.py
├── infrastructure/
│   ├── repositories/
│   │   └── excel_news_repository.py
│   └── clients/
│       └── news_api_client.py
main.py
```

- **main.py**: Ponto de entrada, orquestra o fluxo e injeta dependências
- **application/use_cases**: Casos de uso (fluxos de negócio)
- **domain/entities**: Entidades de domínio (modelos de dados)
- **domain/services**: Regras de negócio puras
- **domain/repositories**: Contratos de persistência
- **infrastructure/clients**: Cliente da API de notícias
- **infrastructure/repositories**: Persistência em Excel e imagens

---

## 🧑‍💻 Princípios e Boas Práticas

### SOLID
- **S (Single Responsibility)**: Cada classe tem uma responsabilidade única
  - `NewsAPIClient`: Responsável apenas pela comunicação com a API
  - `ExcelNewsRepository`: Responsável apenas pelo salvamento em Excel
  - `NewsAnalyzer`: Responsável apenas pela análise de texto das notícias

- **O (Open/Closed)**: Extensível sem modificar código existente
  - Para adicionar suporte a outra fonte de notícias (ex: Reuters, uma das maiores agências de notícias do mundo), basta criar nova classe implementando a mesma interface
  - Para mudar o formato de saída (ex: CSV), basta criar novo repositório sem alterar os existentes

- **L (Liskov Substitution)**: Implementações concretas substituem abstrações
  - `ExcelNewsRepository` implementa `NewsRepository` e pode ser usado em qualquer lugar que espere um repositório
  - `NewsAPIClient` implementa a interface de cliente de API e pode ser substituído por outros clientes

- **I (Interface Segregation)**: Interfaces enxutas e específicas
  - `NewsRepository` define apenas métodos essenciais: `save_news()` e `save_image()`
  - Interfaces pequenas facilitam implementações e testes

- **D (Dependency Inversion)**: Dependências de abstrações
  - `FetchNewsUseCase` recebe `NewsRepository` como abstração, não implementação específica
  - Facilita testes unitários e troca de implementações

### Clean Architecture
- **Separação em Camadas**:
  - `domain/`: Entidades e regras de negócio (ex: `News`, `NewsAnalyzer`)
  - `application/`: Casos de uso (ex: `FetchNewsUseCase`)
  - `infrastructure/`: Implementações concretas (ex: `NewsAPIClient`, `ExcelNewsRepository`)

- **Independência de Frameworks**:
  - Domínio não conhece detalhes de API ou Excel
  - Regras de negócio isoladas em `NewsAnalyzer`
  - Fácil trocar implementações sem afetar lógica

### Object Calisthenics
- **Métodos Pequenos e Claros**:
  ```python
  # Antes
  def process_article(self, article):
      # Muitas responsabilidades em um método

  # Depois
  def _extract_article_data(self, doc):
      # Extrai dados básicos
  def _extract_image_url(self, doc):
      # Extrai URL da imagem
  def _build_request_params(self, begin_date, end_date):
      # Monta parâmetros da requisição
  ```

- **Nomes Descritivos**:
  - `fetch_news()` em vez de `get()`
  - `save_image()` em vez de `save_img()`
  - `build_categories_filter()` em vez de `build_filter()`

- **Classes Coesas**:
  - `News`: Representa uma notícia com seus atributos
  - `NewsAnalyzer`: Análise de texto isolada
  - `NewsAPIClient`: Comunicação com API específica

- **Encapsulamento**:
  - Métodos privados com `_` (ex: `_extract_article_data`)
  - Dados protegidos em classes
  - Acesso controlado via métodos públicos

### Exemplos de Aplicação
```python
# Dependência de Abstração (DIP)
class FetchNewsUseCase:
    def __init__(self, repository: NewsRepository):  # Recebe interface, não implementação
        self.repository = repository

# Responsabilidade Única (SRP)
class NewsAnalyzer:
    @staticmethod
    def analyze_news(title, description, search_phrase):
        # Apenas análise de texto, sem lógica de API ou salvamento

# Interface Segregada (ISP)
class NewsRepository(ABC):
    @abstractmethod
    def save_news(self, news_list: List[News]):
        pass
    
    @abstractmethod
    def save_image(self, url: str, filename: str):
        pass
```

---

## 🐳 Configuração Docker

O projeto usa Docker para garantir consistência entre ambientes. Principais características:

### Sequência de Execução

Quando você executa `docker-compose up`, a seguinte sequência ocorre:

1. **Dockerfile (Construção da Imagem)**
   - Usa Python 3.11-slim como base
   - Instala dependências do Python
   - Copia o código fonte
   - Configura o ambiente
   - Define o comando padrão

2. **Docker Compose (Orquestração)**
   - Usa a imagem construída
   - Configura volumes para persistência
   - Injeta variáveis de ambiente
   - Inicia o container

### Dockerfile
- Imagem base: Python 3.11-slim
- Instala apenas dependências necessárias
- Configura ambiente de execução

### Docker Compose
- Gerencia volumes para persistência de dados
- Configura variáveis de ambiente
- Permite sobrescrever configurações via variáveis de ambiente

### Volumes
- `./images:/app/images`: Persiste imagens baixadas
- `./news_results.xlsx:/app/news_results.xlsx`: Persiste resultados

---

## ⚙️ Variáveis de Ambiente (`.env`)

O projeto usa variáveis de ambiente para configuração. Para começar:

1. Copie o arquivo `.env.example` para `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edite o arquivo `.env` com suas configurações:
   ```env
   # Chave da API (obtenha em: https://developer.newsapi.org)
   API_KEY=your_api_key_here
   
   # URL da API
   API_URL=https://api.newsapi.org/v2/everything
   
   # User-Agent para requisições HTTP
   USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36
   
   # URL base para imagens
   IMAGE_BASE_URL=https://static.newsapi.org
   
   # Caminho do arquivo Excel de saída
   EXCEL_PATH=news_results.xlsx
   
   # Pasta para salvar imagens
   IMAGES_DIR=images
   
   # Pasta para salvar logs (padrão: logs)
   LOG_DIR=logs
   
   # Frase de busca
   SEARCH_PHRASE=your_search_phrase_here
   
   # Categorias de notícias (separadas por vírgula)
   CATEGORIES=business,health,technology,world,u.s.,politics,arts,opinion
   
   # Quantidade de meses para buscar notícias
   MONTHS_TO_SEARCH=2
   ```

3. **Importante**: 
   - Nunca comite o arquivo `.env` no Git
   - O arquivo `.env.example` serve como template
   - Mantenha suas chaves de API seguras
   - A variável `LOG_DIR` define onde os arquivos de log serão salvos (padrão: logs)

---

## 🚀 Como Executar

### Usando Docker (Recomendado)

1. **Clone o repositório**
2. **Crie o arquivo `.env` na raiz** (veja exemplo acima)
3. **Execute o container:**

   ```bash
   # Execução básica
   docker-compose up --build

   # Execução com variáveis personalizadas
   SEARCH_PHRASE="biden" CATEGORIES="politics,world" docker-compose up

   # Execução com arquivo .env personalizado
   docker-compose --env-file .env.custom up
   ```

4. **Opções de execução:**
   - Use variáveis de ambiente para sobrescrever configurações
   - Crie diferentes arquivos .env para diferentes cenários
   - As variáveis de ambiente têm prioridade sobre o arquivo .env

### Execução Local

```bash
pip install -r requirements.txt
python main.py
```

### Exemplos de Uso
```bash
# Busca por "biden" em política
SEARCH_PHRASE="biden" CATEGORIES="politics" docker-compose up

# Busca por "climate" em tecnologia e ciência
SEARCH_PHRASE="climate" CATEGORIES="technology,science" docker-compose up

# Busca por "sports" nos últimos 3 meses
SEARCH_PHRASE="sports" MONTHS_TO_SEARCH=3 docker-compose up
```

---

## 🧪 Testes

### Como executar os testes localmente

Recomendamos o uso do **pytest** para rodar os testes, pois oferece uma saída mais amigável e recursos avançados.

1. **Crie e ative um ambiente virtual:**

   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Linux/Mac:
   source .venv/bin/activate
   ```

2. **Instale as dependências:**

   ```bash
   pip install -r requirements.txt
   pip install pytest
   ```

3. **Execute os testes:**

   Para executar os testes e ver o resultado de cada teste individualmente, utilize o comando:

   ```bash
   pytest -v
   ```

   Para executar um arquivo de teste específico, por exemplo, o de integração:

   ```bash
   pytest -v tests/integration/test_news_fetch.py
   ```

   Exemplo de saída do comando:
   ```
   ================================================================================ test session starts ================================================================================
   platform win32 -- Python 3.10.2, pytest-8.0.0, pluggy-1.6.0
   cachedir: .pytest_cache
   rootdir: C:\Users\Bruno Cosmo\Desafio Tecnico One4Tech
   plugins: cov-4.1.0
   collected 2 items                                                                                                                                                                    

   tests/integration/test_news_fetch.py::TestNewsFetch::test_fetch_news_empty_categories PASSED                                                                                   [ 50%]
   tests/integration/test_news_fetch.py::TestNewsFetch::test_fetch_news_success PASSED                                                                                            [100%]

   ================================================================================= 2 passed in 3.32s ================================================================================= 
   ```

4. **Desative o ambiente virtual ao finalizar:**

   ```bash
   deactivate
   ```

---

## 👨‍ Autor
Bruno Cosmo