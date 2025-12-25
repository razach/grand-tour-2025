# The Grand Tour: Bourbon & Bluegrass 2025

This repository contains the itinerary and website for the Zacharia Brothers' Year-End Road Trip.

## 🚀 Workflow: Single Source of Truth

The website (`docs/index.html`) is **automatically generated** from the markdown plan (`road_trip_plan.md`). You should not edit the HTML manually.

### How to Update
1.  **Edit the Plan**: Open `road_trip_plan.md` and make your changes.
    *   **Itinerary**: Use the `### Day X` and `* **Time**: Title` format.
    *   **Shortlists**: Update the `## 🏨 Hotels`, `## 🍔 Food & Drink Shortlist`, or `## 🎒 Packing List` sections.
2.  **Generate the Site**:
    ```bash
    python src/build_site.py
    ```
    *This script parses the markdown and updates `docs/index.html`.*
3.  **Verify**: Open `docs/index.html` in your browser to check the changes.
4.  **Deploy**:
    ```bash
    git add .
    git commit -m "Update plan"
    git push
    ```
    *The site is hosted on GitHub Pages.*

## 📂 Project Structure
*   `road_trip_plan.md`: The master itinerary document (Source of Truth).
*   `docs/`: The public website folder (served by GitHub Pages).
    *   `index.html`: The generated homepage.
    *   `css/`: Styles.
    *   `js/`: Interactive map logic.
*   `src/`: Build tools.
    *   `build_site.py`: The generator script.
    *   `templates/`: HTML templates (Jinja2).

## 🛠 Setup (If running on a new machine)
1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
