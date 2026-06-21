import ContactCard from "./ContactCard"

function parseContent(content) {
  return content.split("\n").map((line, i) => {
    if (!line.trim()) return <br key={i} />
    const parts = line.split(/\*\*(.*?)\*\*/g)
    return (
      <p key={i} className={i > 0 ? "mt-1" : ""}>
        {parts.map((part, j) =>
          j % 2 === 1 ? <strong key={j} className="font-semibold text-on-surface">{part}</strong> : part
        )}
      </p>
    )
  })
}

function UserBubble({ message }) {
  const isImage = message.type === "image"
  const isAudio = message.type === "audio"

  return (
    <div className="flex justify-end">
      <div className="bg-primary text-on-primary px-4 py-3 rounded-2xl rounded-tr-sm shadow-lg max-w-[72%] flex items-center gap-2">
        {isImage && <span className="material-symbols-outlined text-[16px] opacity-80">photo_camera</span>}
        {isAudio && <span className="material-symbols-outlined text-[16px] opacity-80">mic</span>}
        <p className="text-sm leading-relaxed">{message.content}</p>
      </div>
    </div>
  )
}

function AIAvatar() {
  return (
    <div className="w-9 h-9 rounded-xl bg-surface-container-highest flex-shrink-0 flex items-center justify-center mt-0.5">
      <span className="material-symbols-outlined text-secondary text-[18px]" style={{ fontVariationSettings: "'FILL' 1" }}>smart_toy</span>
    </div>
  )
}

function VoiceNoteCard({ content }) {
  const transcriptMatch = content.match(/\*\*Transcript:\*\*\s*([\s\S]*?)(?:\n\n|\n🔗|$)/)
  const urlMatch = content.match(/\*\*Audio URL:\*\*\s*(\S+)/)
  const sheetsMatch = content.match(/Google Sheets.*?\*\*(.*?)\*\*/)

  if (!transcriptMatch && !urlMatch) {
    return (
      <div className="bg-surface-container border border-outline-variant/30 rounded-xl rounded-tl-sm px-4 py-3 text-sm leading-relaxed text-on-surface">
        {parseContent(content)}
      </div>
    )
  }

  return (
    <div className="bg-surface-container-high border border-outline-variant/50 rounded-xl overflow-hidden ai-border-accent shadow-xl">
      <div className="p-4 space-y-3">
        <div className="flex items-center gap-2 text-tertiary">
          <span className="material-symbols-outlined text-[18px]" style={{ fontVariationSettings: "'FILL' 1" }}>check_circle</span>
          <p className="font-hanken font-semibold text-[15px]">Voice note saved!</p>
        </div>

        {transcriptMatch && (
          <div className="bg-background/40 rounded-lg p-3 border border-outline-variant/20">
            <div className="flex items-center gap-2 mb-2 text-on-surface-variant">
              <span className="material-symbols-outlined text-[15px]">description</span>
              <span className="font-mono text-[10px] uppercase tracking-widest">Transcript</span>
            </div>
            <p className="text-sm text-on-surface/90 leading-relaxed italic">
              "{transcriptMatch[1].trim()}"
            </p>
          </div>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
          {urlMatch && (
            <div className="flex items-center gap-3 p-3 bg-background/20 rounded-lg border border-outline-variant/10">
              <span className="material-symbols-outlined text-primary text-[18px]">link</span>
              <div className="flex-1 min-w-0">
                <p className="font-mono text-[10px] text-on-surface-variant uppercase mb-0.5">Audio URL</p>
                <p className="font-mono text-[11px] text-primary truncate">{urlMatch[1]}</p>
              </div>
            </div>
          )}
          <div className="flex items-center gap-3 p-3 bg-background/20 rounded-lg border border-outline-variant/10">
            <span className="material-symbols-outlined text-tertiary text-[18px]">grid_on</span>
            <div className="flex-1 min-w-0">
              <p className="font-mono text-[10px] text-on-surface-variant uppercase mb-0.5">Sheets</p>
              <p className="font-mono text-[11px] text-on-surface truncate">
                {sheetsMatch ? `Updated for ${sheetsMatch[1]}` : "Updated"}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function DuplicateWarning({ content }) {
  return (
    <div className="bg-error-container/20 border border-error/30 rounded-xl p-3 flex items-start gap-3">
      <span className="material-symbols-outlined text-error text-[18px] mt-0.5 shrink-0" style={{ fontVariationSettings: "'FILL' 1" }}>warning</span>
      <p className="text-sm text-on-surface leading-relaxed">{parseContent(content)}</p>
    </div>
  )
}

function SuccessBanner({ content }) {
  return (
    <div className="bg-surface-container-high border border-outline-variant/40 rounded-xl rounded-tl-sm p-4 ai-border-accent">
      <div className="text-sm leading-relaxed text-on-surface space-y-1">{parseContent(content)}</div>
    </div>
  )
}

function GenericAIBubble({ content }) {
  return (
    <div className="bg-surface-container border border-outline-variant/30 rounded-xl rounded-tl-sm px-4 py-3 text-sm leading-relaxed text-on-surface">
      {parseContent(content)}
    </div>
  )
}

export default function MessageBubble({ message }) {
  const isUser = message.role === "user"
  const content = message.content || ""

  if (isUser) return <UserBubble message={message} />

  const isDuplicate = content.includes("already exists")
  const isVoiceResult = content.includes("Transcript:") && content.includes("Audio URL:")
  const isVoiceSaved = content.toLowerCase().includes("voice note")
  const isSavedToSheets = content.includes("saved to Google Sheets") || content.includes("been saved")

  return (
    <div className="flex gap-3">
      <AIAvatar />
      <div className="flex-1 pt-1 min-w-0 max-w-[82%]">
        {message.type === "card_preview" && message.metadata ? (
          <div>
            <p className="font-mono text-[10px] text-on-surface-variant uppercase tracking-widest mb-2">Extracted Contact</p>
            <ContactCard contact={message.metadata} />
          </div>
        ) : isDuplicate ? (
          <DuplicateWarning content={content} />
        ) : (isVoiceResult || isVoiceSaved) ? (
          <VoiceNoteCard content={content} />
        ) : isSavedToSheets ? (
          <SuccessBanner content={content} />
        ) : (
          <GenericAIBubble content={content} />
        )}
      </div>
    </div>
  )
}
