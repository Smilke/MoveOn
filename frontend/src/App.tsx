// src/App.tsx
import { useEffect, useState } from "react";
import { apiGet, apiPost } from "./api/client";
import Upload from "./components/Upload";

type Item = {
  name: string;
  quantity: number;
};

function App() {
  const [health, setHealth] = useState<string>("Carregando...");

  const [items, setItems] = useState<Item[]>([]);
  const [name, setName] = useState("");
  const [quantity, setQuantity] = useState<number>(1);

  // estados da soma
  const [a, setA] = useState<string>("");
  const [b, setB] = useState<string>("");
  const [sumResult, setSumResult] = useState<string>("");

  // chama /api/health ao carregar
  useEffect(() => {
    apiGet("/health")
      .then((data) => setHealth(JSON.stringify(data)))
      .catch((err) => setHealth(`Erro: ${err.message}`));
  }, []);

  const handleCreateItem = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    try {
      await apiPost("/items", {
        name,
        quantity,
      });

      setItems((prev) => [...prev, { name, quantity }]);
      setName("");
      setQuantity(1);
    } catch (err) {
      console.error(err);
    }
  };

  const handleSum = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!a.trim() || !b.trim()) {
      setSumResult("Preencha os dois números.");
      return;
    }

    try {
      const data = await apiGet(`/soma?a=${a}&b=${b}`);
      // data deve ser algo como: { a: 2, b: 3, resultado: 5 }
      setSumResult(`Resultado: ${data.resultado} (a = ${data.a}, b = ${data.b})`);
    } catch (err: any) {
      console.error(err);
      setSumResult(`Erro: ${err.message}`);
    }
  };

  return (
    <div style={{ maxWidth: 600, margin: "0 auto", padding: "1rem" }}>
      <h1>Frontend React + Backend FastAPI</h1>

      {/* HEALTH */}
      <section style={{ marginBottom: "1.5rem" }}>
        <h2>Status da API (GET /api/health)</h2>
        <pre>{health}</pre>
      </section>

      {/* SOMA */}
      <section style={{ marginBottom: "1.5rem" }}>
        <h2>Soma (GET /api/soma?a=&b=)</h2>
        <form onSubmit={handleSum} style={{ marginBottom: "0.5rem" }}>
          <div style={{ marginBottom: "0.5rem" }}>
            <label>
              A:&nbsp;
              <input
                type="number"
                value={a}
                onChange={(e) => setA(e.target.value)}
              />
            </label>
          </div>
          <div style={{ marginBottom: "0.5rem" }}>
            <label>
              B:&nbsp;
              <input
                type="number"
                value={b}
                onChange={(e) => setB(e.target.value)}
              />
            </label>
          </div>
          <button type="submit">Somar</button>
        </form>
        {sumResult && <p>{sumResult}</p>}
      </section>

      <Upload />

      {/* ITENS */}
      <section>
        <h2>Criar item (POST /api/items)</h2>
        <form onSubmit={handleCreateItem} style={{ marginBottom: "1rem" }}>
          <div style={{ marginBottom: "0.5rem" }}>
            <label>
              Nome:{" "}
              <input
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Ex: Caderno"
              />
            </label>
          </div>
          <div style={{ marginBottom: "0.5rem" }}>
            <label>
              Quantidade:{" "}
              <input
                type="number"
                value={quantity}
                onChange={(e) => setQuantity(Number(e.target.value))}
                min={1}
              />
            </label>
          </div>
          <button type="submit">Enviar para API</button>
        </form>

        <h3>Itens criados (apenas no front)</h3>
        <ul>
          {items.map((item, idx) => (
            <li key={idx}>
              {item.name} — {item.quantity}
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}

export default App;
