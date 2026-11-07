# BeaconKeep
A backend-focused API monitoring platform designed to track service availability, measure response times, detect outages, and manage incidents.

## The eventual flow is:

Create Monitor → schedule checks → make HTTP requests → save CheckResults → open or resolve Incidents → show history and notify users

## Libraries used
|Library/tool|Purpose|
|------------|-------|
|FastAPI|API Framework|
|SQLAlchemy| ORM and db toolkit|
|psycopg| PostgreSQLdriver used by SQLalchemy|
|Pydantic| Request Validation and response schemas|
|Alembic| Versioned database schema migrations|
|pytest| Automated api, schema, and db testing|
|HTTPX | HTTP client used by FastAPI (Dependency)|
|python-dotenv| `.env` config loader|

## Supporting Infrastructure
|Tool|Purpose|
|----|-------|
|PostGreSQL 17| Relational db|
|Docker compose| configures local postgresql container and persistant storage|
|python 3.11| Idunno what its for :/|
