import re
import urllib.parse
from typing import Optional, Dict, List, Union

import click
import requests

regex = re.compile(r"hello!, version: (?P<version>.*)")


class ServerError(Exception):
    def __init__(self, message: str, code: Optional[int], body: str):
        super().__init__(message)
        self.code = code
        self.body = body


class NotFoundError(Exception):
    def __init__(self, query: Union[str, int], entity: str = 'job'):
        self.query = query
        self.entity = entity


class ArgumentValidationError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class AliasAlreadyExistsError(Exception):
    def __init__(self, alias: Optional[str] = None):
        self.alias = alias


class Kronbute:
    def __init__(self, url: str):
        self.url = url

    @property
    def version(self) -> str:
        res = requests.get(urllib.parse.urljoin(self.url, 'hello'))
        if res.status_code != 200:
            raise ServerError(f'Server returned an invalid version or answer', res.status_code, res.text)

        match = regex.match(res.text)
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

    def get_job(self, job_id: int) -> Dict[str, str]:
        res = requests.get(urllib.parse.urljoin(self.url, f'api/jobs/{job_id}'))
        if res.status_code == 404:
            raise NotFoundError(job_id)

        if res.status_code != 200:
            raise ServerError("Error when retrieving job from server", res.status_code, res.text)

        return res.json()

    def edit_job(self, job_id: int, name: Optional[str], image: Optional[str], tag: Optional[str], schedule: Optional[str], env: Optional[Dict[str, str]], entrypoint: Optional[str]) -> None:
        res = requests.get(urllib.parse.urljoin(self.url, f'api/jobs/{job_id}'))
        if res.status_code == 404:
            raise NotFoundError(job_id)

        current_job = res.json()

        data = {
            'name': name or current_job['name'],
            'image': image or current_job['image'],
            'tag': tag or current_job['tag'],
            'schedule': schedule or current_job['cron'],
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

    def delete_job(self, job_id: int):
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


pass_server = click.make_pass_decorator(Kronbute)
