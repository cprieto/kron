import re
import urllib.parse
from typing import Optional, Dict, List, Union, Any, Any

import requests

from .errors import ServerError, ArgumentValidationError, NotFoundError, AliasAlreadyExistsError

version_regex = re.compile(r"hello!, version: (?P<version>.*)")


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