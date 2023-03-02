from typing import List

from fastapi import APIRouter, Depends
from starlette import status

import services.audit_services as audit
import services.project_services as pr_serv
import services.security_services as sec_serv
from domain.users import User

project_api = APIRouter()


@project_api.post('/create_project', tags=['Projects'], status_code=status.HTTP_201_CREATED)
async def create_project(name: str, description: str,
                         user: User = Depends(sec_serv.get_current_user)) -> str:
    """Creates a new project"""
    try:
        return pr_serv.create_project(name, description, user)
    finally:
        audit.audit_entity(user.id, 'created_project', {'name': name, 'description': description})


@project_api.get('/my_projects', tags=['Projects'], status_code=status.HTTP_200_OK)
async def get_project(user: User = Depends(sec_serv.get_current_user)) -> List:
    """Return the list of projects where the user belongs"""
    return pr_serv.get_projects(user)


@project_api.patch('/update_project_info', tags=['Projects'], status_code=status.HTTP_200_OK)
async def update_project_info(project_id: str, name: str, description: str,
                              user: User = Depends(sec_serv.get_current_user)) -> bool:
    """Updates the project information"""
    try:
        pr_serv.update_project_info(project_id, name, description)
        return True
    finally:
        audit.audit_entity(user.id, 'updated_project',
                           {'project_id': project_id, 'name': name, 'description': description})


@project_api.post('/add_user_to_project', tags=['Projects'], status_code=status.HTTP_201_CREATED)
async def add_user_to_project(project_id: str, new_user_id: str,
                              user: User = Depends(sec_serv.get_current_user)) -> bool:
    """Adds a user to a project"""
    try:
        pr_serv.add_user_to_project(project_id, new_user_id, user)
        return True
    finally:
        audit.audit_entity(user.id, 'added_user_to_project', {'project_id': project_id, 'new_user_id': new_user_id})


@project_api.delete('/remove_user_to_project', tags=['Projects'], status_code=status.HTTP_201_CREATED)
async def remove_user_to_project(project_id: str, user_id: str,
                                 user: User = Depends(sec_serv.get_current_user)) -> bool:
    """Remove a user to a project"""
    try:
        pr_serv.remove_user_to_project(project_id, user_id, user)
        return True
    finally:
        audit.audit_entity(user.id, 'removed_user_to_project', {'project_id': project_id, 'user_id': user_id})
