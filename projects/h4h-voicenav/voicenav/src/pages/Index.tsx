import { motion } from "framer-motion";
import { Mic, Eye, AudioLines, Github, ArrowRight } from "lucide-react";

const fadeUp = (delay = 0) => ({
  initial: { opacity: 0, y: 24 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.6, delay, ease: [0.22, 1, 0.36, 1] },
});

const fadeIn = (delay = 0) => ({
  initial: { opacity: 0 },
  animate: { opacity: 1 },
  transition: { duration: 0.6, delay },
});

const steps = [
  { n: "01", title: "Install", desc: "Add the Chrome extension in one click." },
  { n: "02", title: "Speak", desc: 'Say "read the article" or "click login".' },
  { n: "03", title: "AI Parses", desc: "Your page HTML is sent to the vision LLM on AMD Dev Cloud." },
  { n: "04", title: "Hear & Act", desc: "ElevenLabs reads back a natural response and executes your command." },
];

const hackathonQA = [
  {
    q: "Inspiration",
    a: "Millions of blind and low-vision users struggle with websites never built for them. Existing screen readers announce raw structure, \"button\", \"link\", without context. We wanted AI that actually understands a page the way a person does.",
  },
  {
    q: "What it does",
    a: "VoiceNav is a Chrome extension that describes any webpage in natural language and lets users navigate entirely by voice, speaking commands like \"open the article\" or \"go to my assignments\" and having them executed automatically.",
  },
  {
    q: "How we built it",
    a: "Three components: a Chrome extension that extracts clean page structure, a FastAPI backend with routes for description and command processing, and a vision LLM deployed on AMD Dev Cloud via vLLM. Voice input via Google Web Speech API; output via ElevenLabs.",
  },
  {
    q: "Challenges",
    a: "Getting the agent to reliably interact with any webpage, fine-tuning prompts for natural-sounding descriptions, and compressing HTML into a format the LLM could parse while preserving the selectors needed to execute actions.",
  },
  {
    q: "Accomplishments",
    a: "VoiceNav works end-to-end on real websites. Page descriptions sound genuinely natural. We deployed on AMD Dev Cloud with latency low enough for real-time use, and our semantic pipeline compresses full pages by over 90%.",
  },
  {
    q: "What we learned",
    a: "Prompt examples matter more than prompt rules. Building for accessibility forces a different kind of precision, every word in a description has to earn its place.",
  },
  {
    q: "What's next",
    a: "Full form-filling support, persistent user context for frequently visited sites, ElevenLabs voice cloning for a personalized assistant, and expanding to support motor and cognitive disabilities.",
  },
];

export default function Index() {
  return (
    <div className="min-h-screen bg-background text-foreground font-body">
      {/* ── Navbar ── */}
      <motion.header
        {...fadeIn(0)}
        className="fixed top-0 inset-x-0 z-50 border-b border-border/60 bg-background/80 backdrop-blur-md"
      >
        <div className="max-w-5xl mx-auto px-6 h-14 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <img src="/src/logos/logo.png" alt="VoiceNav" className="h-15 w-10 rounded-md" />
          </div>
          <nav className="hidden md:flex items-center gap-6 text-sm text-muted-foreground">
            <a href="#how" className="hover:text-foreground transition-colors">How it works</a>
            <a href="#story" className="hover:text-foreground transition-colors">Project story</a>
          </nav>
          <a
            href="https://github.com/eric-kimm/ai-screen-reader"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 text-sm font-semibold text-primary hover:underline transition"
          >
            <Github className="w-4 h-4" />
            GitHub
          </a>
        </div>
      </motion.header>

      <main className="max-w-5xl mx-auto px-6 pt-28 pb-24 space-y-32">

        {/* ── Hero ── */}
        <section className="text-center space-y-6">
          <motion.div {...fadeUp(0)}>
            <span className="inline-flex items-center gap-2 text-xs font-medium tracking-widest uppercase text-muted-foreground border border-border rounded-full px-4 py-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse" />
              Hack For Humanity 2026
            </span>
          </motion.div>

          <motion.h1
            {...fadeUp(0.1)}
            className="text-6xl md:text-8xl font-display font-bold leading-[0.9] tracking-tight"
          >
            <span className="text-gradient">VoiceNav</span>
            <br />
            <span className="text-3xl md:text-5xl font-normal text-foreground/70">
              Browse the web with your voice.
            </span>
          </motion.h1>

          <motion.p
            {...fadeUp(0.2)}
            className="text-lg text-muted-foreground max-w-xl mx-auto leading-relaxed"
          >
            An AI-powered Chrome extension that makes the internet truly accessible
            for the visually impaired and physically disabled, powered by a vision LLM
            and natural voice synthesis.
          </motion.p>

          <motion.div {...fadeUp(0.3)} className="flex items-center justify-center gap-4 pt-2">
            <a
              href="https://github.com/eric-kimm/ai-screen-reader"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 bg-primary text-white text-sm font-semibold px-6 py-3 rounded-xl hover:bg-primary/90 transition"
            >
              <Mic className="w-4 h-4" />
              Try the Extension
              <ArrowRight className="w-4 h-4" />
            </a>
          </motion.div>

          <br></br>

          <motion.div {...fadeUp(0)}>
            <span className="inline-flex items-center gap-2 text-xs font-medium tracking-widest uppercase text-muted-foreground border border-border rounded-full px-4 py-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse" />
              Eric Kim, Stefan Murphy, Austin Kim, Aarav Mehta
            </span>
          </motion.div>
        </section>

        {/* ── Demo ── */}
        <section id="demo" className="text-center space-y-6">
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="text-4xl md:text-5xl font-display font-bold"
          >
            See it <span className="text-gradient">in action</span>
          </motion.h2>

          {/* ↓ Replace this URL with your YouTube/Loom link when ready */}
          {false ? (
            <div className="aspect-video rounded-2xl overflow-hidden border border-border">
              <iframe
                src="https://YOUR_VIDEO_EMBED_URL_HERE"
                className="w-full h-full"
                allowFullScreen
              />
            </div>
          ) : (
            <div className="aspect-video rounded-2xl border-2 border-dashed border-border flex items-center justify-center bg-muted/30">
              <p className="text-muted-foreground text-sm">Demo video coming soon</p>
            </div>
          )}
        </section>


        {/* ── Three pillars ── */}
        <section>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="grid md:grid-cols-3 gap-5"
          >
            {[
              { Icon: Mic, title: "Voice Navigation", body: "Speak naturally to browse, click links, fill forms, no mouse needed." },
              { Icon: Eye, title: "Vision AI", body: "A vision LLM on AMD Dev Cloud understands your page like a human would." },
              { Icon: AudioLines, title: "Natural Speech", body: "ElevenLabs delivers warm, human-sounding feedback, not robotic readouts." },
            ].map(({ Icon, title, body }, i) => (
              <motion.div
                key={title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: i * 0.1 }}
                className="rounded-2xl border border-border bg-card p-7 group hover:border-primary/30 hover:shadow-sm transition-all duration-300"
              >
                <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center mb-5 group-hover:bg-primary/20 transition-colors">
                  <Icon className="w-5 h-5 text-primary" />
                </div>
                <h3 className="font-display font-semibold text-base mb-2">{title}</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">{body}</p>
              </motion.div>
            ))}
          </motion.div>
        </section>

        {/* ── How it works ── */}
        <section id="how">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="mb-12 text-center"
          >
            <h2 className="text-4xl md:text-5xl font-display font-bold mb-3">
              How it <span className="text-gradient">works</span>
            </h2>
            <p className="text-muted-foreground">From install to interaction in under a minute.</p>
          </motion.div>

          <div className="grid md:grid-cols-4 gap-5">
            {steps.map((s, i) => (
              <motion.div
                key={s.n}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: i * 0.1 }}
                className="rounded-2xl border border-border bg-card p-6"
              >
                <span className="text-xs font-bold tracking-widest text-primary font-display">{s.n}</span>
                <h3 className="font-display font-semibold text-base mt-2 mb-1">{s.title}</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">{s.desc}</p>
              </motion.div>
            ))}
          </div>
        </section>

        {/* ── Tech stack ── */}
        <section>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="mb-10 text-center"
          >
            <h2 className="text-4xl md:text-5xl font-display font-bold mb-3">
              Built <span className="text-gradient">with</span>
            </h2>
          </motion.div>

          <div className="flex flex-wrap justify-center gap-3">
            {[
              ["Chrome Extension", "Page capture & command execution"],
              ["FastAPI", "High-performance Python backend"],
              ["AMD Dev Cloud", "Vision LLM inference via vLLM"],
              ["ElevenLabs", "Natural voice synthesis"],
              ["Google Web Speech", "Voice input API"],
            ].map(([name, detail], i) => (
              <motion.div
                key={name}
                initial={{ opacity: 0, scale: 0.95 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ duration: 0.4, delay: i * 0.07 }}
                className="rounded-xl border border-border bg-card px-5 py-3 text-center hover:border-primary/30 transition-colors"
              >
                <div className="font-display font-semibold text-sm">{name}</div>
                <div className="text-xs text-muted-foreground mt-0.5">{detail}</div>
              </motion.div>
            ))}
          </div>
        </section>

        {/* ── Hackathon story ── */}
        <section id="story">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="mb-12 text-center"
          >
            <h2 className="text-4xl md:text-5xl font-display font-bold mb-3">
              Project <span className="text-gradient">story</span>
            </h2>
          </motion.div>

          <div className="space-y-10">
            {hackathonQA.map(({ q, a }, i) => (
              <motion.div
                key={q}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: i * 0.05 }}
                className="grid md:grid-cols-[200px_1fr] gap-4 items-start border-t border-border pt-8 first:border-0 first:pt-0"
              >
                <h3 className="font-display font-semibold text-base text-primary">{q}</h3>
                <p className="text-foreground/80 leading-relaxed text-base">{a}</p>
              </motion.div>
            ))}
          </div>
        </section>

      </main>

      {/* ── Footer ── */}
      <footer className="border-t border-border py-8 px-6">
        <div className="max-w-5xl mx-auto flex items-center justify-between text-sm text-muted-foreground">
          <img src="/src/logos/logo2.png" alt="VoiceNav" className="h-12 w-auto" />
        </div>
      </footer>
    </div>
  );
}