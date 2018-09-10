from .base_server import BaseServer
from typing import Optional, Dict, List, Union, Any


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