import { useRef, useCallback } from "react"
import { useDropzone } from "react-dropzone"

export default function FileUploader({ onImageUpload, onAudioUpload, disabled }) {
  const imageRef = useRef(null)
  const audioRef = useRef(null)

  const onDrop = useCallback((acceptedFiles) => {
    if (disabled) return
    for (const file of acceptedFiles) {
      if (file.type.startsWith("image/")) {
        onImageUpload(file)
      } else if (file.type.startsWith("audio/") || file.type === "video/webm") {
        onAudioUpload(file)
      }
    }
  }, [disabled, onImageUpload, onAudioUpload])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    noClick: true,
    disabled,
    accept: {
      "image/jpeg": [], "image/png": [], "image/webp": [],
      "audio/mpeg": [], "audio/wav": [], "audio/webm": [],
      "audio/ogg": [], "audio/mp4": [], "video/webm": [],
    },
  })

  function handleImage(e) {
    const file = e.target.files[0]
    if (file) { onImageUpload(file); e.target.value = "" }
  }

  function handleAudio(e) {
    const file = e.target.files[0]
    if (file) { onAudioUpload(file); e.target.value = "" }
  }

  return (
    <div {...getRootProps()} className={`transition-colors rounded-xl ${isDragActive ? "bg-primary/10 border border-dashed border-primary/50" : ""}`}>
      <input {...getInputProps()} />
      <div className="flex items-center gap-2 px-2 pt-1">
        <input ref={imageRef} type="file" accept="image/jpeg,image/png,image/webp" className="hidden" onChange={handleImage} />
        <input ref={audioRef} type="file" accept="audio/*,video/webm" className="hidden" onChange={handleAudio} />

        <button
          type="button"
          onClick={() => imageRef.current?.click()}
          disabled={disabled}
          className="flex items-center gap-1.5 px-3 py-2 rounded-lg bg-surface-container-highest text-on-surface-variant hover:text-primary hover:bg-primary/10 disabled:opacity-40 transition-all text-xs font-mono tracking-wide"
        >
          <span className="material-symbols-outlined text-[16px]">photo_camera</span>
          Card Image
        </button>

        <button
          type="button"
          onClick={() => audioRef.current?.click()}
          disabled={disabled}
          className="flex items-center gap-1.5 px-3 py-2 rounded-lg bg-surface-container-highest text-on-surface-variant hover:text-primary hover:bg-primary/10 disabled:opacity-40 transition-all text-xs font-mono tracking-wide"
        >
          <span className="material-symbols-outlined text-[16px]">mic</span>
          Voice Note
        </button>

        <div className="h-5 w-px bg-outline-variant/40 mx-1" />
        {isDragActive
          ? <span className="text-[11px] text-primary font-mono animate-pulse">Drop file here...</span>
          : <span className="text-[11px] text-on-surface-variant/40 font-mono">or drag & drop</span>
        }
      </div>
    </div>
  )
}
