# SeracTECH-FREE: Open Source Construction Lead Generator

## 1. Project Objective

**Value Proposition:** Empower local tradespeople (builders, architects, roofers) with a free, high-speed tool to find relevant planning applications in their area. By democratizing access to this public data, we enable small businesses to generate leads without paying expensive subscription fees.

**Core Philosophy:** Speed, Efficiency, and Simplicity. The tool must run on free infrastructure (GitHub Actions + Pages) and feel instant to the user.

## 2. Performance Strategy

To ensure scalability and responsiveness within free tier limits:

- **Asynchronous Scraping:** Python `aiohttp` will be used to perform concurrent requests, maximizing throughput during the limited GitHub Actions runtime.
- **Incremental Scraping (Delta Updates):** The scraper will read existing data first. It will only fetch applications newer than the latest entry in the dataset, reducing runtime from hours to minutes.
- **JSON Minimization & Sharding:** Data will be stored in small, static JSON files organized by Postcode Sector (e.g., `data/PO/PO1.json`). This ensures the frontend only fetches relevant ~50kb chunks, not a massive database.
- **Frontend Caching:** `TanStack Query` (React Query) will be used with a "stale-while-revalidate" policy. Users see cached data instantly while background updates occur.
- **Virtualization:** Large lists of leads will be rendered using windowing/virtualization techniques to maintain 60fps scrolling.

## 3. Architecture Overview

1.  **Data Source:** UK Local Council Planning Portals (Idox, Northgate, etc.).
2.  **Ingestion (GitHub Actions):**
    - Scheduled Cron Job (Daily).
    - Python Async Scraper (`aiohttp`).
    - Smart filtering (Incremental check).
3.  **Storage (Git Repository):**
    - Structure: `data/{AREA_CODE}/{SECTOR}.json` (e.g., `data/PO/PO1.json`).
    - Format: Minified JSON.
4.  **Presentation (GitHub Pages):**
    - React + Vite SPA.
    - Client-side filtering (Haversine formula).
    - Serverless Export (Web Workers for PDF/CSV generation).

## 4. Data Model

**Folder Structure:**

```text
data/
  ├── PO/
  │   ├── PO1.json
  │   ├── PO2.json
  │   └── ...
  ├── SO/
  │   ├── SO1.json
  │   └── ...
```

**JSON Schema (Planning Application):**

```json
{
  "id": "23/01234/FUL",
  "desc": "Single storey rear extension",
  "addr": "123 High St, Portsmouth, PO1 2AB",
  "postcode": "PO1 2AB",
  "lat": 50.79,
  "lng": -1.09,
  "date_received": "2023-10-25",
  "status": "Pending",
  "link": "https://publicaccess.portsmouth.gov.uk/..."
}
```

_Note: Keys are shortened (`desc`, `addr`) to save bytes._

## 5. Scraper Strategy

- **Pattern:** Strategy Pattern.
  - `BaseScraper`: Abstract class defining `fetch_results`, `parse_html`, `save_data`.
  - `IdoxScraper`: Implementation for Idox systems.
  - `NorthgateScraper`: Implementation for Northgate systems.
- **Politeness:**
  - Respect `robots.txt` (where reasonable/applicable for open data).
  - Implement rate limiting (semaphores) to avoid overwhelming council servers.
  - User-Agent rotation if necessary.
- **Session Persistence:** Reuse `aiohttp.ClientSession` for connection pooling.

## 6. Frontend Architecture

- **Framework:** React + Vite + TypeScript.
- **Styling:** Tailwind CSS.
- **State Management:**
  - **Server State:** TanStack Query (Caching, Deduping, Background Refetch).
  - **Client State:** Zustand (Cart/Selection management).
- **Mapping:** React Leaflet + Supercluster.
- **Export:** `papaparse` (CSV) and `jspdf` (PDF) running in Web Workers.

## 7. Roadmap

- [x] **Phase 1: MVP (Portsmouth)**
  - Setup project structure.
  - Implement `IdoxScraper` for Portsmouth City Council.
  - Basic React UI to search PO postcodes and list results.
- [x] **Phase 2: Expansion**
  - Add `NorthgateScraper`.
  - Map integration.
  - Export functionality.
- [x] **Phase 3: Optimization**
  - Implement incremental scraping logic.
  - Add virtualized lists.
  - Automate via GitHub Actions.
- [x] **Phase 4: UX Enhancements** _(NEW)_
  - Status filtering (Pending/Approved/Refused).
  - Date range filtering with quick presets.
  - Application details modal.
  - Bulk selection (Select All).
  - Responsive mobile-friendly UI.

## 8. Task List

- [x] **Project Setup**
  - [x] Create `project.md`.
  - [x] Initialize Python environment (`requirements.txt`).
  - [x] Initialize React project (`package.json`).
- [x] **Backend (Python)**
  - [x] Create `scraper/base.py` (Async Base Class).
  - [x] Create `scraper/idox.py` (Portsmouth implementation).
  - [x] Create `scraper/northgate.py` (Southampton implementation).
  - [x] Create `scraper/main.py` (Orchestrator).
  - [x] Implement incremental logic (load existing JSON, compare dates).
- [x] **DevOps**
  - [x] Create `.github/workflows/scrape.yml` (Daily scrape automation).
  - [x] Create `.github/workflows/deploy.yml` (GitHub Pages deployment).
  - [x] Setup `frontend/public/data/` for static serving.
- [x] **Frontend (React)**
  - [x] Create `usePlanningData` hook (TanStack Query).
  - [x] Create `usePostcodeLookup` hook (postcodes.io API).
  - [x] Create `useRadiusFilter` hook (Haversine distance filtering).
  - [x] Build Search Component (Postcode lookup + radius slider).
  - [x] Build Results List (VirtualizedList for performance).
  - [x] Build Export Button (CSV/PDF).
  - [x] Build Cart Component (Zustand state).
  - [x] Build Map View (React Leaflet).
  - [x] Add Select All / Bulk selection actions.
  - [x] Add Status Filter (Pending/Approved/Refused).
  - [x] Add Date Range Filter (Quick presets + custom range).
  - [x] Add Application Details Modal (Full info view).
- [ ] **Enhancement Ideas (Backlog)**
  - [ ] Dark Mode Toggle.
  - [ ] Saved Searches (localStorage).
  - [ ] Push Notifications for new applications.
  - [ ] More council scrapers (Birmingham, Manchester, etc.).

## 9. How to Run

**Backend (Scraper):**

```bash
# Install dependencies
pip install -r requirements.txt

# Run the scraper (must be run as a module)
python -m scraper.main
```

**Frontend (UI):**

```bash
cd frontend
npm install
npm run dev
```
