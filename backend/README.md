# mortality_visualized

# Goal:
This project aims to provide data visualizations and fun/useful stats about diseases and general mortality.

# Running the Development Server
- Follow the base project setup using the [readme from the project root](/README.md).
- Ensure a `/backend/.env` file exists. It can (but doesn't necessarily have to) have the same contents as `.env`.
    - Register for an account with the Human Mortality Database and note your login info. Only do this if you intend to run data collection instead of using fixtures.
    - Set your HMD credentials in `/backend/.env` as `HMD_USERNAME` AND `HMD_PASSWORD`
- Do the following from the project root:
    - Ensure depended upon services are running. `python3 manager.py up`. Note that the state of the `backend` container is not relevent for the development server.
    - If you do not have an initialized database, or want to work from a clean DB state: `python3 manager.py init_db --sample_data`
- Do the following from `/backend`:
    - Install necessary packages via `pip3 install -r requirements.txt`
    - `python3 manage.py runserver`


# Project Areas
- `disease`, which is focused on facts about diseases, generally parsed by reading Wikipedia info box elements obtained by crawling index pages.
- `hmd` collects data from the Human Mortality Database and related projects, and provides a simple API for using this data.

## Data Sources:
Human Mortality Database: Annual actuary tables for approximately 20 countries
Wikipedia: Low quality data on frequency, mortality rate, symptoms, differential diagnosis, tests, etc

## Gifs

![Disease Table](/readme_assets/table.gif)

![Life Table](/readme_assets/graph.gif)
