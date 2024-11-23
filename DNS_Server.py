import pickle
import socket
import time
from collections import OrderedDict
import dns.resolver

CACHE_SIZE = 3
DEFAULT_TTL = 20
DNS_CACHE = OrderedDict()

AUTHORITATIVE_SERVERS = {
    "com": 5058,
    "edu": 5055,
    "gov": 5056,
    "in": 5057,
}

class DNS_MESSAGE:
    def __init__(self):
        self.header = None
        self.question = None
        self.answer = None

    def create(self, domain_name, ip_addr=None, type=0):
        self.header = (0, 0, 1, 0, 0, 0) if type == 0 else (0, 0, 1, 1, 0, 0)
        self.question = domain_name
        self.answer = ip_addr

    def serialize(self):
        return pickle.dumps(self)

    @staticmethod
    def deserialize(data):
        return pickle.loads(data)

def update_cache(domain_name, ip_address):
    current_time = time.time()
    if domain_name in DNS_CACHE:
        DNS_CACHE.move_to_end(domain_name)
    elif len(DNS_CACHE) >= CACHE_SIZE:
        DNS_CACHE.popitem(last=False)
    DNS_CACHE[domain_name] = (ip_address, current_time + DEFAULT_TTL)

def get_from_cache(domain_name):
    current_time = time.time()
    if domain_name in DNS_CACHE:
        ip_address, expiration = DNS_CACHE[domain_name]
        if current_time < expiration:
            DNS_CACHE.move_to_end(domain_name)
            return ip_address
        else:
            del DNS_CACHE[domain_name]
    return None

def query_authoritative_server(tld, domain_name):
    """Query an authoritative TLD server."""
    if tld not in AUTHORITATIVE_SERVERS:
        print(f"No authoritative server found for TLD: {tld}")
        return None

    server_address = ('0.0.0.0', AUTHORITATIVE_SERVERS[tld])
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Serialize the DNS_MESSAGE before sending
        message = DNS_MESSAGE()
        message.create(domain_name)
        serialized_message = message.serialize()

        # Send the serialized message
        client.sendto(serialized_message, server_address)
        data, _ = client.recvfrom(512)
        response = DNS_MESSAGE.deserialize(data)
        return response.answer  # Expect the IP address in the answer field
    except Exception as e:
        print(f"Error querying authoritative server: {e}")
        return None
    finally:
        client.close()


def query_external_root(domain_name):
    """Query real root servers for domain resolution."""
    try:
        result = dns.resolver.resolve(domain_name, 'A')
        return result[0].to_text()
    except Exception as e:
        print(f"External DNS query failed for {domain_name}: {e}")
        return None

def handle_query(data, addr, server):
    message = DNS_MESSAGE.deserialize(data)
    domain_name = message.question
    print(f"Received query for: {domain_name} from {addr}")

    cached_ip = get_from_cache(domain_name)
    if cached_ip:
        print(f"Cache hit for {domain_name}. Sending IP: {cached_ip}")
        response = DNS_MESSAGE()
        response.create(domain_name, cached_ip, 1)
        server.sendto(response.serialize(), addr)
        return

    tld = domain_name.split('.')[-1]
    ip_address = query_authoritative_server(tld, domain_name)
    if ip_address != 'NOT_FOUND':
        print(f"TLD server resolved {domain_name} to {ip_address}")
        response = DNS_MESSAGE()
        response.create(domain_name, ip_address, 1)
        server.sendto(response.serialize(), addr)
        update_cache(domain_name, ip_address)
        return

    external_ip = query_external_root(domain_name)
    if external_ip:
        print(f"External DNS resolved {domain_name} to {external_ip}")
        response = DNS_MESSAGE()
        response.create(domain_name, external_ip, 1)
        server.sendto(response.serialize(), addr)
        update_cache(domain_name, external_ip)
    else:
        print(f"Failed to resolve {domain_name}. Sending NOT_FOUND.")
        response = DNS_MESSAGE()
        response.create(domain_name, "NOT_FOUND", 1)
        server.sendto(response.serialize(), addr)

def dns_server(timeout_seconds):
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind(('0.0.0.0', 6053))  # Listen on port 6053
    print(f"DNS Server is running on port 6053...")

    start_time = time.time()
    while time.time() - start_time < timeout_seconds:
        data, addr = server.recvfrom(512)
        handle_query(data, addr, server)

    server.close()
    print("DNS Server shut down.")

if __name__ == "__main__":
    dns_server(timeout_seconds=60)
