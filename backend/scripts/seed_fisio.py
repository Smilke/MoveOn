import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError

url = "http://127.0.0.1:8000/api/fisioterapeutas"

# dados de exemplo - ajuste conforme precisar
payload = {
    "nome": "João Silva",
    "cpf": "12345678901",
    "registro": "CRF-12345",
    "email": "joao.silva@example.com",
    "cnpj": ""
}

data = json.dumps(payload).encode("utf-8")
req = Request(url, data=data, method="POST")
req.add_header("Content-Type", "application/json")

try:
    with urlopen(req) as resp:
        body = resp.read().decode("utf-8")
        print("Status:", resp.status)
        print("Resposta:", body)
except HTTPError as e:
    print("Erro ao criar fisioterapeuta:", e.code)
    try:
        print(e.read().decode())
    except Exception:
        pass
except Exception as e:
    print("Erro de conexão:", e)
