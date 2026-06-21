import { useEffect, useState } from "react"

const ICONS = {
  success: { icon: "check_circle", color: "text-tertiary" },
  error: { icon: "error", color: "text-error" },
  info: { icon: "info", color: "text-primary" },
}

export function Toast({ message, type = "info", onDone }) {
  const [visible, setVisible] = useState(true)
  const { icon, color } = ICONS[type] || ICONS.info

  useEffect(() => {
    const t = setTimeout(() => { setVisible(false); setTimeout(onDone, 300) }, 3000)
    return () => clearTimeout(t)
  }, [onDone])

  return (
    <div className={`flex items-center gap-3 px-4 py-3 bg-surface-container-high border border-outline-variant/50 rounded-xl shadow-2xl text-sm max-w-sm transition-all duration-300 ${visible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-2"}`}>
      <span className={`material-symbols-outlined text-[18px] shrink-0 ${color}`} style={{ fontVariationSettings: "'FILL' 1" }}>{icon}</span>
      <p className="text-on-surface">{message}</p>
    </div>
  )
}

export function ToastContainer({ toasts, removeToast }) {
  if (!toasts.length) return null
  return (
    <div className="fixed bottom-28 right-6 z-50 flex flex-col gap-2 items-end">
      {toasts.map(t => (
        <Toast key={t.id} message={t.message} type={t.type} onDone={() => removeToast(t.id)} />
      ))}
    </div>
  )
}
