"use client"

import { useState } from "react"

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
          <div className="walk-message">{message || "Batao. Aaj kya karna hai?"}</div>
          <div className="walk-actions">
            <button type="button" onClick={() => setMessage("🎙️ Boliye — apni bhasha mein. ARANYA intent samjhega.")}>🎙️ Boliye</button>
            <button type="button" onClick={() => setMessage("📷 Photo dikhaiye — ARANYA usse context samajhne mein madad lega. Verification alag rahega.")}>📷 Photo</button>
            <button type="button" onClick={() => setMessage("🤝 N2N: ARANYA aapke network ko relevant network se jodne ke liye tayyar hai.")}>🤝 Connect network</button>
          </div>
        </div>
        <div className="principle"><b>WALK THE ARANYA</b><span>Real work creates the record. Evidence proves it. Legitimate value can lead to settlement.</span></div>
      </section>
    </main>
  )
}
