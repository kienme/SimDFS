import math
import pickle
import random

from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler


# TODO: Read from config file
MAPPING_STORE_PATH = "./mapping"
REPLICATION_FACTOR = 2
BLOCK_SIZE = 30  # Bytes
DN_LIST = [
    "http://simpdfs_dn_1:1111",
    "http://simpdfs_dn_2:1111",
    "http://simpdfs_dn_3:1111",
]


class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ("/RPC2",)


class Mapping:
    """
    Maintain mapping of file to its block locations.

    Key: File path string
    Value: List where i'th element is replica list for i'th block

    Sample
    {
        'p11/p12/p13': [
            ['h1', 'h3'], ['h2', 'h3'], ['h1', 'h2']
        ],
        ...
    }
    """

    def __init__(self, mapping_store_path=None):
        """Initialize mapping."""
        self.map = {}
        if mapping_store_path is not None:
            with open(mapping_store_path, "rb") as f:
                try:
                    self.map = pickle.load(f)
                except EOFError:
                    self.map = {}

    # Assuming this is called sequentially
    def add_block(self, path, seq, locations):
        """Add block and its locations to the map."""
        if seq == 0:
            self.map[path] = []
        self.map[path].append(locations)

    def get_mapping(self, path):
        """Return block locations for given path."""
        return self.map[path]

    def persist(self, mapping_store_path):
        """Persist mapping to file."""
        print("Persisting this boi")
        print(self.map)
        with open(mapping_store_path, "wb") as f:
            pickle.dump(self.map, f)


# Global map
mapping = Mapping(MAPPING_STORE_PATH)


def get_locations(path):
    return mapping.get_mapping(path)


def get_locations_new(path, file_size):
    """Return block size and mapping of blocks to replicas."""
    global mapping

    num_blocks = math.ceil(file_size / BLOCK_SIZE)
    for i in range(0, num_blocks):
        replicas = random.sample(DN_LIST, REPLICATION_FACTOR)
        mapping.add_block(path, i, replicas)

    # Assume writes always succeed
    mapping.persist(MAPPING_STORE_PATH)

    ret = {"block_size": BLOCK_SIZE, "map": mapping.get_mapping(path)}

    return ret


def main():
    print("Starting MDN")
    print(mapping.map)
    # get_locations_new('myfile1', 24)
    # print(get_locations('myfile1'))

    with SimpleXMLRPCServer(("0.0.0.0", 2222), requestHandler=RequestHandler) as server:
        server.register_introspection_functions()

        server.register_function(get_locations)
        server.register_function(get_locations_new)

        print("Awaiting requests")
        server.serve_forever()

    print("Stopping MDN")


if __name__ == "__main__":
    main()
