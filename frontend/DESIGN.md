1. <design-system>

   # Design Style: Minimalist Modern

   **Core DNA:** Restraint in quantity, confidence in execution. Clean structure with electric blue accents (`#0052FF`), dual-font system (Calistoga display + Inter body), and purposeful whitespace.
   ---

   ## Tokens (CSS Variables)

   ```css
   --background: #FAFAFA;
   --foreground: #0F172A;    /* Also used for inverted sections */
   --muted: #F1F5F9;
   --muted-foreground: #64748B;
   --accent: #0052FF;
   --accent-secondary: #4D7CFF;
   --border: #E2E8F0;
   --card: #FFFFFF;
   ```

   **Gradient:** `linear-gradient(135deg, #0052FF, #4D7CFF)` — used for buttons, icon backgrounds, borders, text highlights.
   ---

   ## Typography

   | Element        | Font           | Size                                     | Weight | Tracking  | Class                      |
   | -------------- | -------------- | ---------------------------------------- | ------ | --------- | -------------------------- |
   | **Hero H1**    | Calistoga      | `text-5xl md:text-6xl lg:text-[5.25rem]` | normal | `-0.02em` | `font-serif`               |
   | **Section H2** | Calistoga      | `text-3xl md:text-[3.25rem]`             | normal | normal    | `font-serif`               |
   | **H3 Card**    | Inter          | `text-lg xl:text-2xl`                    | 600    | `-0.01em` | `font-sans`                |
   | **Body**       | Inter          | `text-base lg:text-lg`                   | 400    | normal    | `leading-7 text-slate-600` |
   | **Label**      | JetBrains Mono | `text-xs`                                | 400    | `0.15em`  | `uppercase font-mono`      |

   **Gradient Text:** `bg-gradient-to-r from-[#0052FF] to-[#4D7CFF] bg-clip-text text-transparent`
   ---

   ## Components

   ### Button Primary

   ```jsx
   <button className="h-12 md:h-14 px-6 md:px-8 rounded-xl bg-gradient-to-r from-[#0052FF] to-[#4D7CFF] text-white font-medium shadow-sm hover:shadow-[0_8px_24px_rgba(0,82,255,0.35)] hover:-translate-y-0.5 hover:brightness-110 active:scale-[0.98] transition-all duration-200">
     Button Text
   </button>
   ```

   ### Button Secondary

   ```jsx
   <button className="h-12 md:h-14 px-6 rounded-xl border border-slate-200 bg-transparent text-slate-900 font-medium hover:bg-slate-50 hover:border-[#0052FF]/30 transition-all duration-200">
     Secondary
   </button>
   ```

   ### Card Standard

   ```jsx
   <div className="rounded-2xl bg-white border border-slate-200 p-6 md:p-8 shadow-md hover:shadow-xl hover:shadow-[0_20px_25px_rgba(0,82,255,0.08)] transition-all duration-300 group">
     {/* Content */}
   </div>
   ```

   ### Card Featured (Gradient Border)

   ```jsx
   <div className="rounded-2xl p-[2px] bg-gradient-to-br from-[#0052FF] via-[#4D7CFF] to-[#0052FF]">
     <div className="h-full w-full rounded-[calc(1rem-2px)] bg-white p-6">
       {/* Content */}
     </div>
   </div>
   ```

   ### Section Label (Badge)

   ```jsx
   <div className="inline-flex items-center gap-3 rounded-full border border-[#0052FF]/30 bg-[#0052FF]/5 px-5 py-2">
     <span className="h-2 w-2 rounded-full bg-[#0052FF] animate-pulse" />
     <span className="font-mono text-xs uppercase tracking-[0.15em] text-[#0052FF]">
       Section Name
     </span>
   </div>
   ```

   ### Input

   ```jsx
   <input className="h-12 md:h-14 w-full rounded-xl border border-slate-200 bg-transparent px-4 text-slate-900 placeholder:text-slate-400 focus:border-[#0052FF] focus:ring-2 focus:ring-[#0052FF] focus:ring-offset-2 transition-all" />
   ```

   ---

   ## Layout Principles

   **Container:** `max-w-6xl mx-auto px-4 sm:px-6 lg:px-8`
   **Section Spacing:** `py-28 md:py-36 lg:py-44`
   **Grid Patterns:**

   ```jsx
   // Hero: Asymmetric text-heavy
   <div className="grid grid-cols-1 lg:grid-cols-[1.1fr_0.9fr] gap-12">
   // Features: Standard 3-col with optional span
   <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
   // Benefits: Content-first asymmetric
   <div className="grid grid-cols-1 lg:grid-cols-[1.2fr_0.8fr] gap-16">
   ```

   **Inverted Sections:** Use `bg-slate-900 text-white` for contrast. Add dot texture:

   ```jsx
   <div className="relative bg-slate-900 text-white">
     <div className="absolute inset-0 opacity-[0.03]" 
          style={{backgroundImage: 'radial-gradient(circle, white 1px, transparent 1px)', backgroundSize: '32px 32px'}} />
     {/* Content */}
   </div>
   ```

   ---

   ## Animation Guidelines

   **Entrance (Framer Motion):**

   ```jsx
   const easeOut = [0.16, 1, 0.3, 1];
   const fadeInUp = {
     hidden: { opacity: 0, y: 28 },
     visible: { opacity: 1, y: 0, transition: { duration: 0.7, ease: easeOut } }
   };
   // Usage with viewport trigger
   <motion.div initial="hidden" whileInView="visible" viewport={{ once: true, amount: 0.15, margin: "-60px" }} variants={fadeInUp}>
   ```

   **Continuous Animations:**

   ```css
   /* Floating cards */
   @keyframes float {
     0%, 100% { transform: translateY(0); }
     50% { transform: translateY(-10px); }
   }
   .animate-float { animation: float 5s ease-in-out infinite; }
   /* Slow rotating ring */
   .animate-spin-slow { animation: spin 60s linear infinite; }
   /* Pulsing dot */
   .animate-pulse-subtle { 
     animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
   }
   ```

   **Hover Patterns:**

   - Buttons: `-translate-y-0.5` + shadow increase
   - Cards: `shadow-xl` + optional gradient overlay
   - Icons: `scale-110` or `group-hover:translate-x-1` for arrows
     **Accessibility:** Respect `prefers-reduced-motion` — disable continuous animations for users who prefer reduced motion.

2. 

   |      |      |
   | ---- | ---- |
   |      |      |
   |      |      |
   |      |      |
   |      |      |
   |      |      |
   |      |      |

3. |      |      |
   | ---- | ---- |
   |      |      |
   |      |      |
   |      |      |
   |      |      |
   |      |      |
   |      |      |