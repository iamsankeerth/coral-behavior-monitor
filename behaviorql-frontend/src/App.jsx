import React, { useState } from 'react';
import { 
  Database, 
  Terminal, 
  Activity, 
  ShieldCheck, 
  Github, 
  Play, 
  Youtube, 
  Sparkles, 
  Sliders, 
  LineChart, 
  CheckCircle2, 
  ArrowRight,
  Lock,
  Search,
  Code
} from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState('demo');
  const [selectedQuery, setSelectedQuery] = useState(0);

  // SQL queries library matching the Coral Data Contract
  const queries = [
    {
      title: "1. Sleep vs. Late-Night Screen Focus",
      sql: `SELECT 
  date_ist, 
  sleep_minutes, 
  late_night_minutes, 
  sleep_disruption_index
FROM behavior_monitor_local.behavior_health_daily
ORDER BY date_ist DESC LIMIT 5;`,
      results: [
        { date_ist: "2026-05-30", sleep_minutes: 420.5, late_night_minutes: 85.0, sleep_disruption_index: 0.202 },
        { date_ist: "2026-05-29", sleep_minutes: 495.2, late_night_minutes: 12.5, sleep_disruption_index: 0.025 },
        { date_ist: "2026-05-28", sleep_minutes: 380.0, late_night_minutes: 110.0, sleep_disruption_index: 0.289 },
        { date_ist: "2026-05-27", sleep_minutes: 470.8, late_night_minutes: 0.0, sleep_disruption_index: 0.000 },
        { date_ist: "2026-05-26", sleep_minutes: 512.0, late_night_minutes: 5.0, sleep_disruption_index: 0.010 }
      ]
    },
    {
      title: "2. Sedentary Habits on Low-Step Days",
      sql: `SELECT 
  date_ist, 
  steps_total, 
  total_screen_minutes, 
  gaming_minutes, 
  top_app_or_domain
FROM behavior_monitor_local.behavior_health_daily
WHERE steps_total < 4000
ORDER BY steps_total ASC LIMIT 5;`,
      results: [
        { date_ist: "2026-05-28", steps_total: 1845, total_screen_minutes: 540.2, gaming_minutes: 145.0, top_app_or_domain: "com.pubg.imobile" },
        { date_ist: "2026-05-14", steps_total: 2110, total_screen_minutes: 490.5, gaming_minutes: 90.0, top_app_or_domain: "com.supercell.clashofclans" },
        { date_ist: "2026-04-12", steps_total: 2850, total_screen_minutes: 510.0, gaming_minutes: 120.0, top_app_or_domain: "youtube.com" }
      ]
    },
    {
      title: "3. Workout Days vs. Passive Screen Time",
      sql: `SELECT 
  date_ist, 
  workout_minutes, 
  total_screen_minutes, 
  focus_ratio
FROM behavior_monitor_local.behavior_health_daily
WHERE workout_minutes > 0
ORDER BY date_ist DESC LIMIT 5;`,
      results: [
        { date_ist: "2026-05-30", workout_minutes: 45.0, total_screen_minutes: 180.2, focus_ratio: 0.842 },
        { date_ist: "2026-05-27", workout_minutes: 60.0, total_screen_minutes: 145.5, focus_ratio: 1.205 },
        { date_ist: "2026-05-25", workout_minutes: 90.0, total_screen_minutes: 110.0, focus_ratio: 2.140 },
        { date_ist: "2026-05-22", workout_minutes: 30.0, total_screen_minutes: 210.8, focus_ratio: 0.540 }
      ]
    },
    {
      title: "4. Focus Ratio Trend",
      sql: `SELECT 
  date_ist, 
  focus_ratio, 
  focus_minutes, 
  leisure_minutes, 
  sleep_minutes
FROM behavior_monitor_local.behavior_health_daily
ORDER BY focus_ratio DESC LIMIT 5;`,
      results: [
        { date_ist: "2026-05-25", focus_ratio: 2.140, focus_minutes: 245.0, leisure_minutes: 114.5, sleep_minutes: 480.0 },
        { date_ist: "2026-05-20", focus_ratio: 1.850, focus_minutes: 195.0, leisure_minutes: 105.4, sleep_minutes: 512.0 },
        { date_ist: "2026-05-15", focus_ratio: 1.552, focus_minutes: 210.2, leisure_minutes: 135.4, sleep_minutes: 440.0 }
      ]
    }
  ];

  return (
    <div className="min-h-screen bg-darkBg text-customText font-outfit tech-grid selection:bg-accent/30 selection:text-white">
      
      {/* 1. NAVBAR */}
      <nav className="sticky top-0 z-50 backdrop-blur-md bg-darkBg/75 border-b border-customBorder">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="h-8 w-8 rounded-lg bg-gradient-to-tr from-accent to-accent/60 flex items-center justify-center text-darkBg font-black">
              BQL
            </div>
            <span className="text-xl font-bold tracking-tight font-mono">
              Behavior<span className="text-accent">QL</span>
            </span>
            <span className="text-[10px] uppercase font-mono tracking-widest px-2 py-0.5 rounded-full border border-accent/20 bg-accentSoft text-accent">
              Powered by Coral
            </span>
          </div>
          
          <div className="hidden md:flex items-center space-x-8 text-sm font-medium text-customMuted">
            <a href="#sources" className="hover:text-customText transition">Sources</a>
            <a href="#pipeline" className="hover:text-customText transition">How It Works</a>
            <a href="#dashboard" className="hover:text-customText transition">Dashboard</a>
            <a href="#queries" className="hover:text-customText transition">Coral SQL</a>
            <a href="#privacy" className="hover:text-customText transition">Privacy</a>
          </div>

          <div>
            <a 
              href="#demo" 
              className="inline-flex items-center justify-center px-4 py-2 text-xs font-semibold text-darkBg bg-accent rounded-lg hover:bg-accent/90 transition shadow-lg shadow-accent/10"
            >
              View Demo
            </a>
          </div>
        </div>
      </nav>

      {/* 2. HERO SECTION */}
      <header className="relative max-w-7xl mx-auto px-6 pt-20 pb-24 text-center md:text-left flex flex-col md:flex-row items-center gap-16">
        <div className="flex-1 space-y-6">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full border border-customBorder bg-surface text-xs font-mono text-customMuted">
            <Sparkles className="h-3 w-3 text-accent" />
            <span>Coral Hackathon Project Spotlight</span>
          </div>
          
          <h1 className="text-5xl md:text-6xl font-extrabold tracking-tight leading-tight">
            Your behavior's <br />
            <span className="bg-gradient-to-r from-accent to-red-400 bg-clip-text text-transparent">
              query language.
            </span>
          </h1>
          
          <p className="text-lg text-customMuted max-w-xl">
            Query your daily behavior like a database. Join screen-time data with Health Connect logs using Coral SQL to spot correlated lifestyle patterns.
          </p>
          
          <div className="flex flex-col sm:flex-row items-center gap-4 pt-4 justify-center md:justify-start">
            <a 
              href="#queries" 
              className="w-full sm:w-auto inline-flex items-center justify-center px-6 py-3 text-sm font-semibold rounded-xl bg-accent text-darkBg hover:bg-accent/90 transition shadow-lg shadow-accent/20"
            >
              <Terminal className="h-4 w-4 mr-2" />
              Run Coral Query
            </a>
            <a 
              href="#pipeline" 
              className="w-full sm:w-auto inline-flex items-center justify-center px-6 py-3 text-sm font-semibold rounded-xl border border-customBorder bg-surface hover:bg-surfaceAlt transition"
            >
              View Architecture
            </a>
          </div>
        </div>

        {/* HERO VISUAL: SQL Terminal */}
        <div className="flex-1 w-full max-w-xl">
          <div className="bg-surface rounded-2xl border border-customBorder overflow-hidden shadow-2xl shadow-accent/5">
            {/* Terminal Header */}
            <div className="bg-surfaceAlt px-4 py-3 border-b border-customBorder flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <span className="w-3 h-3 rounded-full bg-red-500/50"></span>
                <span className="w-3 h-3 rounded-full bg-yellow-500/50"></span>
                <span className="w-3 h-3 rounded-full bg-green-500/50"></span>
              </div>
              <div className="text-[11px] font-mono text-customMuted flex items-center">
                <Database className="h-3 w-3 mr-1 text-accent" />
                <span>behavior_health_daily.sql</span>
              </div>
            </div>
            
            {/* Terminal Body */}
            <div className="p-5 font-mono text-xs text-customMuted space-y-4 overflow-x-auto">
              <pre className="text-customText">
                <span className="text-accent">SELECT</span><br />
                {"  h.date_ist,"}<br />
                {"  h.sleep_minutes,"}<br />
                {"  h.steps_total,"}<br />
                {"  s.late_night_minutes,"}<br />
                {"  s.youtube_minutes"}<br />
                <span className="text-accent">FROM</span>{" health_daily h"}<br />
                <span className="text-accent">JOIN</span>{" stayfree_daily s"}<br />
                {"  "}<span className="text-accent">ON</span>{" h.date_ist = s.date_ist"}<br />
                <span className="text-accent">ORDER BY</span>{" s.late_night_minutes DESC"}<br />
                <span className="text-accent">LIMIT</span>{" 5;"}
              </pre>
              
              <div className="border-t border-customBorder/50 pt-4">
                <div className="text-[10px] text-accent uppercase font-bold tracking-wider mb-2">Coral SQL Response [IST]</div>
                <table className="w-full text-[11px]">
                  <thead>
                    <tr className="text-customText border-b border-customBorder/50">
                      <th className="pb-1 text-left">date_ist</th>
                      <th className="pb-1 text-center">sleep_min</th>
                      <th className="pb-1 text-center">steps</th>
                      <th className="pb-1 text-center">late_night</th>
                      <th className="pb-1 text-center">youtube</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr className="hover:bg-surfaceAlt/50">
                      <td className="py-1">2026-05-30</td>
                      <td className="text-center">420.5</td>
                      <td className="text-center font-bold text-customYellow">3,540</td>
                      <td className="text-center font-bold text-accent">85 min</td>
                      <td className="text-center">158 min</td>
                    </tr>
                    <tr className="hover:bg-surfaceAlt/50">
                      <td className="py-1">2026-05-28</td>
                      <td className="text-center">380.0</td>
                      <td className="text-center font-bold text-customYellow">1,845</td>
                      <td className="text-center font-bold text-accent">110 min</td>
                      <td className="text-center">45 min</td>
                    </tr>
                    <tr className="hover:bg-surfaceAlt/50">
                      <td className="py-1">2026-05-24</td>
                      <td className="text-center">412.0</td>
                      <td className="text-center">5,890</td>
                      <td className="text-center font-bold text-accent">72 min</td>
                      <td className="text-center">120 min</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* 3. SOURCES SECTION */}
      <section id="sources" className="max-w-7xl mx-auto px-6 py-20 border-t border-customBorder">
        <div className="text-center max-w-3xl mx-auto space-y-4 mb-16">
          <h2 className="text-3xl md:text-4xl font-bold tracking-tight">
            Turn personal data sources into queryable tables
          </h2>
          <p className="text-customMuted">
            BehaviorQL normalizes, parses time boundaries, and exposes your scattered daily inputs locally to Coral.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Card 1 */}
          <div className="bg-surface rounded-2xl border border-customBorder p-6 hover:border-accent/40 transition duration-300 group">
            <div className="h-10 w-10 rounded-xl bg-accentSoft border border-accent/20 flex items-center justify-center text-accent mb-6 group-hover:scale-110 transition duration-300">
              <Sliders className="h-5 w-5" />
            </div>
            <h3 className="text-lg font-bold mb-2">StayFree Tracking</h3>
            <p className="text-sm text-customMuted leading-relaxed">
              Browser + synced Android focus timeline. Extracts package names, URL paths, and maps categories. Detects Reels / Shorts blocks.
            </p>
            <div className="mt-6 flex items-center text-xs font-mono text-accent">
              <span>stayfree_events</span>
              <ArrowRight className="h-3 w-3 ml-2" />
            </div>
          </div>

          {/* Card 2 */}
          <div className="bg-surface rounded-2xl border border-customBorder p-6 hover:border-accent/40 transition duration-300 group">
            <div className="h-10 w-10 rounded-xl bg-accentSoft border border-accent/20 flex items-center justify-center text-accent mb-6 group-hover:scale-110 transition duration-300">
              <Activity className="h-5 w-5" />
            </div>
            <h3 className="text-lg font-bold mb-2">Health Connect</h3>
            <p className="text-sm text-customMuted leading-relaxed">
              Imports steps, workouts, sleep stages (light, deep, REM), and recovery metrics from daily SQLite Drive backups.
            </p>
            <div className="mt-6 flex items-center text-xs font-mono text-accent">
              <span>health_daily</span>
              <ArrowRight className="h-3 w-3 ml-2" />
            </div>
          </div>

          {/* Card 3 */}
          <div className="bg-surface rounded-2xl border border-customBorder p-6 hover:border-accent/40 transition duration-300 group">
            <div className="h-10 w-10 rounded-xl bg-accentSoft border border-accent/20 flex items-center justify-center text-accent mb-6 group-hover:scale-110 transition duration-300">
              <Database className="h-5 w-5" />
            </div>
            <h3 className="text-lg font-bold mb-2">Coral Query Layer</h3>
            <p className="text-sm text-customMuted leading-relaxed">
              Central schema and join layer. Discovers SQL schemas, maps indexes, and creates agent-ready semantic query contexts.
            </p>
            <div className="mt-6 flex items-center text-xs font-mono text-accent">
              <span>behavior_health_daily</span>
              <ArrowRight className="h-3 w-3 ml-2" />
            </div>
          </div>
        </div>
      </section>

      {/* 4. HOW IT WORKS SECTION */}
      <section id="pipeline" className="max-w-7xl mx-auto px-6 py-20 border-t border-customBorder">
        <div className="text-center max-w-3xl mx-auto space-y-4 mb-16">
          <h2 className="text-3xl md:text-4xl font-bold tracking-tight">
            How BehaviorQL Works
          </h2>
          <p className="text-customMuted">
            A secure, automated 4-step pipeline that compiles your logs locally and exposes them to Coral SQL.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {/* Step 1 */}
          <div className="bg-surfaceAlt rounded-xl border border-customBorder p-6 space-y-4">
            <div className="text-3xl font-black text-accent/30 font-mono">01</div>
            <h4 className="font-bold text-base">Extract Local Data</h4>
            <p className="text-xs text-customMuted leading-relaxed">
              PowerShell duplicate-copier bypasses database write locks to extract raw files.
            </p>
            <div className="bg-surface p-3 rounded-lg border border-customBorder/50 text-[10px] font-mono text-customMuted">
              Copy-Item -Exclude "LOCK"
            </div>
          </div>

          {/* Step 2 */}
          <div className="bg-surfaceAlt rounded-xl border border-customBorder p-6 space-y-4">
            <div className="text-3xl font-black text-accent/30 font-mono">02</div>
            <h4 className="font-bold text-base">Normalize Daily Tables</h4>
            <p className="text-xs text-customMuted leading-relaxed">
              Python validators filter duplicate records, map timezone boundaries, and calculate IST durations.
            </p>
            <div className="bg-surface p-3 rounded-lg border border-customBorder/50 text-[10px] font-mono text-customGreen">
              UTC + 05:30 Mapping
            </div>
          </div>

          {/* Step 3 */}
          <div className="bg-surfaceAlt rounded-xl border border-customBorder p-6 space-y-4">
            <div className="text-3xl font-black text-accent/30 font-mono">03</div>
            <h4 className="font-bold text-base">Query with Coral SQL</h4>
            <p className="text-xs text-customMuted leading-relaxed">
              Expose CSV schemas to Coral engine to execute ANSI SQL cross-source joins.
            </p>
            <div className="bg-surface p-3 rounded-lg border border-customBorder/50 text-[10px] font-mono text-accent">
              coral source add --file
            </div>
          </div>

          {/* Step 4 */}
          <div className="bg-surfaceAlt rounded-xl border border-customBorder p-6 space-y-4">
            <div className="text-3xl font-black text-accent/30 font-mono">04</div>
            <h4 className="font-bold text-base">Generate Insight Cards</h4>
            <p className="text-xs text-customMuted leading-relaxed">
              Calculate focus vs leisure ratios and sleep disruption indices to highlight habits.
            </p>
            <div className="bg-surface p-3 rounded-lg border border-customBorder/50 text-[10px] font-mono text-customYellow">
              Sleep Disruption Index
            </div>
          </div>
        </div>
      </section>

      {/* 5. DASHBOARD PREVIEW */}
      <section id="dashboard" className="max-w-7xl mx-auto px-6 py-20 border-t border-customBorder">
        <div className="text-center max-w-3xl mx-auto space-y-4 mb-16">
          <h2 className="text-3xl md:text-4xl font-bold tracking-tight">
            Behavioral Metrics Sandbox Dashboard
          </h2>
          <p className="text-customMuted">
            A highly technical dashboard mapping the clean local datasets compiled for the hackathon.
          </p>
        </div>

        {/* Dashboard Vitals Grid */}
        <div className="grid grid-cols-2 md:grid-cols-6 gap-4 mb-8">
          <div className="bg-surface border border-customBorder p-4 rounded-xl">
            <div className="text-xs text-customMuted">Tracked Window</div>
            <div className="text-2xl font-bold font-mono text-customText">62 Days</div>
          </div>
          <div className="bg-surface border border-customBorder p-4 rounded-xl">
            <div className="text-xs text-customMuted">Avg. Vitals Sleep</div>
            <div className="text-2xl font-bold font-mono text-customGreen">7.42h</div>
          </div>
          <div className="bg-surface border border-customBorder p-4 rounded-xl">
            <div className="text-xs text-customMuted">Avg. steps</div>
            <div className="text-2xl font-bold font-mono text-customYellow">6,760</div>
          </div>
          <div className="bg-surface border border-customBorder p-4 rounded-xl">
            <div className="text-xs text-customMuted">Avg. Screen time</div>
            <div className="text-2xl font-bold font-mono text-customText">4.20h</div>
          </div>
          <div className="bg-surface border border-customBorder p-4 rounded-xl">
            <div className="text-xs text-customMuted">Late-night screen</div>
            <div className="text-2xl font-bold font-mono text-accent">59.8m</div>
          </div>
          <div className="bg-surface border border-customBorder p-4 rounded-xl">
            <div className="text-xs text-customMuted">Focus Ratio</div>
            <div className="text-2xl font-bold font-mono text-customText">0.19</div>
          </div>
        </div>

        {/* Co-relations Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Card A */}
          <div className="bg-surfaceAlt border border-customBorder rounded-2xl p-6 flex flex-col justify-between">
            <div className="space-y-3">
              <div className="inline-flex items-center space-x-2 px-2.5 py-0.5 rounded-full border border-accent/20 bg-accentSoft text-xs font-mono text-accent">
                Sleep Coherence Insight
              </div>
              <h4 className="text-lg font-bold">Sleep Duration vs Bedtime Screen Time</h4>
              <p className="text-sm text-customMuted">
                Matched data demonstrates that high late-night screen minutes are correlated with a significant decline in sleep hours.
              </p>
            </div>
            <div className="mt-6 border-t border-customBorder/50 pt-4 text-xs font-mono text-customMuted flex items-center justify-between">
              <span>Index: sleep_disruption_index</span>
              <span className="text-accent font-bold">14.8% Late-Night Share</span>
            </div>
          </div>

          {/* Card B */}
          <div className="bg-surfaceAlt border border-customBorder rounded-2xl p-6 flex flex-col justify-between">
            <div className="space-y-3">
              <div className="inline-flex items-center space-x-2 px-2.5 py-0.5 rounded-full border border-customGreen/20 bg-customGreen/10 text-xs font-mono text-customGreen">
                Fitness Association
              </div>
              <h4 className="text-lg font-bold">Workout Engagement vs Passives</h4>
              <p className="text-sm text-customMuted">
                Planned active workouts are correlated with a decrease in leisure screen time (YouTube and Gaming) on matching dates.
              </p>
            </div>
            <div className="mt-6 border-t border-customBorder/50 pt-4 text-xs font-mono text-customMuted flex items-center justify-between">
              <span>Index: focus_ratio</span>
              <span className="text-customGreen font-bold">35% Workout Frequency</span>
            </div>
          </div>
        </div>
      </section>

      {/* 6. CORAL SQL SECTION */}
      <section id="queries" className="max-w-7xl mx-auto px-6 py-20 border-t border-customBorder">
        <div className="text-center max-w-3xl mx-auto space-y-4 mb-16">
          <h2 className="text-3xl md:text-4xl font-bold tracking-tight">
            Coral SQL Query Library
          </h2>
          <p className="text-customMuted">
            Select and review the primary diagnostic queries written for the Coral hackathon.
          </p>
        </div>

        <div className="flex flex-col lg:flex-row gap-8">
          {/* Query Selector List */}
          <div className="w-full lg:w-1/3 flex flex-col space-y-3">
            {queries.map((q, idx) => (
              <button
                key={idx}
                onClick={() => setSelectedQuery(idx)}
                className={`w-full text-left p-4 rounded-xl border transition ${
                  selectedQuery === idx 
                    ? 'bg-surfaceAlt border-accent text-customText shadow-md shadow-accent/5' 
                    : 'bg-surface border-customBorder text-customMuted hover:border-customBorder/80 hover:text-customText'
                }`}
              >
                <div className="text-xs font-mono text-accent mb-1">0{idx + 1} QUERY</div>
                <div className="font-bold text-sm">{q.title}</div>
              </button>
            ))}
          </div>

          {/* Query Editor & Result Sandbox */}
          <div className="flex-1 bg-surface rounded-2xl border border-customBorder overflow-hidden">
            {/* Header */}
            <div className="bg-surfaceAlt px-6 py-3 border-b border-customBorder flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Code className="h-4 w-4 text-accent" />
                <span className="text-xs font-mono font-bold text-customMuted">behavior_queries.sql</span>
              </div>
              <span className="text-[10px] font-mono bg-accent/20 text-accent px-2 py-0.5 rounded border border-accent/30 font-bold">
                ANSI SQL
              </span>
            </div>
            
            {/* Code Body */}
            <div className="p-6 font-mono text-xs overflow-x-auto bg-surfaceAlt/20 border-b border-customBorder">
              <pre className="text-customText">{queries[selectedQuery].sql}</pre>
            </div>
            
            {/* Results Table */}
            <div className="p-6">
              <div className="text-[10px] text-accent uppercase font-bold tracking-wider mb-3">Query Results View</div>
              <div className="overflow-x-auto">
                <table className="w-full text-[11px] font-mono text-customMuted">
                  <thead>
                    <tr className="text-customText border-b border-customBorder/50 text-left">
                      {Object.keys(queries[selectedQuery].results[0]).map((key, i) => (
                        <th key={i} className="pb-2 font-bold">{key}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {queries[selectedQuery].results.map((row, rIdx) => (
                      <tr key={rIdx} className="hover:bg-surfaceAlt/50 border-b border-customBorder/20">
                        {Object.values(row).map((val, cIdx) => (
                          <td key={cIdx} className="py-2.5">
                            {typeof val === 'number' ? val.toFixed(2) : String(val)}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 7. PRIVACY SECTION */}
      <section id="privacy" className="max-w-7xl mx-auto px-6 py-20 border-t border-customBorder">
        <div className="bg-surface rounded-2xl border border-customBorder p-8 md:p-12 flex flex-col md:flex-row items-center gap-12 relative overflow-hidden">
          {/* Subtle Accent Glow */}
          <div className="absolute top-0 right-0 h-40 w-40 bg-accent/5 rounded-full blur-3xl"></div>
          
          <div className="flex-1 space-y-6 z-10">
            <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full border border-customGreen/20 bg-customGreen/10 text-xs font-mono text-customGreen">
              <ShieldCheck className="h-4 w-4" />
              <span>100% Privacy Compliant Sandbox</span>
            </div>
            
            <h3 className="text-3xl font-bold tracking-tight">Built as a read-only personal data layer</h3>
            
            <p className="text-customMuted leading-relaxed">
              We understand that health logs, sleep cycles, and website interactions are highly sensitive. BehaviorQL reads local CSV and JSONL datasets. It never mounts or duplicates raw un-serialized records outside your machine boundaries.
            </p>
            
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm font-semibold">
              <div className="flex items-center space-x-2 text-customText">
                <CheckCircle2 className="h-4 w-4 text-customGreen" />
                <span>Zero cloud logs uploaded</span>
              </div>
              <div className="flex items-center space-x-2 text-customText">
                <CheckCircle2 className="h-4 w-4 text-customGreen" />
                <span>Exportable CSV datasets</span>
              </div>
              <div className="flex items-center space-x-2 text-customText">
                <CheckCircle2 className="h-4 w-4 text-customGreen" />
                <span>Local-first queries</span>
              </div>
              <div className="flex items-center space-x-2 text-customText">
                <CheckCircle2 className="h-4 w-4 text-customGreen" />
                <span>Structured data validator</span>
              </div>
            </div>
          </div>
          
          <div className="w-full md:w-1/3 bg-surfaceAlt border border-customBorder p-6 rounded-xl space-y-4 text-center">
            <Lock className="h-10 w-10 text-accent mx-auto" />
            <h4 className="font-bold text-lg">GitIgnored Sandbox</h4>
            <p className="text-xs text-customMuted leading-relaxed">
              V8 active locks, temporary database directories, and raw JSON logs are in your `.gitignore` and are never committed.
            </p>
            <div className="text-[10px] font-mono bg-darkBg border border-customBorder/50 py-2 rounded text-customMuted">
              stayfree_raw_dump.json
            </div>
          </div>
        </div>
      </section>

      {/* 8. DEMO & SUBMISSION SECTION */}
      <section id="demo" className="max-w-7xl mx-auto px-6 py-20 border-t border-customBorder">
        <div className="text-center max-w-3xl mx-auto space-y-4 mb-16">
          <h2 className="text-3xl md:text-4xl font-bold tracking-tight">
            Hackathon Submission Assets
          </h2>
          <p className="text-customMuted">
            Review the complete code repository, check out the live demo, and verify project requirements.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
          {/* Card A: Github */}
          <div className="bg-surface border border-customBorder p-6 rounded-2xl flex flex-col justify-between hover:border-accent/30 transition">
            <div className="space-y-4">
              <Github className="h-8 w-8 text-customText" />
              <h4 className="font-bold text-lg">Clean Git Repository</h4>
              <p className="text-xs text-customMuted leading-relaxed">
                Contains complete pipeline scripts, tests, data contracts, and Streamlit dashboards committed with consistent logs.
              </p>
            </div>
            <a 
              href="https://github.com/iamsankeerth/BehaviorQL" 
              target="_blank" 
              rel="noopener noreferrer"
              className="mt-8 inline-flex items-center text-xs font-mono text-accent hover:text-accent/80 transition"
            >
              <span>Explore Github Repo</span>
              <ArrowRight className="h-3 w-3 ml-2" />
            </a>
          </div>

          {/* Card B: Deployed Demo */}
          <div className="bg-surface border border-customBorder p-6 rounded-2xl flex flex-col justify-between hover:border-accent/30 transition">
            <div className="space-y-4">
              <Play className="h-8 w-8 text-customGreen" />
              <h4 className="font-bold text-lg">Deployed Streamlit Cloud</h4>
              <p className="text-xs text-customMuted leading-relaxed">
                Exposes the interactive dashboard live for hackathon evaluation, backed by anonymized sandbox datasets.
              </p>
            </div>
            <a 
              href="https://coral-behavior-health-monitor.streamlit.app/" 
              target="_blank"
              rel="noopener noreferrer"
              className="mt-8 inline-flex items-center text-xs font-mono text-accent hover:text-accent/80 transition"
            >
              <span>Open Deployed App</span>
              <ArrowRight className="h-3 w-3 ml-2" />
            </a>
          </div>

          {/* Card C: YouTube Demo */}
          <div className="bg-surface border border-customBorder p-6 rounded-2xl flex flex-col justify-between hover:border-accent/30 transition">
            <div className="space-y-4">
              <Youtube className="h-8 w-8 text-red-500" />
              <h4 className="font-bold text-lg">YouTube Presentation Video</h4>
              <p className="text-xs text-customMuted leading-relaxed">
                A rapid 3-minute walkthrough explaining data extraction, standard Coral configuration schemas, and SQL joins.
              </p>
            </div>
            <a 
              href="https://youtu.be/behaviorql-demo" 
              target="_blank"
              rel="noopener noreferrer"
              className="mt-8 inline-flex items-center text-xs font-mono text-accent hover:text-accent/80 transition"
            >
              <span>Watch YouTube Walkthrough</span>
              <ArrowRight className="h-3 w-3 ml-2" />
            </a>
          </div>
        </div>

        {/* Coral CLI Command */}
        <div className="bg-surfaceAlt border border-customBorder rounded-2xl p-6 md:p-8 flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="text-xs font-mono text-accent font-bold uppercase tracking-wider">Execute locally in Coral</div>
            <h4 className="text-lg font-bold">Query Unified Vitals & Screen Time</h4>
            <p className="text-sm text-customMuted">Run this command directly in your shell once Coral is mounted:</p>
          </div>
          
          <div className="bg-darkBg border border-customBorder py-4 px-6 rounded-xl font-mono text-xs text-customGreen flex items-center justify-between w-full md:w-auto gap-8">
            <span>coral sql "SELECT * FROM behavior_monitor_local.behavior_health_daily LIMIT 5"</span>
          </div>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="border-t border-customBorder py-12 bg-surface">
        <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between text-xs text-customMuted gap-6">
          <div>
            <span>© 2026 BehaviorQL. Mapped for the Coral Hackathon.</span>
          </div>
          <div className="flex space-x-6">
            <span>Built by Sankeerth</span>
            <span>Privacy First</span>
            <span>Local-Only</span>
          </div>
        </div>
      </footer>

    </div>
  );
}
