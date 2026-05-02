# SQLModel models defining the Student Survey database schema
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import date

class SurveyBase(SQLModel):
    first_name: str
    last_name: str
    street_address: str
    city: str
    state: str
    zip: str
    telephone: str
    email: str
    date_of_survey: date
    liked_most: str
    interested_via: str
    recommend_likelihood: str

class Survey(SurveyBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

class SurveyCreate(SurveyBase):
    pass

class SurveyRead(SurveyBase):
    id: int

class SurveyUpdate(SQLModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    street_address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    date_of_survey: Optional[date] = None
    liked_most: Optional[str] = None
    interested_via: Optional[str] = None
    recommend_likelihood: Optional[str] = None