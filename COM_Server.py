import socket
import pickle

# Domain data for .com TLD
COM_DOMAINS = {
    "example.com": "93.184.216.34",
    "localtest.com": "127.0.0.1",
    "abcd.com": "108.98.98.2",
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

def tld_server(port, domain_data):
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        server.bind(('0.0.0.0', port))
        print(f"TLD Server is running on port {port}...")

        while True:
            data, addr = server.recvfrom(512)
            #print(f"Raw data received: {data}")

            try:
                # Attempt to deserialize the data
                message = DNS_MESSAGE.deserialize(data)
            except Exception as e:
                print(f"Deserialization failed: {e}")
                continue  # Skip to the next iteration if deserialization fails

            domain_name = message.question
            print(f"TLD Server received query for: {domain_name}")

            # Search for the domain in the TLD's database
            ip_address = domain_data.get(domain_name, "NOT_FOUND")

            # Prepare and send the response
            response = DNS_MESSAGE()
            response.create(domain_name, ip_address, type=1)
            server.sendto(response.serialize(), addr)

    finally:
        server.close()
        print("TLD Server shut down.")

if __name__ == "__main__":
    tld_server(port=5058, domain_data=COM_DOMAINS)
