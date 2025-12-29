<p align="center">
  <img src="https://raw.githubusercontent.com/DidCodeHere/SeracTECH-FREE/main/public/logo.png" alt="SeracTECH-FREE Logo" width="200"/>
</p>

<h1 align="center">SeracTECH-FREE</h1>

<p align="center">
  <strong>🏗️ Free, Open-Source UK Planning Application & Construction Lead Generation Platform</strong>
</p>

<p align="center">
  <a href="https://github.com/DidCodeHere/SeracTECH-FREE/stargazers"><img src="https://img.shields.io/github/stars/DidCodeHere/SeracTECH-FREE?style=social" alt="GitHub Stars"></a>
  <a href="https://github.com/DidCodeHere/SeracTECH-FREE/blob/main/LICENSE"><img src="https://img.shields.io/badge/licence-MIT-blue.svg" alt="Licence"></a>
  <a href="https://github.com/DidCodeHere/SeracTECH-FREE/issues"><img src="https://img.shields.io/github/issues/DidCodeHere/SeracTECH-FREE" alt="Issues"></a>
  <img src="https://img.shields.io/badge/Made%20in-UK%20🇬🇧-red" alt="Made in UK">
</p>

<p align="center">
  <a href="#-features">Features</a> •
  <a href="#-demo">Demo</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-coverage">Coverage</a> •
  <a href="#-api">API</a> •
  <a href="#-contributing">Contributing</a>
</p>

---

## 📋 Overview

**SeracTECH-FREE** is a comprehensive, free-to-use platform designed for the UK construction industry. It aggregates planning applications from local councils across England, Scotland, and Wales, providing builders, contractors, tradespeople, and construction businesses with valuable leads at no cost.

### Why SeracTECH-FREE?

- **Completely Free** — No subscriptions, no hidden fees, no premium tiers
- **Open Source** — Fully transparent codebase, community-driven development
- **Nationwide Coverage** — Scrapes data from 100+ UK local planning authorities
- **Real-Time Updates** — Automated daily data synchronisation via GitHub Actions
- **Privacy-First** — No user tracking, no data harvesting, no third-party analytics

---

## ✨ Features

### 🔍 Intelligent Search
- **Postcode-Based Search** — Enter any UK postcode to find nearby planning applications
- **Radius Filtering** — Customisable search radius from 1km to 25km
- **Show All Mode** — Browse all applications nationwide with a single click

### 🗺️ Interactive Map View
- **Leaflet-Powered Maps** — Visualise planning applications geographically
- **Cluster Markers** — Efficient rendering of thousands of data points
- **Click-to-Details** — Tap any marker for full application information

### 📊 Advanced Filtering
- **Status Filter** — Filter by Pending, Approved, or Refused applications
- **Date Range Filter** — Focus on specific time periods
- **Real-Time Results** — Instant filtering without page reloads

### 📥 Export & Lead Management
- **CSV Export** — Download filtered results as spreadsheet-compatible files
- **PDF Reports** — Generate professional reports for your records
- **Lead Cart** — Save and manage promising leads before exporting

### ⚡ Performance Optimised
- **Virtualised Lists** — Smooth scrolling through thousands of results
- **Lazy Loading** — Efficient data fetching for optimal performance
- **Static Site Hosting** — Lightning-fast GitHub Pages deployment

---

## 🎯 Demo

**Live Demo:** [https://didcodehere.github.io/SeracTECH-FREE](https://didcodehere.github.io/SeracTECH-FREE)

<p align="center">
  <img src="https://raw.githubusercontent.com/DidCodeHere/SeracTECH-FREE/main/docs/screenshot.png" alt="SeracTECH-FREE Screenshot" width="800"/>
</p>

---

## 🚀 Quick Start

### Prerequisites

- **Node.js** 18+ (for frontend development)
- **Python** 3.10+ (for scraper)
- **Git** (for version control)

### Installation

```bash
# Clone the repository
git clone https://github.com/DidCodeHere/SeracTECH-FREE.git
cd SeracTECH-FREE

# Install frontend dependencies
npm install

# Install Python scraper dependencies
pip install -r requirements.txt
```

### Development

```bash
# Start the development server
npm run dev

# Run the scraper (fetches latest planning data)
python -m scraper.main
```

### Production Build

```bash
# Build for production
npm run build

# Preview the production build
npm run preview
```

---

## 🗺️ Coverage

SeracTECH-FREE currently scrapes planning data from councils across the United Kingdom:

### England
| Region | Councils |
|--------|----------|
| **South Coast** | Portsmouth, Southampton, Fareham, Gosport, Havant |
| **London** | Lambeth, Tower Hamlets, Bromley, Croydon, Ealing, Greenwich |
| **North** | Leeds, Manchester, Newcastle, Doncaster |
| **Midlands** | Nottingham, Bristol |

### Scotland
| Region | Councils |
|--------|----------|
| **Central** | Glasgow |

### Data Sources

- **Idox Planning Portal** — Primary source for most councils
- **Planning Data API** — Government open data for participating authorities
- **Weekly Lists** — Fallback scraping method for legacy systems

---

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SCRAPER_DAYS` | Number of days to scrape backwards | `1` |
| `SCRAPER_MOCK_MODE` | Use mock data for testing | `false` |
| `SCRAPER_OUTPUT_DIR` | Output directory for JSON files | `public/data` |

### Vite Configuration

The frontend is configured for GitHub Pages deployment with relative paths:

```typescript
// vite.config.ts
export default defineConfig({
  plugins: [react()],
  base: './', // Relative paths for GitHub Pages
})
```

---

## 📁 Project Structure

```
SeracTECH-FREE/
├── .github/
│   └── workflows/
│       ├── daily_scrape.yml    # Automated daily scraping
│       └── deploy.yml          # GitHub Pages deployment
├── public/
│   ├── data/                   # Scraped planning data (JSON)
│   └── logo.png                # Project logo
├── scraper/
│   ├── main.py                 # Main scraper orchestrator
│   ├── idox_scraper.py         # Idox portal scraper
│   └── api_scraper.py          # Planning Data API client
├── src/
│   ├── components/             # React components
│   ├── hooks/                  # Custom React hooks
│   ├── store/                  # Zustand state management
│   └── utils/                  # Utility functions
├── index.html                  # Entry HTML (SEO optimised)
├── package.json                # Node.js dependencies
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

---

## 🤝 Contributing

We welcome contributions from the community! Whether you're fixing bugs, adding new council support, or improving documentation, your help is appreciated.

### How to Contribute

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Adding a New Council

To add support for a new council, update `scraper/main.py`:

```python
COUNCILS = {
    # ... existing councils
    "your_council": {
        "type": "idox",
        "base_url": "https://planning.yourcouncil.gov.uk",
        "enabled": True
    }
}
```

---

## 📜 Licence

This project is licensed under the **MIT Licence** — see the [LICENCE](LICENCE) file for details.

---

## 👨‍💻 Author

**DidCodeHere**

- GitHub: [@DidCodeHere](https://github.com/DidCodeHere)
- Repository: [SeracTECH-FREE](https://github.com/DidCodeHere/SeracTECH-FREE)

---

## 🙏 Acknowledgements

- [Leaflet](https://leafletjs.com/) — Interactive maps
- [React](https://react.dev/) — UI framework
- [Tailwind CSS](https://tailwindcss.com/) — Styling
- [Vite](https://vitejs.dev/) — Build tooling
- [Planning Data API](https://www.planning.data.gov.uk/) — Open government data

---

## 📈 Keywords

`planning applications` `construction leads` `UK planning` `building permits` `council planning` `planning portal` `construction industry` `lead generation` `open source` `free tools` `builders` `contractors` `tradespeople` `property development` `planning permission` `England` `Scotland` `Wales` `local authority` `Idox` `planning data`

---

<p align="center">
  Made with ❤️ in the United Kingdom 🇬🇧
</p>

<p align="center">
  <a href="https://github.com/DidCodeHere/SeracTECH-FREE">⭐ Star this repository if you find it useful!</a>
</p>
