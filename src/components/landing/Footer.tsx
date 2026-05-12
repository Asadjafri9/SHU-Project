export function Footer() {
  return (
    <footer className="bg-[var(--ghost)]">
      <div className="mx-auto max-w-7xl px-6 py-10 flex flex-wrap items-center justify-between gap-4 text-sm text-[var(--ink-soft)]">
        <div className="flex items-center gap-3 font-display text-base text-[var(--ink)]">
          <img src="/logo.png" alt="StandupBot" className="w-8 h-8 object-contain" />
          StandupBot
        </div>
        <div className="font-mono text-xs uppercase tracking-widest">
          Built for Iterate '26 · © {new Date().getFullYear()}
        </div>
        <div className="flex gap-5">
          <a href="#" className="hover:text-[var(--ink)]">Twitter</a>
          <a href="#" className="hover:text-[var(--ink)]">GitHub</a>
          <a href="#" className="hover:text-[var(--ink)]">Privacy</a>
        </div>
      </div>
    </footer>
  );
}
