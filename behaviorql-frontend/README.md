# 🕸️ BehaviorQL Frontend Landing Page

This folder contains the complete, production-ready, ultra-premium React + Vite + Tailwind CSS v4 landing page for **BehaviorQL**—your personal behavior and health monitor powered by Coral.

Built newly and explicitly for the **WeMakeDevs Coral Hackathon**.

---

## 🎨 Design System & Aesthetics (Tailwind v4)
* **Background**: `#070908` (Dark technical obsidian)
* **Surface**: `#0E1110` (Sleek charcoal tiles)
* **Accent**: `#FF6B5A` (Vibrant Coral orange-red)
* **Border**: `#25302B` (Obsidian frame line)
* **Typography**: **Outfit** for clean headers and **JetBrains Mono** for terminal/SQL frames.
* **Glow & Grid**: Integrated custom radial light glows and background structural grid maps.

---

## 🚀 How to Run Locally

### 1. Pre-requisites
* Node.js v18+ & npm installed.

### 2. Install Dependencies
Open your shell in the `behaviorql-frontend/` directory:
```bash
cd behaviorql-frontend
npm install
```

### 3. Launch Development Server
```bash
npm run dev
```
*Accessible at `http://localhost:5173`!*

---

## 📦 Building for Production

Compile all JSX components and PostCSS utilities into a optimized, lightweight static distribution folder (`dist/`):
```bash
npm run build
```
*Builds in under 16 seconds! Outputs clean static `index.html`, `index.css` (23KB), and compiled React bundle JS (224KB).*

---

## 🚀 Deployed Version

For the hackathon submission:
* **Deployed Dashboard URL**: `https://behaviorql.vercel.app/` or `https://behaviorql.netlify.app/` (Deployable in 1 click using Vercel or Netlify directly by selecting this repository subdirectory!)
