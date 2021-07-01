import os
import json
import time
import random
import typing

from .util import request_jsonrpc

# TODO: WORK IN PROGRESS
# TODO: Create a node dataclass


class SwarmException(Exception):
    pass


class Swarm:
    def __init__(self):

        # Create working variables
        self.swarm_url_lock = asyncio.Lock()
        self.swarm_map = {}
        self.storage_server_seed_cache = {}

        # Load seed for the swarm
        current = os.path.dirname(os.path.abspath(__file__))
        node_path = os.path.join(current, "cryptography", "node_list.json")
        with open(node_path, "r") as node_file:
            self.seed_node_list = json.loads(node_file)

    async def storage_servers_from_seed(self) -> list:
        if self.storage_server_seed_cache:
            return self.storage_server_seed_cache

        seed = random.choice(self.seed_node_list)

        params = {
            "active_only": True,
            "limit": 5,  # Request only 5 for now.
            "fields": {
                "public_ip": True,
                "storage_port": True,
            },
        }
        result = await request_jsonrpc(seed.url, "get_n_service_nodes", params)
        result = filter(lambda node: node.public_ip != "0.0.0.0", result)
        result = map(
            lambda node: f"https://{node.public_ip}:{node.storage_port}/storage_rpc/v1"
        )

        # Cache to speed up the progress
        self.storage_server_seed_cache = result

        return result

    async def storage_servers_from_service_nodes(self) -> list:
        node_url = await self.random_service_node(True)

        # Retrieve all service nodes
        # NOTE: This requests all service nodes every time. needs some optimization.
        params = {
            "active_only": True,
            "fields": {"public_ip": True, "storage_port": True},
        }

        result = await request_jsonrpc(
            node_url, "oxend_request", params, options={"snode": True}
        )
        result = filter(lambda node: node.public_ip != "0.0.0.0", result)
        result = map(
            lambda node: f"https://{node.public_ip}:{node.storage_port}:/storage_rpc/v1"
        )
        return result

    async def random_service_node(self, use_seed: bool = False) -> str:
        storage_nodes = [x for nodes in self.swarm_map.snodes for x in nodes]
        storage_nodes = map(
            lambda node: f"https://{node.ip}:{node.port}/storage_rpc/v1"
        )

        if use_seed:
            storage_nodes.append(await self.storage_servers_from_seed())
        else:
            storage_nodes.append(await self.storage_servers_from_service_nodes())
        return random.choice(storage_nodes)

    async def get_swarm_node_url(self, public_key) -> str:
        """Retrieve a single swarm node url"""
        if not public_key or len(public_key) < 66:
            raise Exception(f"Invalid public key: {public_key}, {len(public_key)}")

        if (
            not self.swarm_map[public_key]
            or time.time() - self.swarm_map[public_key] > 3600
        ):
            async with self.swarm_url_lock:
                node_url = await self.random_storage_node(False)
                node_data = await self.ublic_key_ask(
                    node_url, "get_snode_for_pubkey", public_key
                )
                if not node_data:
                    raise SwarmException(
                        f"Could not get storage nodes from {node_url} pub: {public_key}"
                    )
                if not "snodes" in node_data:
                    raise SwarmException(
                        f"Could not get storage nodes object from {node_url}, {public_key}"
                    )

                random_node = random.choice(self.swarm_map[public_key].snodes)
                return f"https://{random_node.ip}:{random_node.port}/storage_rpc/v1"
