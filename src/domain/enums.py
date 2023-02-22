from enum import Enum


class Environment(Enum):
    PROD = 'PROD'
    STAGE = 'STAGE'
    DEV = 'DEV'


class State(Enum):
    INACTIVE = 'inactive'
    ACTIVE = 'active'


class Language(Enum):
    SPANISH = 'spanish'
    ENGLISH = 'english'


class UserRole(Enum):
    STAFFER = 'staffer'
    EXPERT = 'expert'
    ADMIN = 'admin'
