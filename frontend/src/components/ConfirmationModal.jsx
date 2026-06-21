import ContactCard from "./ContactCard"

export default function ConfirmationModal({ contact, onConfirm, onReject }) {
  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 px-4">
      <div className="bg-surface-container-low border border-outline-variant rounded-2xl p-6 w-full max-w-sm shadow-2xl">
        <div className="flex items-center gap-3 mb-1">
          <span className="material-symbols-outlined text-primary" style={{ fontVariationSettings: "'FILL' 1" }}>contact_page</span>
          <h2 className="font-hanken font-semibold text-[18px] text-on-surface">Confirm Contact</h2>
        </div>
        <p className="text-sm text-on-surface-variant mb-4 ml-9">
          Are these details correct?
        </p>

        <ContactCard contact={contact} />

        <div className="flex gap-3 mt-5">
          <button
            onClick={onConfirm}
            className="flex-1 flex items-center justify-center gap-2 bg-primary text-on-primary py-2.5 rounded-xl font-semibold text-sm transition-all hover:opacity-90 active:scale-95"
          >
            <span className="material-symbols-outlined text-[16px]" style={{ fontVariationSettings: "'FILL' 1" }}>check_circle</span>
            Yes, Save
          </button>
          <button
            onClick={onReject}
            className="flex-1 flex items-center justify-center gap-2 bg-error-container/30 border border-error/30 text-error py-2.5 rounded-xl font-semibold text-sm transition-all hover:bg-error-container/50 active:scale-95"
          >
            <span className="material-symbols-outlined text-[16px]">cancel</span>
            Retry
          </button>
        </div>
      </div>
    </div>
  )
}
