from typing import List, Dict

from fastapi import APIRouter, Depends
from starlette import status

import services.audit_services as audit
import services.evaluation_services as eval_serv
import services.security_services as sec_serv
from domain.enums import Language
from domain.evaluations import EvaluationResult
from domain.users import User
from rest_api.dtos import CreateEvaluationRequest, UpdateEvaluationInfoRequest, CreateQuestionRequest, \
    UpdateQuestionRequest, DeleteQuestionRequest

evaluation_api = APIRouter()


@evaluation_api.post('/create_evaluation', tags=['Evaluations'], status_code=status.HTTP_201_CREATED)
async def create_evaluation(create_evaluation_request: CreateEvaluationRequest,
                            user: User = Depends(sec_serv.get_current_user)) -> str:
    """Creates a new evaluation"""
    try:
        return eval_serv.create_evaluation(create_evaluation_request, user)
    finally:
        audit.audit_entity(user.id, 'created_evaluation', create_evaluation_request.to_audit())


@evaluation_api.patch('/update_evaluation_info', tags=['Evaluations'], status_code=status.HTTP_200_OK)
async def update_evaluation_info(update_evaluation_request: UpdateEvaluationInfoRequest,
                                 user: User = Depends(sec_serv.get_current_user)) -> bool:
    """Updates an evaluation information"""
    try:
        eval_serv.update_evaluation_info(update_evaluation_request, user)
        return True
    finally:
        audit.audit_entity(user.id, 'updated_evaluation', update_evaluation_request.to_audit())


@evaluation_api.get('/evaluations_by_project', tags=['Evaluations'], status_code=status.HTTP_200_OK)
async def get_evaluations_by_project(project_id: str,
                                     user: User = Depends(sec_serv.get_current_user)) -> List:
    """Return all the evaluations information from a project"""
    return eval_serv.get_evaluations_by_project(project_id, user)


@evaluation_api.get('/evaluation', tags=['Evaluations'], status_code=status.HTTP_200_OK)
async def get_evaluation(project_id: str, evaluation_id,
                         user: User = Depends(sec_serv.get_current_user)) -> Dict:
    """Return the complete evaluations information"""
    return eval_serv.get_evaluation(project_id, evaluation_id, user)


@evaluation_api.post('/create_question', tags=['Evaluations'], status_code=status.HTTP_201_CREATED)
async def create_question(create_question_request: CreateQuestionRequest,
                          user: User = Depends(sec_serv.get_current_user)) -> str:
    """Creates a new question in the evaluation"""
    try:
        return eval_serv.create_question(create_question_request, user)
    finally:
        audit.audit_entity(user.id, 'created_question', create_question_request.to_audit())


@evaluation_api.patch('/update_question', tags=['Evaluations'], status_code=status.HTTP_200_OK)
async def update_question(update_question_request: UpdateQuestionRequest,
                          user: User = Depends(sec_serv.get_current_user)) -> bool:
    """Updates a question in the evaluation"""
    try:
        eval_serv.update_question(update_question_request, user)
        return True
    finally:
        audit.audit_entity(user.id, 'updated_question', update_question_request.to_audit())


@evaluation_api.delete('/delete_question', tags=['Evaluations'], status_code=status.HTTP_200_OK)
async def delete_question(delete_question_request: DeleteQuestionRequest,
                          user: User = Depends(sec_serv.get_current_user)) -> bool:
    """Deletes a question in the evaluation"""
    try:
        eval_serv.delete_question(delete_question_request, user)
        return True
    finally:
        audit.audit_entity(user.id, 'deleted_question', delete_question_request.to_audit())


@evaluation_api.get('/generate_question', tags=['Evaluations'], status_code=status.HTTP_200_OK)
async def generate_question(topic: str, language: Language,
                            user: User = Depends(sec_serv.get_current_user)) -> str:
    """Generates a question given a topic to ask"""
    try:
        return eval_serv.generate_question(topic, language)
    finally:
        audit.audit_entity(user.id, 'generated_question', {'topic': topic})


@evaluation_api.get('/evaluate_answer', tags=['Evaluations'], status_code=status.HTTP_200_OK)
async def evaluate_answer(question: str, answer: str,
                          user: User = Depends(sec_serv.get_current_user)) -> EvaluationResult:
    """Evaluates from 1 to 5 the response given by a candidate to a question"""
    try:
        return eval_serv.evaluate_answer(question, answer)
    finally:
        audit.audit_entity(user.id, 'evaluated_answer', {'question': question, 'answer': answer})
