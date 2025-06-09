# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Structure

Lecturia is a lecture generation and playback system with two main components:

- **API (Python/FastAPI)**: Backend service for generating interactive lectures from topics using LLM chains
- **Web (Next.js/React)**: Frontend for viewing and playing generated lectures

## Common Commands

### API Development
```bash
cd api
uv sync                    # Install dependencies
uv run playwright install  # Install browser dependencies for slide generation
uv run python -m lecturia.server  # Run API server
```

### Web Development
```bash
cd web
pnpm dev                   # Run development server on localhost:3000
pnpm build                # Build for production
pnpm lint                 # Run linting
```

## Architecture Overview

### Core Workflow
1. **Slide Generation**: Uses LangChain to generate HTML slides from topics
2. **Script Creation**: Converts slides to speaker scripts with character assignments
3. **Audio Generation**: Creates TTS audio for each slide
4. **Event Extraction**: Generates timeline events for character animations and slide transitions
5. **Lecture Assembly**: Combines all components into a playable lecture

### Key Components

**API Core (`api/src/lecturia/`)**:
- `models.py`: Core data models (MovieConfig, Event, Character, Manifest)
- `router.py`: REST API endpoints for lecture management
- `server.py`: FastAPI application setup with CORS
- `chains/`: LangChain components for content generation
- `cloud_pipeline/workflow.py`: Main lecture generation workflow
- `storage.py`: Google Cloud Storage integration

**Chain Modules (`api/src/lecturia/chains/`)**:
- `slide_maker.py`: Generates HTML slides from topics
- `slide_to_script.py`: Converts slides to speaker scripts
- `tts.py`: Text-to-speech generation with multiple voice types
- `event_extractor.py`: Creates timeline events from audio and slides
- `sprite_generator.py`: Character sprite management

**Web Components (`web/`)**:
- `app/lectures/[id]/page.tsx`: Lecture player page
- `components/Player.tsx`: Main lecture playback component
- `hooks/useTimeline.ts`: Timeline state management

### Data Flow
1. User submits `MovieConfig` with topic and character settings
2. System generates slides → scripts → audio → events → final manifest
3. All assets stored in Google Cloud Storage
4. Web client fetches manifest and plays synchronized content

### Key Models
- `MovieConfig`: Input configuration (topic, characters, settings)
- `Event`: Timeline events for animations and transitions
- `Character`: Speaker definitions with voice types and sprites
- `Manifest`: Final lecture metadata for playback

## Development Notes

- The system uses Google Cloud Tasks for async lecture generation
- Audio processing includes silence removal and segment timing
- Character sprites are embedded as base64 in manifests
- Slide transitions are timed based on audio duration + configurable delays