import uuid
from typing import Dict, List

from fastapi import HTTPException
from starlette import status

import infra.language_model_manager as model
import infra.repositories.evaluation_repository as eval_repo
import infra.repositories.project_repository as proj_repo
from constants import PROJECT_DO_NOT_EXIST, EVALUATION_DO_NOT_EXIST, USER_NOT_IN_PROJECT, QUESTION_DO_NOT_EXIST
from domain.enums import Language
from domain.evaluations import EvaluationResult, Evaluation, Project, Question
from domain.users import User
from rest_api.dtos import CreateEvaluationRequest, UpdateEvaluationInfoRequest, CreateQuestionRequest, \
    UpdateQuestionRequest, DeleteQuestionRequest


def get_project(project_id: str) -> Project:
    project = proj_repo.find_project_by_id(project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=PROJECT_DO_NOT_EXIST)

    return project


def create_evaluation(create_evaluation_request: CreateEvaluationRequest, user: User) -> str:
    project = get_project(create_evaluation_request.project_id)

    if user.id not in project.users:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=USER_NOT_IN_PROJECT)

    new_evaluation = Evaluation(
        id=str(uuid.uuid4()),
        project_id=project.id,
        name=create_evaluation_request.evaluation_name,
        language=create_evaluation_request.language,
        description=create_evaluation_request.evaluation_description
    )
    eval_repo.insert_evaluation(new_evaluation)

    return new_evaluation.id


def update_evaluation_info(update_evaluation_request: UpdateEvaluationInfoRequest, user: User):
    project = get_project(update_evaluation_request.project_id)

    if user.id not in project.users:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=USER_NOT_IN_PROJECT)

    evaluation = eval_repo.find_evaluation_by_id(update_evaluation_request.evaluation_id)
    if not evaluation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=EVALUATION_DO_NOT_EXIST)

    updated_evaluation = Evaluation(
        id=evaluation.id,
        project_id=project.id,
        name=update_evaluation_request.evaluation_name,
        description=update_evaluation_request.evaluation_description,
        language=update_evaluation_request.language,
        questions=evaluation.questions
    )

    eval_repo.update_evaluation(updated_evaluation)


def get_evaluation(project_id: str, evaluation_id: str, user: User) -> Dict:
    project = get_project(project_id)

    if user.id not in project.users:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=USER_NOT_IN_PROJECT)

    evaluation = eval_repo.find_evaluation_by_id(evaluation_id)
    if not evaluation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=EVALUATION_DO_NOT_EXIST)

    return evaluation.to_api_response()


def get_evaluations_by_project(project_id, user) -> List:
    project = get_project(project_id)

    if user.id not in project.users:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=USER_NOT_IN_PROJECT)

    evaluations_list = []
    for evaluation in eval_repo.find_evaluations_by_project_id(project_id):
        evaluations_list.append(evaluation.to_simple_api_response())

    return evaluations_list


def create_question(create_question_request: CreateQuestionRequest, user) -> str:
    project = get_project(create_question_request.project_id)

    if user.id not in project.users:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=USER_NOT_IN_PROJECT)

    evaluation = eval_repo.find_evaluation_by_id(create_question_request.evaluation_id)
    if not evaluation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=EVALUATION_DO_NOT_EXIST)

    new_question = Question(
        id=str(uuid.uuid4()),
        text=create_question_request.text,
        mandatory=create_question_request.mandatory,
        time_to_respond=create_question_request.time_to_respond,
    )

    if not evaluation.questions:
        evaluation.questions = []
    evaluation.questions.append(new_question)
    eval_repo.update_evaluation(evaluation)

    return new_question.id


def update_question(update_question_request: UpdateQuestionRequest, user):
    project = get_project(update_question_request.project_id)

    if user.id not in project.users:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=USER_NOT_IN_PROJECT)

    evaluation = eval_repo.find_evaluation_by_id(update_question_request.evaluation_id)
    if not evaluation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=EVALUATION_DO_NOT_EXIST)

    current_question = None
    for q in evaluation.questions:
        if q.id == update_question_request.question_id:
            current_question = q

    if not current_question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=QUESTION_DO_NOT_EXIST)

    current_question.text = update_question_request.text
    current_question.mandatory = update_question_request.mandatory
    current_question.time_to_respond = update_question_request.time_to_respond

    eval_repo.update_evaluation(evaluation)


def delete_question(delete_question_request: DeleteQuestionRequest, user):
    project = get_project(delete_question_request.project_id)

    if user.id not in project.users:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=USER_NOT_IN_PROJECT)

    evaluation = eval_repo.find_evaluation_by_id(delete_question_request.evaluation_id)
    if not evaluation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=EVALUATION_DO_NOT_EXIST)

    question_to_delete = None
    for q in evaluation.questions:
        if q.id == delete_question_request.question_id:
            question_to_delete = q

    if not question_to_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=QUESTION_DO_NOT_EXIST)

    evaluation.questions.remove(question_to_delete)
    eval_repo.update_evaluation(evaluation)


def evaluate_answer(question: str, answer: str) -> EvaluationResult:
    result = model.evaluate_answer(question, answer)
    # TODO: Store the result in database
    return result


def generate_question(topic: str, language: Language) -> Dict:
    return {'question': model.create_question(topic, language)}
