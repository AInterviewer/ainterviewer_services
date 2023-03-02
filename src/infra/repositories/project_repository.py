from typing import Dict

from domain.evaluations import Project
from infra.repositories.general_repository import AINTERVIEWER_CLIENT

PROJECTS_COLLECTION = AINTERVIEWER_CLIENT.projects


def insert_project(project: Project):
    PROJECTS_COLLECTION.insert_one(project.to_dict())


def find_project_by_id(project_id: str):
    project_data = PROJECTS_COLLECTION.find_one({'_id': project_id})
    if project_data:
        return deserialize_project(project_data)


def find_project_by_name(project_name: str):
    project_data = PROJECTS_COLLECTION.find_one({'name': project_name})
    if project_data:
        return deserialize_project(project_data)


def deserialize_project(project_data: Dict) -> Project:
    return Project(
        id=project_data.get('_id'),
        name=project_data.get('name'),
        description=project_data.get('description'),
        users=project_data.get('users')
    )


def update_project(project: Project):
    PROJECTS_COLLECTION.update_one(
        {'_id': project.id},
        {'$set': {
            'name': project.name,
            'description': project.description,
            'users': project.users
        }}
    )
