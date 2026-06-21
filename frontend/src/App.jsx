import SessionSidebar from "./components/SessionSidebar"
import ChatWindow from "./components/ChatWindow"
import { useSession } from "./hooks/useSession"

export default function App() {
  const {
    sessions,
    setSessions,
    currentSessionId,
    setCurrentSessionId,
    startNewSession,
    loading,
  } = useSession()

  async function handleNewSession() {
    const session = await startNewSession()
    setSessions(prev => {
      const exists = prev.find(s => s.session_id === session.session_id)
      return exists ? prev : [session, ...prev]
    })
    setCurrentSessionId(session.session_id)
  }

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-background">
        <div className="flex flex-col items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-primary-container flex items-center justify-center">
            <span className="material-symbols-outlined text-on-primary-container" style={{ fontVariationSettings: "'FILL' 1" }}>sim_card</span>
          </div>
          <p className="font-mono text-xs text-on-surface-variant opacity-50 tracking-widest">LOADING...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex h-screen overflow-hidden bg-background text-on-surface dark">
      <SessionSidebar
        sessions={sessions}
        currentSessionId={currentSessionId}
        onSelectSession={setCurrentSessionId}
        onNewSession={handleNewSession}
      />
      <main className="ml-[280px] flex-1 flex flex-col min-w-0 relative">
        {currentSessionId ? (
          <ChatWindow key={currentSessionId} sessionId={currentSessionId} />
        ) : (
          <div className="flex-1 flex items-center justify-center text-on-surface-variant opacity-50 text-sm">
            Select or create a session to begin
          </div>
        )}
      </main>
    </div>
  )
}
