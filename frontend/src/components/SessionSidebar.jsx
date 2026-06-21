import { format, isValid } from "date-fns"

export default function SessionSidebar({ sessions, currentSessionId, onSelectSession, onNewSession }) {
  function formatDate(val) {
    if (!val) return "Just now"
    const d = new Date(val)
    return isValid(d) ? format(d, "MMM d, h:mm a") : "Just now"
  }

  return (
    <aside className="w-[280px] h-full fixed left-0 top-0 bg-surface-container-low border-r border-outline-variant flex flex-col p-4 z-50">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 rounded-lg bg-primary-container flex items-center justify-center shrink-0">
          <span className="material-symbols-outlined text-on-primary-container" style={{ fontVariationSettings: "'FILL' 1" }}>sim_card</span>
        </div>
        <div>
          <h1 className="font-hanken font-bold text-[18px] leading-6 text-on-surface">Card Digitizer</h1>
          <p className="font-mono text-[11px] text-on-surface-variant opacity-70 tracking-wider">AI ASSISTANT</p>
        </div>
      </div>

      <button
        onClick={onNewSession}
        className="mb-6 w-full py-3 px-4 bg-primary text-on-primary font-hanken font-semibold text-sm rounded-xl flex items-center justify-center gap-2 transition-all hover:opacity-90 active:scale-95"
      >
        <span className="material-symbols-outlined text-[18px]">add</span>
        New Session
      </button>

      <nav className="flex-1 space-y-1 overflow-y-auto custom-scrollbar">
        {sessions.length === 0 && (
          <p className="text-on-surface-variant text-xs text-center py-6 opacity-50">No sessions yet</p>
        )}
        {sessions.map((session, i) => {
          const isActive = session.session_id === currentSessionId
          const icons = ["person", "chat", "history", "work", "contacts"]
          const icon = icons[i % icons.length]
          return (
            <button
              key={session.session_id}
              onClick={() => onSelectSession(session.session_id)}
              className={`w-full text-left px-3 py-3 rounded-r-lg flex items-center gap-3 transition-colors cursor-pointer group ${
                isActive
                  ? "bg-surface-variant text-on-surface border-l-4 border-primary"
                  : "text-on-surface-variant hover:bg-surface-container-highest border-l-4 border-transparent"
              }`}
            >
              <span className="material-symbols-outlined text-[18px] shrink-0" style={isActive ? { fontVariationSettings: "'FILL' 1" } : {}}>{icon}</span>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">{session.title || "New Session"}</p>
                <p className="text-[10px] opacity-60 mt-0.5">{formatDate(session.last_active)}</p>
              </div>
            </button>
          )
        })}
      </nav>

      <div className="mt-auto pt-3 border-t border-outline-variant flex items-center gap-2">
        <div className="w-8 h-8 rounded-full bg-surface-container-high flex items-center justify-center cursor-pointer hover:bg-surface-variant transition-colors">
          <span className="material-symbols-outlined text-[16px] text-on-surface-variant">settings</span>
        </div>
        <div className="w-8 h-8 rounded-full bg-surface-container-high flex items-center justify-center cursor-pointer hover:bg-surface-variant transition-colors">
          <span className="material-symbols-outlined text-[16px] text-on-surface-variant">help</span>
        </div>
      </div>
    </aside>
  )
}
