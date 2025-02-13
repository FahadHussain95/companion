from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from http import HTTPStatus

from constants import (
    USERNAME_EXISTS,
    USER_SUCCESSFULLY_CREATED,
    INVALID_CREDS,
    PROFILE_EXISTS,
    PROFILE_NOT_FOUND,
    ACCESS_TOKEN_EXPIRY,
    USER_NOT_FOUND,
    RESPONSE_SAVED,
    QUESTION_CREATED
)
from utils import get_authenticated_user
from database import engine, Base, get_db
from models import (
    User,
    UserProfile,
    SurveyQuestion,
    SurveyResponse
)
from auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user
)
from pydantic import BaseModel
from typing import Optional, List
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm

app = FastAPI()

# Create tables
Base.metadata.create_all(bind=engine)


# Authentication models
class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


# User Profile models
class UserProfileCreate(BaseModel):
    name: str
    description: Optional[str] = None
    hobbies: Optional[str] = None
    dislikes: Optional[str] = None
    favorite_music: Optional[str] = None
    favorite_movies: Optional[str] = None
    personality_type: Optional[str] = None
    stress_handling: Optional[str] = None
    humor_preference: Optional[str] = None
    long_term_goals: Optional[str] = None
    decision_making: Optional[str] = None
    assistant_personality: Optional[str] = None
    wants_deep_conversations: Optional[bool] = True


class SurveyQuestionCreate(BaseModel):
    question_text: str
    category: str


class BulkSurveyQuestionsCreate(BaseModel):
    questions: List[SurveyQuestionCreate]


class SurveyAnswer(BaseModel):
    question_id: int
    response_text: str


@app.post("/register/")
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=USERNAME_EXISTS)

    hashed_pw = hash_password(user_data.password)
    new_user = User(username=user_data.username, email=user_data.email, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": USER_SUCCESSFULLY_CREATED}


@app.post("/token/", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail=INVALID_CREDS)

    access_token = create_access_token(data={"sub": user.username}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRY))
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/user/")
def get_me(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == current_user["sub"]).first()
    if not user:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail=USER_NOT_FOUND)
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email
    }


@app.post("/users/profile/")
def create_user_profile(
    profile_data: UserProfileCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user = get_authenticated_user(db, current_user)

    if db.query(UserProfile).filter(UserProfile.user_id == user.id).first():
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=PROFILE_EXISTS)

    new_profile = UserProfile(user_id=user.id, **profile_data.dict())
    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)
    return new_profile


@app.get("/users/profile/")
def get_user_profile(
        db: Session = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    print("here:")
    user = get_authenticated_user(db, current_user)
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    if not profile:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=PROFILE_NOT_FOUND)

    return profile


@app.get("/survey/questions/")
def get_survey_questions(db: Session = Depends(get_db)):
    questions = db.query(SurveyQuestion).all()
    return questions


@app.post("/survey/questions/bulk/")
def create_bulk_survey_questions(
    bulk_data: BulkSurveyQuestionsCreate,
    db: Session = Depends(get_db),
):
    new_questions = [
        SurveyQuestion(question_text=question.question_text, category=question.category)
        for question in bulk_data.questions
    ]

    db.add_all(new_questions)
    db.commit()

    return {"message": QUESTION_CREATED, "count": len(new_questions)}


@app.post("/survey/answers/")
def submit_survey_answer(
        answers: List[SurveyAnswer],
        db: Session = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    user = get_authenticated_user(db, current_user)

    for answer in answers:
        new_response = SurveyResponse(
            user_id=user.id,
            question_id=answer.question_id,
            response_text=answer.response_text
        )
        db.add(new_response)

    db.commit()
    return {"message": RESPONSE_SAVED}
