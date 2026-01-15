## MoveOn – Backend (FastAPI) + Frontend (React)

Projeto base com:

- **Backend** em Python usando **FastAPI**
- **Frontend** em **React + Vite + TypeScript**
- Comunicação via HTTP entre front (`localhost:5173`) e back (`localhost:8000`)

### ✅ Pré-requisitos

- Python 3.10+

- Node.js 18+ (ou versão LTS recente)

- npm (vem junto com o Node)

- Git (opcional, mas recomendado)

### 🚀 Backend – FastAPI
1. Entrar na pasta do backend
```cd backend```

2. Criar e ativar o ambiente virtual
```python -m venv .venv```
    - Linux
```source .venv/bin/activate```
    - Windows (PowerShell)
```.venv\Scripts\Activate.ps1```

3. Instalar dependências
```pip install -r requirements.txt```

4. Rodar o servidor

    - Ainda dentro de backend/:

        ```uvicorn app.main:app --reload```


    - A API sobe em:
        http://127.0.0.1:8000

5. Documentação interativa

    - Swagger UI:
        http://127.0.0.1:8000/docs

### 🧪 Testes

Backend (pytest):

1. Dentro de `backend` crie e ative o virtualenv e instale dependências:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Rodar os testes:

```bash
pytest
```

Frontend (Vitest):

1. Instalar dependências e rodar testes:

```bash
cd frontend
npm install
npm test
```


### 🎨 Frontend – React + Vite + TypeScript
1. Entrar na pasta do frontend

    Em outro terminal:
    ```cd frontend```

2. Instalar dependências
```npm install```

3. Arquivo .env do frontend

    Crie um frontend/.env:

    ```VITE_API_URL="http://127.0.0.1:8000/api"```

Esse valor deve bater com o API_PREFIX do backend.

4. Rodar o frontend
```npm run dev```


- A aplicação abre em:
http://localhost:5173