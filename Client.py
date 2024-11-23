import pickle
import socket

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


# Updated client code for proper serialization
def query_dns_server(server_address, domain_name):
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Create and serialize DNS_MESSAGE
        message = DNS_MESSAGE()
        message.create(domain_name)
        serialized_message = message.serialize()

        # Send serialized message
        client.sendto(serialized_message, server_address)
        data, _ = client.recvfrom(512)

        # Deserialize the received data
        response = DNS_MESSAGE.deserialize(data)
        return response
    except Exception as e:
        print(f"Error querying DNS server: {e}")
        return None
    finally:
        client.close()



if __name__ == "__main__":
    domain_name = input("Enter the domain name: ")
    local_dns_server_address = ('54.205.107.129', 6053)
    response = query_dns_server(local_dns_server_address, domain_name)

    if response and response.answer == "NOT_FOUND":
        print("Fatal Error: Domain Name does not exist")
    else:
        print(f"DNS resolved '{domain_name}' to {response.answer}")
