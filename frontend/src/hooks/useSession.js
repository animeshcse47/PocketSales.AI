import { useState, useEffect } from "react"
import { createSession, listSessions } from "../services/api"

export function useSession() {
  const [sessions, setSessions] = useState([])
  const [currentSessionId, setCurrentSessionId] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadSessions()
  }, [])

  async function loadSessions() {
    try {
      const all = await listSessions()
      setSessions(all)
      if (all.length > 0) {
        setCurrentSessionId(all[0].session_id)
      } else {
        await startNewSession()
      }
    } catch {
      await startNewSession()
    } finally {
      setLoading(false)
    }
  }

  async function startNewSession() {
    const session = await createSession()
    setSessions(prev => [session, ...prev])
    setCurrentSessionId(session.session_id)
    return session
  }

  return { sessions, setSessions, currentSessionId, setCurrentSessionId, startNewSession, loading }
}
