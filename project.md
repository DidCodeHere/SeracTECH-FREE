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

- **Pattern:** Strategy Pattern with full implementation.
  - `BaseScraper`: Abstract class defining `fetch_applications`, `parse_results`, `save_data`.
  - `IdoxScraper`: Implementation for Idox Public Access systems (Portsmouth, Havant, Gosport).
  - `NorthgateScraper`: Implementation for Northgate Planning Explorer systems (Southampton, Fareham).
- **Geocoding:** `Geocoder` class using postcodes.io API for lat/lng enrichment.
- **Politeness:**
  - Token bucket rate limiting (`RateLimiter` class) - 1 req/sec default.
  - Exponential backoff retry logic (`RetryConfig` class).
  - Session persistence via `aiohttp.ClientSession` for connection pooling.
- **Incremental Scraping:**
  - Metadata tracking in `data/_metadata.json`.
  - Automatic date range calculation from last successful scrape.
  - Deduplication on save (by application ID).

**Scraper Modules:**

```text
scraper/
  ├── __init__.py       # Package exports
  ├── base.py           # BaseScraper abstract class
  ├── idox.py           # Idox system scraper (Portsmouth, etc.)
  ├── northgate.py      # Northgate system scraper (Southampton, etc.)
  ├── geocoder.py       # postcodes.io geocoding with bulk lookup
  ├── rate_limiter.py   # Rate limiting & retry utilities
  └── main.py           # Orchestration & CLI entry point
```

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
  - [x] Create `scraper/idox.py` (Portsmouth implementation with real scraping).
  - [x] Create `scraper/northgate.py` (Southampton implementation with real scraping).
  - [x] Create `scraper/geocoder.py` (postcodes.io integration with bulk lookup).
  - [x] Create `scraper/rate_limiter.py` (Token bucket + exponential backoff).
  - [x] Create `scraper/main.py` (Orchestrator with metadata tracking).
  - [x] Implement incremental logic (metadata-based date tracking).
  - [x] Add mock mode toggle via environment variable.
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

## 10. Supported Councils

| Council     | System    | Status     | Postcode Areas |
| ----------- | --------- | ---------- | -------------- |
| Portsmouth  | Idox      | ✅ Enabled | PO1-PO6        |
| Southampton | Northgate | ✅ Enabled | SO14-SO19      |
| Fareham     | Northgate | ⏸ Disabled | PO14-PO17      |
| Havant      | Idox      | ⏸ Disabled | PO7-PO11       |
| Gosport     | Idox      | ⏸ Disabled | PO12-PO13      |

_Enable/disable councils in `scraper/main.py` COUNCILS configuration._

## 11. Environment Variables

| Variable             | Default | Description                                      |
| -------------------- | ------- | ------------------------------------------------ |
| `SCRAPER_MOCK_MODE`  | `true`  | Use mock data (set to `false` for real scraping) |
| `SCRAPER_OUTPUT_DIR` | `data`  | Directory for output JSON files                  |
| `SCRAPER_DAYS`       | `30`    | Number of days to scrape on initial run          |

## 12. How to Run

**Backend (Scraper):**

```bash
# Install dependencies
pip install -r requirements.txt

# Run with mock data (default)
python -m scraper.main

# Run with real scraping (connects to council websites)
SCRAPER_MOCK_MODE=false python -m scraper.main

# Custom output directory
SCRAPER_OUTPUT_DIR=./custom_data python -m scraper.main
```

**Frontend (UI):**

```bash
cd frontend
npm install
npm run dev
```

**Copy data to frontend (for local dev):**

```bash
# PowerShell
Copy-Item -Path "data\*" -Destination "frontend\public\data\" -Recurse -Force

# Bash/Linux
cp -r data/* frontend/public/data/
```

## 13. Project Statistics

- **Scraper Systems:** 2 (Idox, Northgate)
- **Councils Configured:** 5 (2 enabled)
- **Frontend Components:** 8+ React components
- **Data Format:** Sharded JSON (~50kb per sector)
- **Caching Strategy:** TanStack Query (stale-while-revalidate)
- **List Performance:** Virtualized (60fps with 10k+ items)
