import urllib.parse
from typing import Optional, Dict, List

import click
import requests


class ServerException(Exception):
    def __init__(self, message: str, code: Optional[int]):
        super().__init__(message)
        self.code = code


class Kronbute:
    def __init__(self, url: str):
        self.url = url

    def list_jobs(self) -> List[Dict[str, str]]:
        res = requests.get(urllib.parse.urljoin(self.url, 'api/jobs'))
        if res.status_code != 200:
            raise ServerException(f'Error when requesting info to server', res.status_code)
        data = res.json()

        return data

    def create_job(self, name: str, image: str, tag: str, schedule: str, env: Dict[str, str]) -> int:
        data = {'name': name, 'image': image, 'tag': tag, 'schedule': schedule}
        if len(env) > 0:
            data['environment'] = [{'key': key, 'value': value or ''} for key, value in env.items()]

        res = requests.post(urllib.parse.urljoin(self.url, 'api/jobs'), json=data)
        if res.status_code != 201:
            raise ServerException(f'Error when requesting info to server', res.status_code)

        data = res.json()

        return data

    def get_job(self, job_id: int) -> Dict[str, str]:
        res = requests.get(urllib.parse.urljoin(self.url, f'api/jobs/{job_id}'))
        if res.status_code != 200:
            raise ServerException("Error when retrieving job from server", res.status_code)

        return res.json()

    def edit_job(self, job_id: int, name: str, image: str, tag: str, schedule: str, env: Dict[str, str]) -> None:
        data = {'name': name, 'image': image, 'tag': tag, 'schedule': schedule, 'environment': []}
        if len(env) > 0:
            data['environment'] = [{'key': key, 'value': value or ''} for key, value in env.items()]

        res = requests.put(urllib.parse.urljoin(self.url, f'api/jobs/{job_id}'), json=data)

        if res.status_code != 202:
            raise ServerException(f'Error when requesting info to server, {res.status_code}', res.status_code)

    def delete_job(self, job_id: int):
        res = requests.delete(urllib.parse.urljoin(self.url, f'api/jobs/{job_id}'))

        if res.status_code != 204:
            raise ServerException(f'Error when requesting info to server, {res.status_code}', res.status_code)


pass_server = click.make_pass_decorator(Kronbute)
