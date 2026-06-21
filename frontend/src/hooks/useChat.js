import { useState, useCallback, useEffect } from "react"
import { sendMessage, uploadImage, uploadAudio, getChatHistory } from "../services/api"

export function useChat(sessionId) {
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)

  // restore history when session changes
  useEffect(() => {
    if (!sessionId) return
    setMessages([])
    getChatHistory(sessionId)
      .then(history => {
        if (!history?.length) return
        const restored = history.map((m, i) => ({
          id: `history-${i}`,
          role: m.role,
          content: m.content,
          type: m.message_type || "text",
          metadata: m.metadata || null,
        }))
        setMessages(restored)
      })
      .catch(() => {})
  }, [sessionId])

  const addMessage = useCallback((role, content, type = "text", metadata = null) => {
    setMessages(prev => [...prev, {
      role,
      content,
      type,
      metadata,
      id: Date.now() + Math.random(),
    }])
  }, [])

  const send = useCallback(async (text = "", imageRef = null, audioRef = null) => {
    if (!text && !imageRef && !audioRef) return null
    setLoading(true)

    const label = imageRef ? "Card image uploaded" : audioRef ? "Voice note uploaded" : text
    const labelType = imageRef ? "image" : audioRef ? "audio" : "text"
    addMessage("user", label, labelType)

    try {
      const res = await sendMessage(sessionId, text, imageRef, audioRef)
      addMessage("assistant", res.response, res.response_type, res.metadata)
      return res
    } catch {
      addMessage("assistant", "Something went wrong. Please try again.")
      return null
    } finally {
      setLoading(false)
    }
  }, [sessionId, addMessage])

  const sendImage = useCallback(async (file) => {
    const { ref } = await uploadImage(file)
    return send("", ref, null)
  }, [send])

  const sendAudio = useCallback(async (file) => {
    const { ref } = await uploadAudio(file)
    return send("", null, ref)
  }, [send])

  return { messages, setMessages, loading, send, sendImage, sendAudio, addMessage }
}
