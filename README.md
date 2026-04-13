# teste_StanAI

## 📋 Requisitos

1. Instalar o [Ollama](https://ollama.com/download)  
2. Após a instalação, executar no terminal: `ollama pull qwen2:7b`
3. Na pasta do repositório, instalar as dependências: `pip install -r requirements.txt`

---

## 🚀 Como rodar

1. No arquivo `ingest.py`, insira a URL da wiki Fandom que deseja usar.
2. Execute a ingestão com `python ingest.py`  
⚠️ **Importante:**  
- Esse processo é **MUITO demorado**, mas executado apenas uma vez
- Ele cria o banco vetorial (`chroma_db`)
- Para testes rápidos, use wikis pequenas (menos de 100 páginas)  
💡 Dica:  
Você pode verificar quantas páginas uma wiki possui usando o arquivo `teste.py` — o primeiro número do output indica a quantidade.

3. Após a ingestão, inicie o chat com `python chat.py`

---

## 🔧 Melhorias necessárias

- Suporte a imagens da wiki
- Otimização geral (ingestão e tempo de resposta)
- Estrutura de ingestão em JSON (talvez)
- Uso de um modelo de embedding que tenha um processamento menos lento

---

## ⚠️ Limitações

- Pode ter dificuldade com **termos muito nichados**
- Depende da qualidade das informações disponíveis na wiki (conteúdo da comunidade)
