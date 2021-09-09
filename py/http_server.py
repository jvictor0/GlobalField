import SimpleHTTPServer 
import SocketServer
import time
import util
import threading
import os.path

def HTMLPath(path):
    return os.path.dirname(os.path.abspath(__file__)) + "/../html/" + path

class Handler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_GET(self):
        global g_ctx
        
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            with open(HTMLPath("main.html"), "r") as f:
                self.wfile.write(f.read())
        elif self.path == "/get_mutation_energy":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(str(g_ctx.MutationEnergy()))
        else:
            self.send_response(404)

def ServerThread(ctx, host='localhost', port=2516):
    global g_ctx
    g_ctx = ctx

    SocketServer.TCPServer.allow_reuse_address = True
    web_server = SocketServer.TCPServer((host, port), Handler)
    util.TraceInfo("Server", "Server started http://%s:%s" % (host, port))

    try:
        web_server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        web_server.server_close()
        util.TraceInfo("Server", "Server stopped")

g_ctx = None
        
def LaunchServer(ctx, host='localhost', port=2516):
    t = threading.Thread(target=ServerThread, args=(ctx, host, port))
    t.start()

if __name__ == "__main__":
    LaunchServer(None)