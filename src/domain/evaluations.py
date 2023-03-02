from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

from constants import TIME_FORMAT
from domain.enums import Language


@dataclass
class Project:
    id: str
    name: str
    description: str
    users: Optional[List[str]] = None

    def to_dict(self) -> dict:
        return {
            '_id': self.id,
            'name': self.name,
            'description': self.description,
            'users': self.users
        }

    def to_api_response(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }


@dataclass
class Question:
    id: str
    text: str
    mandatory: bool
    time_to_respond: datetime.time

    def to_dict(self) -> dict:
        return {
            '_id': self.id,
            'text': self.text,
            'mandatory': self.mandatory,
            'time_to_respond': self.time_to_respond.strftime(TIME_FORMAT)
        }

    def to_api_response(self):
        return {
            'id': self.id,
            'text': self.text,
            'mandatory': self.mandatory,
            'time_to_respond': self.time_to_respond.strftime(TIME_FORMAT)
        }


@dataclass
class Evaluation:
    id: str
    project_id: str
    name: str
    description: str
    language: Language
    questions: Optional[List[Question]] = None

    def to_dict(self) -> dict:
        return {
            '_id': self.id,
            'project_id': self.project_id,
            'name': self.name,
            'description': self.description,
            'language': self.language.name,
            'questions': [question.to_dict() for question in self.questions] if self.questions else None
        }

    def to_api_response(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'name': self.name,
            'description': self.description,
            'language': self.language.name,
            'questions': [question.to_api_response() for question in
                          self.questions] if self.questions else None
        }

    def to_simple_api_response(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'name': self.name,
            'language': self.language.name,
            'description': self.description
        }


@dataclass
class EvaluationResult:
    question: str
    answer: str
    grade: int
    explanation: str
