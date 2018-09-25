from typing import Optional, Dict, List, Union, Any, Tuple

import requests

from kron.kronbute import NotFoundError
from .base_server import BaseServer


class JobServer:
    def __init__(self, server: BaseServer):
        self.server = server

    def list(self) -> List[Dict[str, Any]]:
        return self.server.list('api/jobs')

    def view(self, job_id: Union[int, str]) -> Dict[str, Any]:
        return self.server.get('api/jobs', job_id)

    def create(self, name: str, image: str, tag: str, schedule: str, env: Dict[str, str], entrypoint: str,
               alias: Optional[str], groups: Tuple[str], timezone: str) -> Optional[int]:

        data = {'name': name, 'image': image, 'tag': tag, 'schedule': schedule, 'entryPoint': entrypoint,
                'environment': env, 'timeZone': timezone}

        if alias:
            data['alias'] = alias

        data['groups'] = groups

        created_job = self.server.create('api/jobs', data)

        return created_job

    def edit(self, job_id: Union[int, str], name: Optional[str], image: Optional[str], tag: Optional[str],
             schedule: Optional[str], alias: Optional[str], env: Optional[Dict[str, str]],
             entrypoint: Optional[str], groups: Tuple[str], timezone: str):

        current_job = self.server.get('api/jobs', job_id)

        data = {'name': name or current_job['name'],
                'image': image or current_job['image'],
                'tag': tag or current_job['tag'],
                'schedule': schedule or current_job['schedule'],
                'alias': alias or current_job['alias'],
                'entryPoint': entrypoint or current_job['entryPoint'],
                'groups': list(groups) or current_job['groups'],
                'timeZone': timezone or current_job['timeZone'],
                'environment': env or current_job['environment']
                }

        self.server.edit('api/jobs', job_id, data)

    def delete(self, job_id: Union[str, int]):
        self.server.delete('api/jobs', job_id)

    def run_now(self, job_id: Union[str, int]):
        response = requests.post(f'{self.server.url}/api/jobs/{job_id}/run')
        if response.status_code == 404:
            raise NotFoundError(job_id)
