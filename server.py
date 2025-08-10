from http.server import HTTPServer, SimpleHTTPRequestHandler
import os

class AudioServer(SimpleHTTPRequestHandler):
    def do_GET(self):
        # Serve the player.html file as the index
        if self.path == '/':
            self.path = '/player.html'
        return SimpleHTTPRequestHandler.do_GET(self)

def run_server(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, AudioServer)
    print(f"Server running on http://localhost:{port}")
    httpd.serve_forever()

if __name__ == '__main__':
    run_server() 