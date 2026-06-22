import { useState, useEffect, useRef } from "react"
import { createSession, listSessions } from "../services/api"

export function useSession() {
  const [sessions, setSessions] = useState([])
  const [currentSessionId, setCurrentSessionId] = useState(null)
  const [loading, setLoading] = useState(true)
  const initialized = useRef(false)

  useEffect(() => {
    if (initialized.current) return
    initialized.current = true
    loadSessions()
  }, [])

  async function loadSessions() {
    try {
      const all = await listSessions()
      setSessions(all)
      if (all.length > 0) {
        setCurrentSessionId(all[0].session_id)
      } else {
        const session = await createSession()
        setSessions([session])
        setCurrentSessionId(session.session_id)
      }
    } catch {
      try {
        const session = await createSession()
        setSessions([session])
        setCurrentSessionId(session.session_id)
      } catch {}
    } finally {
      setLoading(false)
    }
  }

  async function startNewSession() {
    const session = await createSession()
    setSessions(prev => {
      const exists = prev.find(s => s.session_id === session.session_id)
      return exists ? prev : [session, ...prev]
    })
    setCurrentSessionId(session.session_id)
    return session
  }

  return {
    sessions,
    setSessions,
    currentSessionId,
    setCurrentSessionId,
    startNewSession,
    loading,
  }
}
