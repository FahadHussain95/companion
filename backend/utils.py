from fastapi import HTTPException
from sqlalchemy.orm import Session

from constants import USER_NOT_FOUND
from models import User, SurveyResponse, SurveyQuestion, UserProfile
from http import HTTPStatus


def get_authenticated_user(db: Session, current_user: dict):
    """
    Fetch authenticated user from the database.

    Raises:
        HTTPException: 404 if user is not found.

    Returns:
        User: Authenticated user object.
    """
    user = db.query(User).filter(User.username == current_user["sub"]).first()
    if not user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=USER_NOT_FOUND)
    return user


def convert_to_boolean(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ["yes", "true", "1"]
    return False


def update_user_profile(db: Session, user_id: int):
    """
    Process survey responses and update the user's profile.
    """
    responses = (
        db.query(SurveyResponse)
        .join(SurveyQuestion, SurveyResponse.question_id == SurveyQuestion.id)
        .filter(SurveyResponse.user_id == user_id)
        .all()
    )

    if not responses:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="No responses found.")

    category_mapping = {
        "general_information": ["name", "description"],
        "hobbies_interests": ["hobbies", "favorite_music", "favorite_movies"],
        "dislikes_personality": ["dislikes", "personality_type", "wants_deep_conversations"],
        "stress_emotions": ["stress_handling"],
        "humor_communication": ["humor_preference"],
        "life_goals_decision_making": ["long_term_goals", "decision_making"],
        "ai_assistant_personality": ["assistant_personality"],
        "deep_conversations_engagement": ["wants_deep_conversations"]
    }

    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not profile:
        profile = UserProfile(user_id=user_id)
        db.add(profile)

    for response in responses:
        question = response.question
        category = question.category
        answer = response.response_text

        if category in category_mapping:
            profile_fields = category_mapping[category]
            for field in profile_fields:
                if field == "wants_deep_conversations":
                    setattr(profile, field, convert_to_boolean(answer))
                else:
                    setattr(profile, field, answer)

    db.commit()
    db.refresh(profile)
    return profile
