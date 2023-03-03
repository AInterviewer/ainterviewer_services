import logging
import re

import openai

from constants import MODEL, ANSWERS, API_KEY, QUESTION_EN, QUESTION_ES, MAX_TOKENS, MODEL_TEMPERATURE
from domain.enums import Language
from domain.evaluations import EvaluationResult
from domain.exeptions import AIModelException


def execute_prompt(prompt: str) -> str:
    # TODO: Check how to send maximum 20 requests per minute
    openai.api_key = API_KEY
    completion = openai.ChatCompletion.create(
        model=MODEL,
        messages=[
            {'role': 'user',
             'content': prompt},
        ],
        max_tokens=MAX_TOKENS,
        temperature=MODEL_TEMPERATURE
    )
    return completion.choices[0].message.content


def replace_key_in_message(message: str, key: str, value: str):
    return message.replace(key, value)


def create_question(topic: str, language: Language) -> str:
    question = QUESTION_EN if language == Language.ENGLISH else QUESTION_ES
    message = replace_key_in_message(question, '<topic>', topic)
    response = execute_prompt(message)
    return response.replace('\n', '')


def evaluate_answer(question: str, answer: str) -> EvaluationResult:
    message = replace_key_in_message(ANSWERS, '<question>', question)
    message = replace_key_in_message(message, '<answer>', answer)
    logging.info(f'Message sent to the model: {message}')

    response = execute_prompt(message)
    try:
        response = response.replace('\n', '')
        logging.info(f'Response received from the model: {response}')

        return EvaluationResult(
            question=question,
            answer=answer,
            grade=int(re.sub(r'[^0-9]', '', response)),
            explanation=response.lstrip()
        )
    except Exception as e:
        logging.error(f"Response {response}, error {e.__traceback__}")
        raise AIModelException("Error processing model")
