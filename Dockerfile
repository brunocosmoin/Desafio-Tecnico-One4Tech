# Imagem base: Python 3.9 com versão slim (menor tamanho, mantém apenas o essencial)
FROM python:3.9-slim

# Define o diretório de trabalho dentro do container
# Todas as operações seguintes serão executadas neste diretório
WORKDIR /app

# Copia apenas o arquivo de requisitos primeiro
# Isso permite que o Docker use cache nas camadas
# Se requirements.txt não mudar, não precisa reinstalar as dependências
COPY requirements.txt .

# Instala as dependências Python listadas em requirements.txt
# --no-cache-dir: não armazena cache do pip (reduz tamanho da imagem)
# O Docker ainda mantém seu próprio cache de camadas
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código fonte para o container
# Isso é feito depois de instalar dependências para aproveitar o cache do Docker
# Se apenas o código mudar (e não requirements.txt), o Docker reutiliza a camada com as dependências
COPY . .

# Cria diretório para armazenar as imagens baixadas
# -p: cria diretório pai se não existir
RUN mkdir -p /app/images

# Configura variável de ambiente para Python
# PYTHONUNBUFFERED=1: força o Python a não usar buffer de saída
# Isso garante que os logs apareçam em tempo real no console
ENV PYTHONUNBUFFERED=1

# Define o comando que será executado quando o container iniciar
# Neste caso, executa o script principal Python
CMD ["python", "main.py"] 