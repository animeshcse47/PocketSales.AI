export default function ContactCard({ contact }) {
  return (
    <div className="w-full max-w-md bg-surface-container-high border border-outline-variant/50 rounded-xl overflow-hidden shadow-2xl relative">
      <div className="absolute top-0 left-0 w-1 h-full bg-primary opacity-40" />

      <div className="p-5">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h3 className="font-hanken font-semibold text-[18px] leading-6 text-on-surface">
              {contact.name || "Unknown Name"}
            </h3>
            {contact.designation && (
              <p className="text-primary font-medium text-sm mt-0.5">{contact.designation}</p>
            )}
          </div>
          <div className="w-11 h-11 bg-white/5 rounded-lg flex items-center justify-center shrink-0">
            <span className="material-symbols-outlined text-on-surface-variant">corporate_fare</span>
          </div>
        </div>

        {contact.company && (
          <p className="font-mono text-[11px] uppercase tracking-widest text-on-surface-variant opacity-70 mb-4">
            {contact.company}
          </p>
        )}

        <div className="space-y-2">
          {contact.email && (
            <div className="flex items-center gap-3">
              <span className="material-symbols-outlined text-primary text-[16px]">mail</span>
              <span className="text-sm text-on-surface">{contact.email}</span>
            </div>
          )}
          {contact.phone && (
            <div className="flex items-center gap-3">
              <span className="material-symbols-outlined text-primary text-[16px]">call</span>
              <span className="text-sm text-on-surface">{contact.phone}</span>
            </div>
          )}
          {contact.address && (
            <div className="flex items-center gap-3">
              <span className="material-symbols-outlined text-primary text-[16px]">location_on</span>
              <span className="text-sm text-on-surface">{contact.address}</span>
            </div>
          )}
          {contact.website && (
            <div className="flex items-center gap-3">
              <span className="material-symbols-outlined text-primary text-[16px]">language</span>
              <a
                href={contact.website.startsWith("http") ? contact.website : `https://${contact.website}`}
                target="_blank"
                rel="noreferrer"
                className="text-sm text-primary hover:underline"
              >
                {contact.website}
              </a>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
