import uuid
from typing import List

from fastapi import HTTPException
from starlette import status

import infra.repositories.project_repository as proj_repo
import infra.repositories.user_repository as user_repo
from constants import PROJECT_ALREADY_EXIST, PROJECT_DO_NOT_EXIST, USER_NOT_IN_PROJECT, USER_NOT_FOUND
from domain.evaluations import Project
from domain.users import User


def create_project(name: str, description, user: User) -> str:
    project = proj_repo.find_project_by_name(name)
    if project:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=PROJECT_ALREADY_EXIST)

    project = Project(
        id=str(uuid.uuid4()),
        name=name,
        description=description,
        users=[user.id]
    )

    proj_repo.insert_project(project)

    # Update user
    if not user.projects:
        user.projects = []
    user.projects.append(project.id)
    user_repo.update_user(user)

    return project.id


def get_projects(user: User) -> List:
    data = []
    for project_id in user.projects:
        project = proj_repo.find_project_by_id(project_id)
        data.append(project.to_api_response())

    return data


def update_project_info(project_id: str, name: str, description):
    project = proj_repo.find_project_by_id(project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=PROJECT_DO_NOT_EXIST)

    existing_project = proj_repo.find_project_by_name(name)
    if existing_project and existing_project.id != project_id:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=PROJECT_ALREADY_EXIST)

    updated_project = Project(
        id=project_id,
        name=name,
        description=description,
        users=project.users
    )

    proj_repo.update_project(updated_project)


def add_user_to_project(project_id: str, new_user_id: str, current_user: User):
    project = proj_repo.find_project_by_id(project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=PROJECT_DO_NOT_EXIST)

    if current_user.id not in project.users:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=USER_NOT_IN_PROJECT)

    user = user_repo.find_user_by_id(new_user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=USER_NOT_FOUND)

    # Update project
    project.users.append(new_user_id)
    proj_repo.update_project(project)

    # Update user
    if not user.projects:
        user.projects = []
    user.projects.append(project_id)
    user_repo.update_user(user)


def remove_user_to_project(project_id: str, new_user_id: str, current_user: User):
    project = proj_repo.find_project_by_id(project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=PROJECT_DO_NOT_EXIST)

    if current_user.id not in project.users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=USER_NOT_IN_PROJECT)

    user = user_repo.find_user_by_id(new_user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=USER_NOT_FOUND)

    # Update project
    project.users.remove(new_user_id)
    proj_repo.update_project(project)

    # Update user
    if not user.projects:
        user.projects = []
    user.projects.remove(project_id)
    user_repo.update_user(user)
