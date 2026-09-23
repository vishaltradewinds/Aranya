"use client"

import { useEffect, useRef, useState } from "react"

const paths = [
  { key: "have", icon: "🌿", title: "Mere paas hai", text: "resource, produce, knowledge, capacity" },
  { key: "need", icon: "🔎", title: "Mujhe chahiye", text: "buyer, material, service, finance" },
  { key: "can", icon: "🛠️", title: "Main kar sakta hoon", text: "processing, transport, research, training" },
  { key: "connect", icon: "🤝", title: "Mujhe judna hai", text: "people, networks, institutions, markets" },
]

const next = {
  have: "Apne paas jo hai, uske baare mein batao. ARANYA sirf zaroori sawaal poochega.",
  need: "Aapko kya chahiye? Naam, quantity ya photo se shuru kar sakte ho.",
  can: "Aap kya kar sakte ho? Apni capability ya capacity batao.",
  connect: "Kis tarah ke stakeholder ya network se judna hai? ARANYA raasta dhoondhega.",
}

export default function Home() {
  const [selected, setSelected] = useState<string | null>(null)
  const [message, setMessage] = useState("")
  const [input, setInput] = useState("")
  const [aiReply, setAiReply] = useState("")
  const [aiBusy, setAiBusy] = useState(false)
  const [journey, setJourney] = useState<any>(null)
  const [aiAvailable, setAiAvailable] = useState<boolean | null>(null)
  const [evidenceStatus, setEvidenceStatus] = useState("")

  const [listening, setListening] = useState(false)
  const [photoName, setPhotoName] = useState("")
  const [queued, setQueued] = useState(0)
  const recognitionRef = useRef<any>(null)\n  const dbRef = useRef<IDBDatabase | null>(null)

  const openQueue = () => new Promise<IDBDatabase>((resolve,reject) => {\n    const req=indexedDB.open("aranya-offline",1)\n    req.onupgradeneeded=()=>req.result.createObjectStore("queue",{keyPath:"id",autoIncrement:true})\n    req.onsuccess=()=>resolve(req.result)\n    req.onerror=()=>reject(req.error)\n  })\n  const saveOffline = async (kind:string,payload:any) => { try { const db=dbRef.current || await openQueue(); dbRef.current=db; const tx=db.transaction("queue","readwrite"); tx.objectStore("queue").add({kind,payload,createdAt:Date.now()}); setQueued((q)=>q+1) } catch {} }\n\n  useEffect(() => {
    if ("serviceWorker" in navigator) navigator.serviceWorker.register("/sw.js").catch(() => {})
    try { openQueue().then(db=>{dbRef.current=db; const tx=db.transaction("queue","readonly"); const req=tx.objectStore("queue").count(); req.onsuccess=()=>setQueued(req.result) }).catch(()=>{}) } catch {}\n    const sync=()=>{ setMessage("Connection restored. ARANYA will synchronise saved work when authenticated."); }\n    window.addEventListener("online",sync); return ()=>window.removeEventListener("online",sync)
  }, [])

  const startVoice = () => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
    if (!SpeechRecognition) { setMessage("🎙️ Voice input is not available in this browser. You can type instead."); return }
    if (listening) { recognitionRef.current?.stop(); return }
    const recognition = new SpeechRecognition()
    recognition.lang = "hi-IN"
    recognition.interimResults = false
    recognition.onstart = () => setListening(true)
    recognition.onend = () => setListening(false)
    recognition.onerror = () => { setListening(false); setMessage("🎙️ Voice could not be captured. Try again or type your message.") }
    recognition.onresult = (event: any) => {
      const text = event.results?.[0]?.[0]?.transcript || ""
      setInput(text)
      setMessage("Voice captured. Press Batao to continue.")
    }
    recognitionRef.current = recognition
    recognition.start()
  }

  const uploadEvidence = async (file: File) => {
    const api = process.env.NEXT_PUBLIC_ARANYA_API_URL || "http://localhost:8000"
    try {
      const form = new FormData()
      form.append("entity_id", "pending")
      form.append("evidence_type", "PHOTO")
      form.append("file", file)
      const response = await fetch(`${api}/api/v1/evidence-objects`, { method: "POST", body: form })
      if (!response.ok) throw new Error("upload failed")
      const data = await response.json()
      setEvidenceStatus(`Evidence captured · ${data.content_hash.slice(0, 12)}…`)
    } catch { await saveOffline("photo",{name:file.name,type:file.type,blob:file}); setEvidenceStatus("Evidence saved locally for later synchronisation.") }
  }

  const handlePhoto = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return
    setPhotoName(file.name)
    setMessage("📷 Photo captured. ARANYA will use it as context; verification remains separate.")
    void uploadEvidence(file)
  }
  const askAranya = async () => {
    if (!input.trim()) return
    setAiBusy(true)
    setAiReply("")
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_ARANYA_API_URL || "http://localhost:8000"}/api/v1/ai/understand`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: input, context: { selected_intent: selected } }),
      })
      const data = await response.json()
      if (!response.ok) throw new Error(data.detail || "AI request failed")
      setAiAvailable(Boolean(data.ai?.available ?? true))
      setAiReply(data.ai?.reply || data.reply || "ARANYA could not respond yet.")
    } catch {
      setAiAvailable(false)
      await saveOffline("intent",{message:input,context:{selected_intent:selected}})
      setAiReply("ARANYA is offline right now. I saved this task for later synchronisation.")
    } finally { setAiBusy(false) }
  }

  const choose = (key: string) => {
    setSelected(key)
    setMessage(next[key as keyof typeof next])
  }

  return (
    <main className="aranya-shell">
      <section className="aranya-world" aria-label="ARANYA entry experience">
        <div className="topline"><span>ARANYA</span><span className="status">● Live work mode</span></div>
        <div className="forest-scene" aria-hidden="true">
          <div className="sun" /><div className="tree tree-a" /><div className="tree tree-b" /><div className="tree tree-c" /><div className="tree tree-d" />
          <div className="pathway" /><div className="deer">🦌</div>
        </div>
        <div className="welcome">
          <p className="kicker">ENTER ARANYA</p>
          <h1>Jungle se baat karo.</h1>
          <p>Apni baat apne tareeke se batao. ARANYA aapko sirf agla zaroori kadam dikhayega.</p>
        </div>
        <div className="intent-grid">
          {paths.map((item) => (
            <button key={item.key} className={selected === item.key ? "intent selected" : "intent"} onClick={() => choose(item.key)}>
              <span className="intent-icon">{item.icon}</span><strong>{item.title}</strong><small>{item.text}</small>
            </button>
          ))}
        </div>
        <div className="walk-panel" aria-live="polite">
          <div className="walk-label">YOUR NEXT STEP</div>
          <div className="walk-message">{aiReply || message || "Batao. Aaj kya karna hai?"}</div>
          <div className="walk-actions">
            <button type="button" onClick={startVoice}>{listening ? "⏹️ Sun raha hoon" : "🎙️ Boliye"}</button>
            <label className="media-button">📷 Photo<input type="file" accept="image/*" capture="environment" onChange={handlePhoto} /></label>
            <button type="button" onClick={() => setMessage("🤝 N2N: ARANYA aapke network ko relevant network se jodne ke liye tayyar hai.")}>🤝 Connect network</button>
          </div>
          <div className="offline-note">{queued > 0 ? "Offline queue: " + queued + " task(s) waiting" : "Offline capture ready."}{photoName ? " · " + photoName : ""}{evidenceStatus ? " · " + evidenceStatus : ""}</div>\n          {journey && <div className="journey-card"><b>Journey: {journey.key.replaceAll("_", " ")}</b><span>State: {journey.state.replaceAll("_", " ")}</span>{journey.questions?.length > 0 && <span>Next: {journey.questions[0]}</span>}<strong>{journey.next_action.replaceAll("_", " ")}</strong></div>}
          <div className="ask-row">
            <input aria-label="Tell ARANYA what you need" value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={(e) => { if (e.key === "Enter") askAranya() }} placeholder="Apni baat likhiye..." />
            <button type="button" onClick={askAranya} disabled={aiBusy}>{aiBusy ? "..." : "Batao"}</button>\n            {aiAvailable === false && <small className="ai-state">Local AI unavailable — task can still be captured.</small>}
          </div>
        </div>
        <div className="principle"><b>WALK THE ARANYA</b><span>Real work creates the record. Evidence proves it. Legitimate value can lead to settlement.</span></div>
      </section>
    </main>
  )
}
