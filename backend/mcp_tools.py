# FastMCP server exposing Student Survey CRUD operations as AI-callable tools.
# These tools wrap the same DB models used by the REST API in main.py.

from datetime import date as date_type
from typing import Optional, List
from sqlmodel import Session, select, or_
from fastmcp import FastMCP

from database import engine
from models import Survey

# Create the FastMCP server. The name appears in MCP Inspector.
mcp = FastMCP(name="student-survey-mcp")


def _serialize(survey: Survey) -> dict:
    """Convert a Survey DB row to a JSON-safe dict."""
    return {
        "id": survey.id,
        "first_name": survey.first_name,
        "last_name": survey.last_name,
        "street_address": survey.street_address,
        "city": survey.city,
        "state": survey.state,
        "zip": survey.zip,
        "telephone": survey.telephone,
        "email": survey.email,
        "date_of_survey": survey.date_of_survey.isoformat(),
        "liked_most": survey.liked_most,
        "interested_via": survey.interested_via,
        "recommend_likelihood": survey.recommend_likelihood,
    }


@mcp.tool()
def create_survey(
    first_name: str,
    last_name: str,
    street_address: str,
    city: str,
    state: str,
    zip: str,
    telephone: str,
    email: str,
    date_of_survey: str,
    liked_most: str,
    interested_via: str,
    recommend_likelihood: str,
) -> dict:
    """Create a new student survey record in the database.

    All fields are required. `date_of_survey` must be ISO format: YYYY-MM-DD.
    `recommend_likelihood` should be one of: 'Very Likely', 'Likely',
    'Neutral', 'Unlikely', 'Very Unlikely'.
    `interested_via` is how the student heard about the university
    (e.g. 'Friends', 'Internet', 'Television', 'Other').
    `liked_most` is what the student liked most (e.g. 'Dorms', 'Campus',
    'Atmosphere', 'Sports').

    Returns the created survey including its assigned ID.
    """
    with Session(engine) as session:
        survey = Survey(
            first_name=first_name,
            last_name=last_name,
            street_address=street_address,
            city=city,
            state=state,
            zip=zip,
            telephone=telephone,
            email=email,
            date_of_survey=date_type.fromisoformat(date_of_survey),
            liked_most=liked_most,
            interested_via=interested_via,
            recommend_likelihood=recommend_likelihood,
        )
        session.add(survey)
        session.commit()
        session.refresh(survey)
        return {"status": "success", "survey": _serialize(survey)}


@mcp.tool()
def list_surveys() -> dict:
    """List all student surveys in the database.

    Returns a list of every survey record with all fields.
    Use this when the user asks to 'show all surveys' or similar.
    """
    with Session(engine) as session:
        surveys = session.exec(select(Survey)).all()
        return {
            "status": "success",
            "count": len(surveys),
            "surveys": [_serialize(s) for s in surveys],
        }


@mcp.tool()
def get_survey_by_id(survey_id: int) -> dict:
    """Fetch a single survey by its numeric ID.

    Returns the full survey record, or an error status if not found.
    """
    with Session(engine) as session:
        survey = session.get(Survey, survey_id)
        if not survey:
            return {"status": "not_found", "survey_id": survey_id}
        return {"status": "success", "survey": _serialize(survey)}


@mcp.tool()
def search_surveys(
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    liked_most: Optional[str] = None,
    interested_via: Optional[str] = None,
    recommend_likelihood: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> dict:
    """Search for surveys matching one or more optional filters.

    All parameters are optional. String parameters do case-insensitive
    partial matching (e.g. liked_most='dorm' matches 'Dorms').
    `date_from` and `date_to` must be ISO format YYYY-MM-DD and filter
    on date_of_survey inclusively.

    Use this tool whenever the user wants to find specific surveys,
    e.g. 'Find John Doe's survey', 'Show surveys where students liked
    dorms', 'How many students are unlikely to recommend?'.
    """
    with Session(engine) as session:
        stmt = select(Survey)
        if first_name:
            stmt = stmt.where(Survey.first_name.ilike(f"%{first_name}%"))
        if last_name:
            stmt = stmt.where(Survey.last_name.ilike(f"%{last_name}%"))
        if city:
            stmt = stmt.where(Survey.city.ilike(f"%{city}%"))
        if state:
            stmt = stmt.where(Survey.state.ilike(f"%{state}%"))
        if liked_most:
            stmt = stmt.where(Survey.liked_most.ilike(f"%{liked_most}%"))
        if interested_via:
            stmt = stmt.where(Survey.interested_via.ilike(f"%{interested_via}%"))
        if recommend_likelihood:
            stmt = stmt.where(
                Survey.recommend_likelihood.ilike(f"%{recommend_likelihood}%")
            )
        if date_from:
            stmt = stmt.where(Survey.date_of_survey >= date_type.fromisoformat(date_from))
        if date_to:
            stmt = stmt.where(Survey.date_of_survey <= date_type.fromisoformat(date_to))

        surveys = session.exec(stmt).all()
        return {
            "status": "success",
            "count": len(surveys),
            "surveys": [_serialize(s) for s in surveys],
        }


@mcp.tool()
def update_survey(
    survey_id: int,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    street_address: Optional[str] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    zip: Optional[str] = None,
    telephone: Optional[str] = None,
    email: Optional[str] = None,
    date_of_survey: Optional[str] = None,
    liked_most: Optional[str] = None,
    interested_via: Optional[str] = None,
    recommend_likelihood: Optional[str] = None,
) -> dict:
    """Update one or more fields of an existing survey by ID.

    Only non-null parameters are updated; others are left unchanged.
    `date_of_survey` must be ISO format YYYY-MM-DD if provided.

    Example: to change a recommendation, pass survey_id and
    recommend_likelihood='Likely'.
    """
    with Session(engine) as session:
        survey = session.get(Survey, survey_id)
        if not survey:
            return {"status": "not_found", "survey_id": survey_id}

        updates = {
            "first_name": first_name,
            "last_name": last_name,
            "street_address": street_address,
            "city": city,
            "state": state,
            "zip": zip,
            "telephone": telephone,
            "email": email,
            "liked_most": liked_most,
            "interested_via": interested_via,
            "recommend_likelihood": recommend_likelihood,
        }
        for key, value in updates.items():
            if value is not None:
                setattr(survey, key, value)
        if date_of_survey is not None:
            survey.date_of_survey = date_type.fromisoformat(date_of_survey)

        session.add(survey)
        session.commit()
        session.refresh(survey)
        return {"status": "success", "survey": _serialize(survey)}


@mcp.tool()
def delete_survey(survey_id: int) -> dict:
    """Delete a survey by its numeric ID.

    IMPORTANT: The calling agent should confirm with the user before
    calling this tool, since deletion is irreversible.

    Returns success with the deleted survey's details, or not_found
    if no survey exists with that ID.
    """
    with Session(engine) as session:
        survey = session.get(Survey, survey_id)
        if not survey:
            return {"status": "not_found", "survey_id": survey_id}
        deleted_snapshot = _serialize(survey)
        session.delete(survey)
        session.commit()
        return {"status": "success", "deleted": deleted_snapshot}