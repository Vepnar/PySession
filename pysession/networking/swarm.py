import os
import json
import time
import random
import aiohttp
import asyncio

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

    async def storage_servers_from_seed(self):
        if self.storage_server_seed_cache:
            return self.storage_server_seed_cache

        seed = random.choice(self.seed_node_list)
        
        async with aiohttp.ClientSession() as session:
            async with session.post(''):
                pass

    async def get_swarm_node_url(self, pub_key):
        if not pub_key or len(pub_key) < 66:
            raise Exception(f'Invalid public key: {pub_key}, {len(pub_key)}')

        if not self.swarm_map[pub_key] or time.time() - self.swarm_map[pub_key] > 3600:
            async with self.swarm_url_lock:
                pass
