import axios from "axios"

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
})

export async function createSession() {
  const { data } = await api.post("/api/sessions/")
  return data
}

export async function listSessions() {
  const { data } = await api.get("/api/sessions/")
  return data.sessions
}

export async function sendMessage(sessionId, message, imageRef = null, audioRef = null) {
  const { data } = await api.post("/api/chat/", {
    session_id: sessionId,
    message: message || "",
    image_ref: imageRef,
    audio_ref: audioRef,
  })
  return data
}

export async function uploadImage(file) {
  const form = new FormData()
  form.append("file", file)
  const { data } = await api.post("/api/upload/image", form, {
    headers: { "Content-Type": "multipart/form-data" },
  })
  return data
}

export async function uploadAudio(file) {
  const form = new FormData()
  form.append("file", file)
  const { data } = await api.post("/api/upload/audio", form, {
    headers: { "Content-Type": "multipart/form-data" },
  })
  return data
}

export async function getChatHistory(sessionId) {
  const { data } = await api.get(`/api/chat/${sessionId}/history`)
  return data.messages
}
