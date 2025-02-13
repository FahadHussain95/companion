from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete")
    survey_responses = relationship("SurveyResponse", back_populates="user", cascade="all, delete-orphan")


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    hobbies = Column(Text, nullable=True)
    dislikes = Column(Text, nullable=True)
    favorite_music = Column(Text, nullable=True)
    favorite_movies = Column(Text, nullable=True)
    personality_type = Column(String, nullable=True)
    stress_handling = Column(Text, nullable=True)
    humor_preference = Column(Text, nullable=True)
    long_term_goals = Column(Text, nullable=True)
    decision_making = Column(Text, nullable=True)
    assistant_personality = Column(String, nullable=True)
    wants_deep_conversations = Column(Boolean, default=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    user = relationship("User", back_populates="profile")


class SurveyQuestion(Base):
    __tablename__ = "survey_questions"

    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(String, nullable=False)
    category = Column(String, nullable=False)


class SurveyResponse(Base):
    __tablename__ = "survey_responses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("survey_questions.id"), nullable=False)
    response_text = Column(Text, nullable=False)

    user = relationship("User", back_populates="survey_responses")
    question = relationship("SurveyQuestion")
