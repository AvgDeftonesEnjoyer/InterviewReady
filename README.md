# InterviewReady 🎯

InterviewReady is a comprehensive Mobile Application (React Native/Expo) powered by a Django + Django REST Framework backend. It helps software engineers prepare for technical interviews using Scripted scenarios, gamified UI, AI Practice Sandboxes, and performance tracking.

## Technology Stack 🚀

### Frontend (Mobile App)

- **Framework:** React Native (Expo)
- **Language:** TypeScript
- **State Management:** Zustand, React Query
- **Styling/Animations:** `react-native-reanimated`, Expo Linear Gradients, Custom Glassmorphism UI
- **Icons:** Lucide React Native

### Backend (REST API)

- **Framework:** Django + DRF
- **Database:** PostgreSQL
- **Authentication:** JWT (djangorestframework-simplejwt)
- **Caching/Tasks:** Redis + Celery
- **AI Integration:** OpenAI API

### Infrastructure

- Docker & Docker Compose
- Nginx (Reverse Proxy)

## Getting Started 🛠️

### Prerequisites

- Docker and Docker Compose installed on your machine.
- Node.js and npm (for frontend local development/running).
- Python 3.12 (optional, if running backend locally outside Docker).

### Running with Docker (Recommended)

You can spin up the entire backend stack (Django, Postgres, Redis, Celery) and the frontend bundler in one go.

1. Clone the repository.
2. Ensure you have the `.env` files set up (see `.env.example`).
3. Run the following command from the root directory:
   ```bash
   docker-compose up --build
   ```

Note: If you are running the frontend via Expo on a physical device, make sure your phone and development machine are on the same Wi-Fi network, and update `API_URL` in `frontend/src/api/client.ts` to point to your machine's local IP address instead of `127.0.0.1`.

## Features 🌟

- **Gamified Dashboard:** Track your daily streaks, XP, and weekly standing.
- **Scripted Interviews:** Practice heavily vetted architectural and algorithm questions.
- **AI Practice Sandbox:** Talk directly to a simulated HR Bot that evaluates your answers with real-time feedback and dynamic scoring metrics.
- **Progress Tracking:** Follow your growth through immersive heatmaps and weekly bar charts.
- **PRO Subscription tier:** Unlock unlimited AI evaluations and harder scenarios.

## Project Structure 📁

```
InterviewReady/
├── backend/          # Django project root
│   ├── core/         # Core settings and configurations
│   ├── users/        # Auth, JWT, and User models
│   ├── learning/     # Questions, Topics, Options logic
│   ├── interview/    # Session handling (Scripted & AI)
│   ├── progress/     # XP, Streaks, Gamification
│   └── subscriptions/# Stripe/Apple Pay webhooks and models
├── frontend/         # Expo React Native root
│   ├── src/
│   │   ├── api/      # Axios config and fetchers
│   │   ├── components# Reusable UI elements (Glassmorphism, Badges)
│   │   ├── features/ # Feature-based modules (auth, learning, ai, etc.)
│   │   ├── navigation# React Navigation setup and Custom Tab Bar
│   │   ├── store/    # Zustand global state
│   │   ├── theme/    # Design tokens (Colors, Typography)
│   │   └── utils/    # Storage and helpers
├── docker/           # Dockerfiles (backend, frontend)
└── docker-compose.yml
```
