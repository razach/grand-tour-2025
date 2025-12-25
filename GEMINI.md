# Gemini Workspace Context for YearEnd Trip

## Project Overview
This project contains the planning documents and website source code for the "Grand Tour: Bourbon & Bluegrass" road trip (Dec 2025).
The core artifact is a static website hosted on GitHub Pages.

## Workflow: Single Source of Truth
The website content is generated programmatically from the markdown plan.
*   **Source**: `road_trip_plan.md` (Edit this file).
*   **Generator**: `src/build_site.py` (Run this script).
*   **Output**: `docs/index.html` (Do not edit manually).

## Building and Running
1.  **Install Dependencies:**
    ```bash
    ./.venv/bin/pip install -r requirements.txt
    ```
2.  **Generate Website:**
    ```bash
    ./.venv/bin/python src/build_site.py
    ```

## Project Structure
*   `road_trip_plan.md`: Master itinerary and content source.
*   `docs/`: Public website (HTML/CSS/JS).
*   `src/`:
    *   `build_site.py`: Generator script (Markdown -> HTML).
    *   `templates/`: Jinja2 HTML templates.
*   `data/`: Raw data storage.
*   `notebooks/`: Experimentation.
