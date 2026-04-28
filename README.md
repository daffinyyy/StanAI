# StanAI

---

## Visão geral do fluxo

1. **Ingestão** (`ingest.py`) — define a URL base da wiki, baixa conteúdo, cria chunks e persiste vetores em `chroma_dbs/<hash>/` (um diretório por wiki normalizada).
2. **Consulta** — `chat.py` (CLI) ou `api.py` (FastAPI): busca trechos semelhantes, monta contexto e o LLM gera a resposta em português.

---

## Pré-requisitos

| Caminho    | O que você precisa                                                                                             |
| ---------- | -------------------------------------------------------------------------------------------------------------- |
| **Local**  | Python 3.12+, [Ollama](https://ollama.com/download), espaço em disco (PyTorch + modelo de embedding + Chroma). |
| **Docker** | [Docker](https://docs.docker.com/get-docker/) e Docker Compose v2.                                             |

Primeira execução pode demorar: download do modelo de embeddings (Hugging Face) e, no Ollama, do modelo de chat (ex.: `qwen2:7b`).

---

## Tutorial: uso local

### 1. Clonar e instalar dependências

Na pasta do repositório:

```bash
pip install -r requirements.txt
```

### 2. Instalar o modelo de chat no Ollama

```bash
ollama pull qwen2:7b
```

(Outro modelo: defina a variável `OLLAMA_MODEL` e faça o `pull` correspondente.)

### 3. Configurar a wiki na ingestão

Defina a URL base da wiki (ex.: `https://nomedawiki.fandom.com`): em `ingest.py`, altere `fandom_url` (por padrão vem de `DEFAULT_WIKI_BASE_URL` em `rag/wiki_paths.py`, onde você também pode mudar o default do projeto).

### 4. Rodar a ingestão

```bash
python ingest.py
```

- Executa **uma vez** (ou quando quiser reindexar).
- Pode ser **muito lento** em wikis grandes; para testes, prefira wikis pequenas.
- O índice fica em `chroma_dbs/<hash>/`. O legado `./chroma_db` ainda é suportado pela API se existir.

### 5. Conversar

**CLI interativa** (usa `STANAI_WIKI_URL` ou a wiki padrão do código):

```bash
set STANAI_WIKI_URL=https://sua-wiki.fandom.com
python chat.py
```

No PowerShell: `$env:STANAI_WIKI_URL="https://..."` antes de `python chat.py`.

**API HTTP** (em outro terminal):

```bash
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

- Documentação interativa: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Saúde: `GET http://127.0.0.1:8000/health`

Exemplo de pergunta via `POST /chat`:

```bash
curl -s -X POST "http://127.0.0.1:8000/chat" ^
  -H "Content-Type: application/json" ^
  -d "{\"wiki_url\": \"https://sua-wiki.fandom.com\", \"message\": \"Quem é o protagonista?\"}"
```

(No bash/Linux, use `\` em vez de `^` para quebra de linha ou envie o JSON em uma linha só.)

Corpo esperado: `wiki_url` (URL base da wiki) e `message` (pergunta). A resposta inclui `answer`, `sources` (título/seção dos trechos) e `used_legacy_vector_store` se tiver caído no índice antigo.

---

## Tutorial: uso com Docker

### 1. Subir Ollama e a API

Na raiz do repositório:

```bash
docker compose up --build
```

- **Ollama** fica em `http://localhost:11434`.
- **API** em `http://localhost:8000`.

### 2. Baixar o modelo de chat dentro do Ollama

Na primeira vez, em **outro** terminal:

```bash
docker compose exec ollama ollama pull qwen2:7b
```

Aguarde o pull terminar antes de testar o chat, senão as respostas falham.

### 3. Ingestão dentro do container

Ajuste a wiki em `ingest.py` (ou `rag/wiki_paths.py`) como no fluxo local. Depois execute **uma task** com o mesmo código e volumes do Compose:

```bash
docker compose run --rm --no-deps api python ingest.py
```

`--no-deps` evita subir o Ollama só para ingestão (ela usa embeddings locais e HTTP para a Fandom). Os dados do Chroma vão para o volume nomeado `chroma_dbs` e persistem entre reinícios.

### 4. Testar a API

Mesmos endpoints que no modo local (`/docs`, `/health`, `POST /chat`).

### Variáveis úteis (Docker / local)

| Variável          | Descrição                 | Padrão                                                                  |
| ----------------- | ------------------------- | ----------------------------------------------------------------------- |
| `OLLAMA_BASE_URL` | URL do servidor Ollama    | `http://127.0.0.1:11434` (no Compose já aponta para o serviço `ollama`) |
| `OLLAMA_MODEL`    | Nome do modelo Ollama     | `qwen2:7b`                                                              |
| `STANAI_WIKI_URL` | Wiki usada pelo `chat.py` | Valor em `rag/wiki_paths.py`                                            |

---

## Dicas

- Para estimar tamanho da wiki antes da ingestão, você pode usar `teste.py` (o output ajuda a ver quantidade de páginas).
- Documentação da API gerada pelo FastAPI em `/docs` é a referência mais fiel aos campos e exemplos.

---

## Melhorias planejadas

- Suporte a imagens da wiki
- Otimização geral (ingestão e tempo de resposta)
- Estrutura de ingestão em JSON (talvez)
- Modelo de embedding mais leve ou cache agressivo

---

## Limitações

- Respostas dependem do que estiver na wiki e da qualidade do texto extraído.
- Termos muito nichados podem falhar na recuperação ou no modelo.
