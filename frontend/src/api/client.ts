// src/api/client.ts
const API_URL = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000/api";

export async function apiGet(path: string) {
  const res = await fetch(`${API_URL}${path}`);

  if (!res.ok) {
    throw new Error(`Erro na requisição: ${res.status}`);
  }

  return res.json();
}

export async function apiPost(path: string, body: unknown) {
  const res = await fetch(`${API_URL}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    throw new Error(`Erro na requisição: ${res.status}`);
  }

  return res.json();
}

export async function apiPostForm(path: string, formData: FormData) {
  const res = await fetch(`${API_URL}${path}`, {
    method: "POST",
    body: formData,
  });

  const text = await res.text();
  if (!res.ok) {
    // tenta parsear JSON de erro quando possível
    let detail = text;
    try {
      const j = JSON.parse(text);
      detail = j.detail ?? JSON.stringify(j);
    } catch (_) {}
    throw new Error(`Erro na requisição: ${res.status} - ${detail}`);
  }

  try {
    return JSON.parse(text);
  } catch (_) {
    return text;
  }
}
