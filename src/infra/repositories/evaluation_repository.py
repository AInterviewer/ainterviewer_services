from typing import Dict, List

from domain import utils
from domain.enums import Language
from domain.evaluations import Evaluation, Question
from infra.repositories.general_repository import AINTERVIEWER_CLIENT

EVALUATIONS_COLLECTION = AINTERVIEWER_CLIENT.evaluations


def insert_evaluation(evaluation: Evaluation):
    EVALUATIONS_COLLECTION.insert_one(evaluation.to_dict())


def find_evaluation_by_id(evaluation_id: str):
    evaluation_data = EVALUATIONS_COLLECTION.find_one({'_id': evaluation_id})
    if evaluation_data:
        return deserialize_evaluation(evaluation_data)


def find_evaluations_by_project_id(project_id: str) -> List[Evaluation]:
    evaluations = []
    evaluation_list = EVALUATIONS_COLLECTION.find({'project_id': project_id})
    for evaluation_data in evaluation_list:
        evaluations.append(deserialize_evaluation(evaluation_data))

    return evaluations


def update_evaluation(evaluation: Evaluation):
    EVALUATIONS_COLLECTION.update_one(
        {'_id': evaluation.id},
        {'$set': {
            'name': evaluation.name,
            'description': evaluation.description,
            'language': evaluation.language.name,
            'questions': [question.to_dict() for question in
                          evaluation.questions] if evaluation.questions else None
        }}
    )


def deserialize_evaluation(evaluation_data: Dict) -> Evaluation:
    return Evaluation(
        id=evaluation_data.get('_id'),
        project_id=evaluation_data.get('project_id'),
        name=evaluation_data.get('name'),
        description=evaluation_data.get('description'),
        language=Language[evaluation_data.get('language')],
        questions=deserialize_questions(evaluation_data.get('questions')) if evaluation_data.get(
            'questions') else None
    )


def deserialize_questions(questions_list_data: List):
    questions = []
    for question_data in questions_list_data:
        questions.append(
            Question(
                id=question_data.get('_id'),
                text=question_data.get('text'),
                mandatory=question_data.get('mandatory'),
                time_to_respond=utils.get_time_from_str(question_data.get('time_to_respond')),
            )
        )

    return questions
