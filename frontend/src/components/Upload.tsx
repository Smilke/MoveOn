import React, { useEffect, useState } from "react";
import { apiPostForm } from "../api/client";

export default function Upload() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [status, setStatus] = useState<string>("");
  const [patientId, setPatientId] = useState<string>("");
  const [exerciseId, setExerciseId] = useState<string>("");
  const [analysis, setAnalysis] = useState<any>(null);

  useEffect(() => {
    if (!file) {
      setPreview(null);
      return;
    }

    const url = URL.createObjectURL(file);
    setPreview(url);

    return () => URL.revokeObjectURL(url);
  }, [file]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files && e.target.files[0];
    setFile(f ?? null);
    setStatus("");
    setAnalysis(null);
  };

  const handleUpload = async () => {
    if (!file) return setStatus("Selecione um arquivo primeiro.");

    setStatus("Enviando...");
    const fd = new FormData();
    fd.append("file", file);
    if (patientId) fd.append("patient_id", patientId);
    if (exerciseId) fd.append("exercise_id", exerciseId);

    try {
      const data = await apiPostForm("/upload/video", fd);
      setStatus(`Upload concluído: ${data.filename}`);
      setAnalysis(data.analysis ?? null);
      setFile(null);
    } catch (err: any) {
      setStatus(`Erro: ${err.message}`);
    }
  };

  const API_URL = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000/api";

  return (
    <section style={{ marginTop: "1.5rem" }}>
      <h2>Upload de Vídeo (POST /api/upload/video)</h2>

      <div style={{ marginBottom: "0.5rem" }}>
        <label>
          Patient ID:&nbsp;
          <input value={patientId} onChange={(e) => setPatientId(e.target.value)} placeholder="ex: p123" />
        </label>
      </div>

      <div style={{ marginBottom: "0.5rem" }}>
        <label>
          Exercise ID:&nbsp;
          <input value={exerciseId} onChange={(e) => setExerciseId(e.target.value)} placeholder="ex: squat" />
        </label>
      </div>

      <div style={{ marginBottom: "0.5rem" }}>
        <input type="file" accept="video/*" onChange={handleChange} />
      </div>

      {preview && (
        <div style={{ marginBottom: "0.5rem" }}>
          <video src={preview} controls style={{ maxWidth: "100%" }} />
        </div>
      )}

      <div>
        <button onClick={handleUpload} disabled={!file}>
          Enviar
        </button>
      </div>

      {status && <p>{status}</p>}

      {analysis && (
        <div style={{ marginTop: "0.5rem" }}>
          <h3>Feedback da Análise</h3>
          <pre style={{ whiteSpace: "pre-wrap" }}>{JSON.stringify(analysis, null, 2)}</pre>
          {analysis && analysis.Repetitions !== undefined && (
            <p>Repetições detectadas: {analysis.Repetitions}</p>
          )}
          {analysis && analysis.filename && (
            <p>
              Arquivo salvo: <a href={`${API_URL}/uploads/${analysis.filename}`} target="_blank" rel="noreferrer">Abrir</a>
            </p>
          )}
        </div>
      )}
    </section>
  );
}
