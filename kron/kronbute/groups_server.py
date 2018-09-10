from .base_server import BaseServer
from typing import Optional, Dict, List, Union, Any


class GroupsServer:
    def __init__(self, server: BaseServer):
        self.server = server

    def list(self) -> List[Dict[str, Optional[Any]]]:
        return self.server.list('api/groups')

    def view(self, group_id: Union[str, int]) -> Dict[str, Optional[Any]]:
        return self.server.get('api/groups', group_id)

    def delete(self, group_id: Union[str, int]) -> None:
        self.server.delete('api/groups', group_id)

    def create(self, name: str, environment: Dict[str, Optional[Any]]) -> Optional[int]:
        data = {
            'name': name,
            'environment': environment or {}
        }
        return self.server.create('api/groups', data)

    def edit(self, group_id: Union[str, int], name: Optional[str], environment: Optional[Dict[str, Any]]):
        existing_group = self.server.get('api/groups', group_id)

        data = {
            'name': name or existing_group['name'],
            'environment': environment or existing_group['environment'] or {}
        }
        return self.server.edit('api/groups', group_id, data)
