# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Structure

Lecturia is a lecture generation system with two main components:

* **API (Python/FastAPI)**: Backend service that generates interactive lectures from topics using LLM chains
* **Web (Next.js/React)**: Frontend that displays and plays generated lectures

## Common Commands

### API Development

```bash
cd api
cp .env.example .env  # Fill in ANTHROPIC_API_KEY, GOOGLE_API_KEY, BRAVE_API_KEY
docker compose up -d  # Start local development with emulators
docker compose exec lecturia python examples/seeder.py  # Seed example data
```

### Web Development

```bash
cd web
cp .env.example .env
pnpm install          # Install dependencies
pnpm dev              # Start development server on localhost:3000
pnpm build            # Build for production
pnpm lint             # Run ESLint
npx tsc --noEmit      # Run TypeScript type checking
```

### Testing

The project uses example scripts for testing individual components:
```bash
cd api
python examples/pipeline_test.py    # Test full pipeline
python examples/tts_test.py         # Test text-to-speech
python examples/event_test.py       # Test event extraction
```

## Architecture Overview

### Core Workflow

1. **Slide Generation**: Create HTML slides from topics using LangChain
2. **Script Creation**: Convert slides to speaker scripts with character assignments
3. **Audio Generation**: Generate TTS audio for each slide
4. **Event Extraction**: Extract character animation and transition timeline events from audio and slides
5. **Lecture Assembly**: Integrate all elements into playable lecture data

### Key Components

**API Core (`api/src/lecturia/`)**:
* `models.py`: Data model definitions (MovieConfig, Event, Character, Manifest)
* `router.py`: REST API endpoints for lecture management
* `server.py`: FastAPI application with CORS configuration
* `chains/`: LangChain components for content generation
* `cloud_pipeline/workflow.py`: Main workflow for lecture generation
* `storage.py`: Google Cloud Storage integration

**Chain Modules (`api/src/lecturia/chains/`)**:
* `slide_maker.py`: Generate HTML slides from topics
* `slide_to_script.py`: Convert slides to speaker scripts
* `tts.py`: Text-to-speech audio generation with multiple voice types
* `event_extractor.py`: Extract timeline events from audio and slides
* `sprite_generator.py`: Character sprite management
* `quiz_generator.py`: Generate interactive quizzes

**Web Components (`web/`)**:
* `app/lectures/[id]/page.tsx`: Lecture playback page
* `components/Player.tsx`: Main lecture playback component
* `hooks/useTimeline.ts`: Timeline state management hook

### Data Flow

1. User submits `MovieConfig` (topic and character settings)
2. System generates: Slides → Scripts → Audio → Events → Final Manifest
3. All assets stored in Google Cloud Storage
4. Web client fetches manifest and performs synchronized playback

### Core Models

* `MovieConfig`: Input configuration with topic and character settings
* `Event`: Timeline events for animations and transitions
* `Character`: Speaker definitions with voice and sprite information
* `Manifest`: Playback metadata for lectures

## Development Notes

* Asynchronous lecture generation uses Google Cloud Tasks
* Audio processing includes silence removal and segment timing adjustments
* Character sprites are embedded as base64 in manifests
* Slide transitions are controlled by audio length + delay settings
* Local development uses emulators for GCS, Firestore, and Cloud Tasks
* Examples in `api/examples/` demonstrate individual component usage