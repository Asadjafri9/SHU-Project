import { Reveal } from "./Reveal";

export function Features() {
  return (
    <section id="features" className="border-b border-[var(--line-strong)] bg-[var(--surface-2)]">
      <div className="mx-auto max-w-7xl px-6 py-24">
        <Reveal className="section-label mb-4">What's inside</Reveal>
        <div className="flex items-end justify-between flex-wrap gap-6 mb-14">
          <Reveal variant="mask" as="h2" className="font-display font-bold text-5xl md:text-7xl text-[var(--ink)] max-w-3xl">
            Cross-person reasoning. Not another todo list.
          </Reveal>
          <Reveal className="text-[var(--ink-soft)] max-w-sm">
            Six things a WhatsApp group can't do — and ChatGPT can't either, unless someone manually paste-collects every update.
          </Reveal>
        </div>

        <Reveal variant="stagger" className="grid md:grid-cols-3 gap-4">
          {/* Big card */}
          <article className="md:col-span-2 md:row-span-2 box box-shadow-hard p-8 flex flex-col justify-between min-h-[360px] relative overflow-hidden">
            <div className="absolute inset-0 bg-grid opacity-40" />
            <div className="relative">
              <span className="pill mb-6">Hero feature</span>
              <h3 className="font-display text-4xl md:text-5xl text-[var(--ink)] leading-[0.95] max-w-lg">
                AI reads <em className="not-italic text-[var(--persian)]">everyone's</em> updates together.
              </h3>
              <p className="mt-4 max-w-md text-[var(--ink-soft)]">
                One prompt, all submissions, full project context. The brief names dependencies a single chat could never surface.
              </p>
            </div>
            <div className="relative mt-8 grid grid-cols-3 gap-3 text-xs font-mono">
              {["AHMED → blocked", "ZAIN ← can unblock", "SARA · new"].map((t) => (
                <div key={t} className="border border-[var(--line-strong)] bg-[var(--ghost)] px-3 py-2">{t}</div>
              ))}
            </div>
          </article>

          <FeatureCard
            kicker="01"
            title="90-second submit"
            body="Three questions. One screen. Members are in and out before their coffee cools."
          />
          <FeatureCard
            kicker="02"
            title="New joiner welcome"
            body="The brief automatically introduces anyone running their first standup."
          />
          <FeatureCard
            kicker="03"
            title="Live streaming brief"
            body="Tokens render as the model thinks. Generated in under 15 seconds."
          />
          <FeatureCard
            kicker="04"
            title="Role-tagged invite links"
            body="Generate a link with a role baked in. Drop it in WhatsApp. Done."
          />
          <FeatureCard
            kicker="05"
            title="Color-coded risk"
            body="Blockers red, shipped green, missing amber, welcomes blue. Scan in 5 seconds."
            wide
          />
        </Reveal>
      </div>
    </section>
  );
}

function FeatureCard({
  kicker, title, body, accent, wide,
}: { kicker: string; title: string; body: string; accent?: boolean; wide?: boolean }) {
  return (
    <article
      className={`box box-shadow-hard p-6 ${wide ? "md:col-span-2" : ""} ${
        accent ? "bg-[var(--persian)] text-white" : ""
      }`}
    >
      <div className={`font-mono text-xs ${accent ? "text-white/70" : "text-[var(--ink-soft)]"}`}>{kicker}</div>
      <h3 className={`font-display text-2xl mt-3 ${accent ? "text-white" : "text-[var(--ink)]"}`}>{title}</h3>
      <p className={`mt-2 text-sm ${accent ? "text-white/90" : "text-[var(--ink-soft)]"}`}>{body}</p>
    </article>
  );
}
