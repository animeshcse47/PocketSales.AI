import { useState, useRef, useEffect, useCallback } from "react"
import MessageBubble from "./MessageBubble"
import FileUploader from "./FileUploader"
import ConfirmationModal from "./ConfirmationModal"
import { ToastContainer } from "./Toast"
import { useChat } from "../hooks/useChat"

export default function ChatWindow({ sessionId }) {
  const { messages, loading, send, sendImage, sendAudio } = useChat(sessionId)
  const [input, setInput] = useState("")
  const [pendingCard, setPendingCard] = useState(null)
  const [toasts, setToasts] = useState([])
  const bottomRef = useRef(null)
  const textareaRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  // auto-resize textarea
  useEffect(() => {
    const el = textareaRef.current
    if (!el) return
    el.style.height = "auto"
    el.style.height = Math.min(el.scrollHeight, 120) + "px"
  }, [input])

  const addToast = useCallback((message, type = "info") => {
    const id = Date.now()
    setToasts(prev => [...prev, { id, message, type }])
  }, [])

  const removeToast = useCallback((id) => {
    setToasts(prev => prev.filter(t => t.id !== id))
  }, [])

  async function handleSend() {
    const text = input.trim()
    if (!text || loading) return
    setInput("")
    const res = await send(text)
    if (res?.response_type === "card_preview" && res?.metadata) {
      setPendingCard(res.metadata)
    }
  }

  async function handleImageUpload(file) {
    addToast("Processing card image...", "info")
    const res = await sendImage(file)
    if (res?.response_type === "card_preview" && res?.metadata) {
      setPendingCard(res.metadata)
      addToast("Card extracted — please confirm details", "success")
    }
  }

  async function handleAudioUpload(file) {
    addToast("Transcribing voice note...", "info")
    const res = await sendAudio(file)
    if (res) addToast("Voice note saved to Sheets!", "success")
  }

  async function handleConfirm(confirmed) {
    setPendingCard(null)
    if (confirmed) {
      addToast("Saving contact...", "info")
    }
    const res = await send(confirmed ? "Yes, the details are correct" : "No, please try again")
    if (confirmed && res) {
      addToast("Contact saved to Google Sheets!", "success")
    }
  }

  function handleKey(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="flex flex-col h-full relative">
      {/* Header */}
      <header className="flex justify-between items-center px-6 py-4 border-b border-outline-variant/30 bg-background/80 backdrop-blur-md sticky top-0 z-40">
        <div>
          <h2 className="font-hanken font-bold text-[22px] leading-tight text-on-surface">Card Digitizer Assistant</h2>
          <p className="font-mono text-[10px] text-on-surface-variant opacity-50 tracking-widest mt-0.5">AI-POWERED · GEMINI 2.5 FLASH</p>
        </div>
        <div className="flex items-center gap-3">
          <span className="material-symbols-outlined text-on-surface-variant hover:text-primary cursor-pointer transition-colors">settings</span>
          <span className="material-symbols-outlined text-on-surface-variant hover:text-primary cursor-pointer transition-colors">help</span>
          <div className="h-6 w-px bg-outline-variant/30 mx-1" />
          <div className="w-8 h-8 rounded-full bg-primary-container/20 flex items-center justify-center">
            <span className="material-symbols-outlined text-primary text-[20px]" style={{ fontVariationSettings: "'FILL' 1" }}>account_circle</span>
          </div>
        </div>
      </header>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto custom-scrollbar px-6 pt-6 pb-44 bg-background">
        <div className="max-w-[860px] mx-auto space-y-5">
          {messages.length === 0 && (
            <div className="flex gap-3">
              <div className="w-9 h-9 rounded-xl bg-surface-container-highest flex-shrink-0 flex items-center justify-center">
                <span className="material-symbols-outlined text-secondary text-[18px]" style={{ fontVariationSettings: "'FILL' 1" }}>smart_toy</span>
              </div>
              <div className="flex-1 pt-1">
                <div className="bg-surface-container border border-outline-variant/30 rounded-xl rounded-tl-sm px-4 py-3 max-w-sm">
                  <p className="text-sm text-on-surface-variant leading-relaxed">
                    Upload a visiting card or voice note to get started.
                  </p>
                </div>
              </div>
            </div>
          )}

          {messages.map(msg => (
            <MessageBubble key={msg.id} message={msg} />
          ))}

          {loading && (
            <div className="flex gap-3">
              <div className="w-9 h-9 rounded-xl bg-surface-container-highest flex-shrink-0 flex items-center justify-center">
                <span className="material-symbols-outlined text-secondary text-[18px]" style={{ fontVariationSettings: "'FILL' 1" }}>smart_toy</span>
              </div>
              <div className="pt-3.5 flex items-center gap-1.5 pl-1">
                <span className="w-1.5 h-1.5 rounded-full bg-on-surface-variant opacity-50 animate-bounce" />
                <span className="w-1.5 h-1.5 rounded-full bg-on-surface-variant opacity-50 animate-bounce delay-100" />
                <span className="w-1.5 h-1.5 rounded-full bg-on-surface-variant opacity-50 animate-bounce delay-200" />
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>
      </div>

      {/* Input bar */}
      <div className="absolute bottom-0 left-0 w-full px-6 pb-6 pt-4 bg-gradient-to-t from-background via-background/95 to-transparent pointer-events-none">
        <div className="max-w-[860px] mx-auto bg-surface-container-high/95 backdrop-blur-xl border border-outline-variant/50 rounded-2xl p-2 shadow-2xl pointer-events-auto">
          <div className="flex flex-col gap-2">
            <FileUploader
              onImageUpload={handleImageUpload}
              onAudioUpload={handleAudioUpload}
              disabled={loading}
            />
            <div className="flex items-end gap-2 bg-surface-container-lowest/50 rounded-xl border border-outline-variant/30 focus-within:border-primary/50 transition-all px-4 py-2">
              <textarea
                ref={textareaRef}
                rows={1}
                className="flex-1 bg-transparent border-none focus:ring-0 text-sm text-on-surface placeholder-on-surface-variant/40 outline-none resize-none py-1.5 leading-relaxed"
                placeholder="Type a message..."
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={handleKey}
                disabled={loading}
                style={{ minHeight: "36px", maxHeight: "120px" }}
              />
              <button
                onClick={handleSend}
                disabled={loading || !input.trim()}
                className="w-9 h-9 rounded-lg bg-primary text-on-primary flex items-center justify-center hover:opacity-90 active:scale-95 disabled:opacity-40 transition-all shrink-0 mb-0.5"
              >
                <span className="material-symbols-outlined text-[18px]">send</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {pendingCard && (
        <ConfirmationModal
          contact={pendingCard}
          onConfirm={() => handleConfirm(true)}
          onReject={() => handleConfirm(false)}
        />
      )}

      <ToastContainer toasts={toasts} removeToast={removeToast} />
    </div>
  )
}
