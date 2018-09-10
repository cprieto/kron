import re
import abc
import urllib.parse
from typing import Optional, Dict, List, Union, Any, Any

import requests

from .errors import ServerError, ArgumentValidationError, NotFoundError, AliasAlreadyExistsError

version_regex = re.compile(r"hello!, version: (?P<version>.*)")


class Kronbute:
    def __init__(self, url: str):
        self.url = url

    @property
    def version(self) -> str:
        res = requests.get(urllib.parse.urljoin(self.url, 'hello'))
        if res.status_code != 200:
            raise ServerError(f'Server returned an invalid version or answer', res.status_code, res.text)

        match = version_regex.match(res.text)
        version = match.group('version')

        return version

    def list_jobs(self) -> List[Dict[str, str]]:
        res = requests.get(urllib.parse.urljoin(self.url, 'api/jobs'))
        if res.status_code != 200:
            raise ServerError(f'Error when requesting info to server', res.status_code, res.text)
        data = res.json()

        return data

    def create_job(self, name: str, image: str, tag: str, schedule: str, env: Dict[str, str], entrypoint: str,
                   alias: Optional[str]) -> int:

        data = {'name': name, 'image': image, 'tag': tag, 'schedule': schedule, 'entryPoint': entrypoint}
        if len(env) > 0:
            data['environment'] = [{'key': key, 'value': value or ''} for key, value in env.items()]

        if alias:
            data['alias'] = alias

        res = requests.post(urllib.parse.urljoin(self.url, 'api/jobs'), json=data)
        if res.status_code == 400:
            raise ArgumentValidationError(res.text)

        if res.status_code == 409:
            raise AliasAlreadyExistsError(alias)

        if res.status_code != 201:
            raise ServerError(f'Error when requesting info to server', res.status_code, res.text)

        data = res.json()

        return data

    def get_job(self, job_id: Union[int, str]) -> Dict[str, Union[str, Dict[str, str]]]:
        res = requests.get(urllib.parse.urljoin(self.url, f'api/jobs/{job_id}'))
        if res.status_code == 404:
            raise NotFoundError(job_id)

        if res.status_code != 200:
            raise ServerError("Error when retrieving job from server", res.status_code, res.text)

        return res.json()

    def edit_job(self, job_id: Union[int, str], name: Optional[str], image: Optional[str], tag: Optional[str],
                 schedule: Optional[str], alias: Optional[str], env: Optional[Dict[str, str]],
                 entrypoint: Optional[str]) -> None:
        res = requests.get(urllib.parse.urljoin(self.url, f'api/jobs/{job_id}'))
        if res.status_code == 404:
            raise NotFoundError(job_id)

        current_job = res.json()

        data = {
            'name': name or current_job['name'],
            'image': image or current_job['image'],
            'tag': tag or current_job['tag'],
            'schedule': schedule or current_job['cron'],
            'alias': alias or current_job['alias'],
            'entryPoint': entrypoint or current_job['entryPoint']
        }

        if 'entryPoint' in current_job:
            data['environment'] = [{'key': key, 'value': value or ''}
                                   for key, value in current_job['environment'].items()]

        if env:
            data['environment'] = [{'key': key, 'value': value or ''}
                                   for key, value in env.items()]

        res = requests.put(urllib.parse.urljoin(self.url, f'api/jobs/{job_id}'), json=data)
        if res.status_code == 400:
            raise ArgumentValidationError(res.text)

        if res.status_code != 202:
            raise ServerError(f"Error while processing update for job:", res.status_code, res.text)

    def delete_job(self, job_id: Union[int, str]):
        res = requests.delete(urllib.parse.urljoin(self.url, f'api/jobs/{job_id}'))

        if res.status_code == 404:
            raise NotFoundError(job_id)

        if res.status_code != 204:
            raise ServerError(f'Error when requesting info to server, {res.status_code}', res.status_code, res.text)

    def list_runs(self):
        res = requests.get(urllib.parse.urljoin(self.url, 'api/runs'))

        if res.status_code != 200:
            raise ServerError(f'Error when requesting info to server', res.status_code, res.text)

        data = res.json()

        return data


class BaseServer:
    def __init__(self, url: str):
        self.url = url

    @property
    def version(self) -> str:
        res = requests.get(urllib.parse.urljoin(self.url, 'hello'))
        if res.status_code != 200:
            raise ServerError(f'Server returned an invalid version or answer', res.status_code, res.text)

        match = version_regex.match(res.text)
        version = match.group('version')

        return version

    def list(self, endpoint: str) -> List[Any]:
        res = requests.get(urllib.parse.urljoin(self.url, endpoint))
        if res.status_code != 200:
            raise ServerError(f'Error when requesting info to server', res.status_code, res.text)
        data = res.json()

        return data

    def get(self, endpoint: str, entity_id: Union[int, str]) -> Dict[str, Any]:
        res = requests.get(urllib.parse.urljoin(self.url, f'{endpoint}/{entity_id}'))
        if res.status_code == 404:
            raise NotFoundError(entity_id)

        if res.status_code != 200:
            raise ServerError("Error when retrieving entity from server", res.status_code, res.text)

        return res.json()

    def create(self, endpoint: str, data: Dict[Any, Optional[Any]]) -> Optional[int]:
        res = requests.post(urllib.parse.urljoin(self.url, endpoint), json=data)
        if res.status_code == 400:
            raise ArgumentValidationError(res.text)

        if res.status_code == 409:
            raise AliasAlreadyExistsError()

        if res.status_code != 201:
            raise ServerError(f'Error when creating entity', res.status_code, res.text)

        data = res.json()

        return data

    def edit(self, endpoint: str, entity_id: Union[int, str], data: Dict[Any, Optional[Any]]):
        res = requests.put(urllib.parse.urljoin(self.url, f'{endpoint}/{entity_id}'), json=data)
        if res.status_code == 400:
            raise ArgumentValidationError(res.text)

        if res.status_code != 202:
            raise ServerError(f"Error while processing update for job:", res.status_code, res.text)

    def delete(self, endpoint: str, entity_id: Union[str, int]):
        res = requests.delete(urllib.parse.urljoin(self.url, f'{endpoint}/{entity_id}'))

        if res.status_code == 404:
            raise NotFoundError(entity_id)

        if res.status_code != 204:
            raise ServerError(f'Error when requesting info to server, {res.status_code}', res.status_code, res.text)


class JobServer:
    def __init__(self, server: BaseServer):
        self.server = server

    def list(self) -> List[Dict[str, Any]]:
        return self.server.list('api/jobs')

    def view(self, job_id: Union[int, str]) -> Dict[str, Any]:
        return self.server.get('api/jobs', job_id)

    def create(self, name: str, image: str, tag: str, schedule: str, env: Dict[str, str], entrypoint: str,
                   alias: Optional[str]) -> Optional[int]:
        data = {'name': name, 'image': image, 'tag': tag, 'schedule': schedule, 'entryPoint': entrypoint}
        if len(env) > 0:
            data['environment'] = [{'key': key, 'value': value or ''} for key, value in env.items()]

        if alias:
            data['alias'] = alias

        created_job = self.server.create('api/jobs', data)

        return created_job

    def edit(self, job_id: Union[int, str], name: Optional[str], image: Optional[str], tag: Optional[str],
                 schedule: Optional[str], alias: Optional[str], env: Optional[Dict[str, str]],
                 entrypoint: Optional[str]):

        current_job = self.server.get('api/jobs', job_id)

        data = {
            'name': name or current_job['name'],
            'image': image or current_job['image'],
            'tag': tag or current_job['tag'],
            'schedule': schedule or current_job['cron'],
            'alias': alias or current_job['alias'],
            'entryPoint': entrypoint or current_job['entryPoint']
        }

        if 'entryPoint' in current_job:
            data['environment'] = [{'key': key, 'value': value or ''}
                                   for key, value in current_job['environment'].items()]

        if env:
            data['environment'] = [{'key': key, 'value': value or ''}
                                   for key, value in env.items()]

        self.server.edit('api/jobs', job_id, data)

    def delete(self, job_id: Union[str, int]):
        self.server.delete('api/jobs', job_id)


class RunsServer:
    def __init__(self, server: BaseServer):
        self.server = server

    def list(self):
        return self.server.list('api/runs')
