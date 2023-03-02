from dataclasses import dataclass


@dataclass
class ApiCallException(Exception):
    message: str
    exception: Exception


@dataclass
class BusinessException(Exception):
    message: str


@dataclass
class AIModelException(Exception):
    message: str
