# StadiumIQ

A GenAI-powered assistant for fan navigation, crowd safety, transport, multilingual support, staff coordination, and sustainability tracking at FIFA World Cup 2026 stadiums.

Built for Prompt Wars Challenge 4 — Smart Stadiums & Tournament Operations.

## What it does

- **Navigation** — GPT-4o powered step-by-step directions between stadium zones, in five languages.
- **Crowd safety** — real-time density reporting and automatic classification (low/moderate/high/critical), with dashboard alerts for zones that need attention.
- **Transport** — recommends the lowest-emission way to reach the stadium based on distance, with estimated CO2e per option.
- **Multilingual support** — on-demand translation into English, Hindi, Arabic, Spanish, and French.
- **Staff coordination** — a task board for volunteers to create, filter, and update operational tasks by zone.
- **Sustainability tracking** — logs electricity, water, waste, and transport usage and converts it into estimated CO2e, using published emission factors.
- **Live operational intelligence** — a control-room dashboard (`/insights`) that streams crowd risk, open tasks, and sustainability totals in real time via Server-Sent Events, plus an AI-generated plain-language briefing telling staff what to prioritize right now.

## Stack

Flask, SQLAlchemy, SQLite, Flask-Login, Flask-Caching, Flask-Talisman (security headers/CSP), Flask-Limiter (rate limiting), OpenAI GPT-4o, pytest.

## Architecture

The app follows a layered structure so each piece can be tested and reasoned about independently:

```
app/
  blueprints/   route handlers only — no business logic
  services/     business logic (crowd classification, emissions math, AI calls)
  models/       SQLAlchemy models
  utils/        sanitization and validation helpers
  templates/    Jinja2 templates, built with semantic HTML and ARIA landmarks
  static/       CSS and vanilla JS (no build step required)
```

Routes call services, services touch the database and the AI layer. This keeps `app/blueprints/*.py` thin and makes the business logic unit-testable without spinning up HTTP requests.

## Setup

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env           # then fill in OPENAI_API_KEY
flask --app run seed-demo-data # optional: creates a demo admin + sample data
python run.py
```

Visit `http://localhost:5000`.

Demo admin (if you ran the seed command): `admin@stadiumiq.demo` / `ChangeMe123!`

## Testing

```bash
pytest
```

183 tests, 95% coverage. Covers model behavior, service business logic, input sanitization, authentication, role-based access control (fan / volunteer / admin) for every route, and the live operational intelligence stream.

Linting runs via `ruff check .` and type checking via `mypy app --ignore-missing-imports`, both clean as of this submission.

## Security

- Bleach-based sanitization on every free-text input field before it touches the database.
- Flask-Talisman applies a Content-Security-Policy and forces HTTPS/HSTS in production.
- Passwords hashed with Werkzeug's `generate_password_hash` (never stored in plaintext).
- Role checks (`fan` / `volunteer` / `admin`) enforced server-side on every sensitive route, not just hidden in the UI.
- Rate limiting on auth endpoints to slow down credential stuffing attempts.

## Accessibility

- Skip-to-content link, semantic landmarks (`header`, `main`, `footer`, `nav`).
- All form inputs have associated `<label>` elements.
- Density and status are shown as text, not color alone.
- Visible focus outlines on every interactive element for keyboard navigation.
- Live regions (`aria-live="polite"`) on dynamic result areas (translation output, navigation guidance, form feedback).

## Sustainability methodology

Emission factors (kg CO2e per unit) used for estimates:

| Category | Factor | Basis |
|---|---|---|
| Electricity | 0.475 kg/kWh | Grid average |
| Water | 0.000344 kg/liter | Treatment + supply |
| Waste | 0.457 kg/kg | Landfill waste |
| Transport | 0.171 kg/passenger-km | Shuttle bus average |

These are estimates for demonstration, not an audited carbon accounting standard.

## How this meets the challenge brief

The Challenge 4 brief asks for a GenAI solution that improves *navigation, crowd management, accessibility, transportation, sustainability, multilingual assistance, operational intelligence, and real-time decision support* for FIFA World Cup 2026 stadiums. Here's exactly where each of those is implemented:

| Brief requirement | Where it lives |
|---|---|
| Navigation | `/navigation` — GPT-4o directions between stadium zones (`app/services/ai_service.py::get_navigation_guidance`) |
| Crowd management | `/crowd` — density classification and zone alerts (`app/services/crowd_service.py`) |
| Accessibility | Site-wide — WCAG-conscious templates, skip links, ARIA live regions, keyboard focus states (`app/templates/base.html`, `app/static/css/main.css`) |
| Transportation | `/transport` — emission-ranked recommendations (`app/services/transport_service.py`) |
| Sustainability | `/sustainability` — CO2e tracking across electricity, water, waste, transport (`app/services/sustainability_service.py`) |
| Multilingual assistance | `/multilingual` — on-demand GPT-4o translation, 5 languages (`app/services/ai_service.py::get_translation`) |
| Operational intelligence | `/insights` — cross-domain snapshot combining crowd, tasks, and sustainability into one picture (`app/services/insights_service.py::build_snapshot`) |
| Real-time decision support | `/insights` — live Server-Sent Events stream plus an AI-generated prioritization briefing (`app/blueprints/insights.py::stream`, `insights_service.py::generate_briefing`) |

## Running with Docker

```bash
docker build -t stadiumiq .
docker run -p 8000:8000 --env-file .env stadiumiq
```

Visit `http://localhost:8000`.

## Type checking

```bash
mypy app --ignore-missing-imports
```

Models use SQLAlchemy 2.0's typed declarative style (`Mapped[...]` / `mapped_column`), which is fully type-checked, not just annotated.

## Deployment

Configured for Render via `render.yaml`. Set `OPENAI_API_KEY` as a secret environment variable in the Render dashboard after the first deploy. A `Dockerfile` is also included for containerized deployment on any platform that supports it.


