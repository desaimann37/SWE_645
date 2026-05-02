# FastAPI REST API + MCP tool server for Student Survey data
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from typing import List

from database import get_session, create_tables
from models import Survey, SurveyCreate, SurveyRead, SurveyUpdate
from mcp_tools import mcp

# Build the MCP ASGI sub-app. FastMCP needs its lifespan to run so the
# MCP session manager initializes properly.
mcp_app = mcp.http_app(path="/")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Existing startup: create DB tables
    create_tables()
    # FastMCP lifespan for the mounted /mcp sub-app
    async with mcp_app.lifespan(app):
        yield


app = FastAPI(title="Student Survey API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the MCP server. Agent will call tools at http://<host>/mcp
app.mount("/mcp", mcp_app)


# ---------- Existing REST CRUD routes (unchanged) ----------

@app.post("/surveys/", response_model=SurveyRead)
def create_survey(survey: SurveyCreate, session: Session = Depends(get_session)):
    db_survey = Survey(**survey.model_dump())
    session.add(db_survey)
    session.commit()
    session.refresh(db_survey)
    return db_survey


@app.get("/surveys/", response_model=List[SurveyRead])
def get_surveys(session: Session = Depends(get_session)):
    return session.exec(select(Survey)).all()


@app.get("/surveys/{survey_id}", response_model=SurveyRead)
def get_survey(survey_id: int, session: Session = Depends(get_session)):
    survey = session.get(Survey, survey_id)
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")
    return survey


@app.put("/surveys/{survey_id}", response_model=SurveyRead)
def update_survey(
    survey_id: int,
    survey_update: SurveyUpdate,
    session: Session = Depends(get_session),
):
    survey = session.get(Survey, survey_id)
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")
    update_data = survey_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(survey, key, value)
    session.add(survey)
    session.commit()
    session.refresh(survey)
    return survey


@app.delete("/surveys/{survey_id}")
def delete_survey(survey_id: int, session: Session = Depends(get_session)):
    survey = session.get(Survey, survey_id)
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")
    session.delete(survey)
    session.commit()
    return {"message": "Survey deleted successfully"}