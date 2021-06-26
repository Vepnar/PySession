import os
import json
import time
import random
import typing

from .util import request_jsonrpc

# TODO: WORK IN PROGRESS

class Swarm():

    def __init__(self):
        
        # Create working variables
        self.swarm_url_lock = asyncio.Lock()
        self.swarm_map = {}
        self.storage_server_seed_cache = {}

        # Load seed for the swarm
        current = os.path.dirname(os.path.abspath(__file__))
        node_path = os.path.join(current,'cryptography', 'node_list.json')
        with open(node_path, 'r') as node_file:
            self.seed_node_list = json.loads(node_file)

    async def storage_servers_from_seed(self) -> list:
        if self.storage_server_seed_cache:
            return self.storage_server_seed_cache

        seed = random.choice(self.seed_node_list)
        
        params = {
            'active_only' : True,
            'limit' : 5  # Request only 5 for now.
            'fields' : {
                'public_ip' : True,
                'storage_port' : True,
                }
        }
        result = await request_jsonrpc(seed.url, 'get_n_service_nodes', params)
        result = filter(lambda node: node.public_ip != '0.0.0.0', result)
        result = map(lambda node: f'https://{node.public_ip}:{node.storage_port}/storage_rpc/v1')
        
        # Cache to speed up the progress
        self.storage_server_seed_cache = result
        
        return result

    async def get_swarm_node_url(self, pub_key):
        if not pub_key or len(pub_key) < 66:
            raise Exception(f'Invalid public key: {pub_key}, {len(pub_key)}')

        if not self.swarm_map[pub_key] or time.time() - self.swarm_map[pub_key] > 3600:
            async with self.swarm_url_lock:
                pass 
