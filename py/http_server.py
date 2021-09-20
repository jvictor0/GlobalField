import SimpleHTTPServer 
import SocketServer
import time
import util
import threading
import os.path
import serialize_for_web
import json

def HTMLPath(path):
    return os.path.dirname(os.path.abspath(__file__)) + "/../html/" + path

def JSPath(path):
    return os.path.dirname(os.path.abspath(__file__)) + "/../js/" + path

class Handler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_GET(self):
        global g_ctx
        
        if self.path in ["/", "/control"]:
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            fname = "main.html" if self.path == "/" else "control.html"
            with open(HTMLPath(fname), "r") as f:
                self.wfile.write(f.read())

        elif self.path == "/get_data" and g_ctx is not None:
            self.send_response(200)
            self.send_header("Content-type", "text/json")
            self.end_headers()
            self.wfile.write(json.dumps(serialize_for_web.SerializeContext(g_ctx)))

        elif self.path[:5] == "/set?" and g_ctx is not None:
            HandleSet(g_ctx, self.path[5:])
            self.send_response(200)
            self.send_header("Content-type", "text/json")
            self.end_headers()

        elif self.path[-3:] == ".js":
            file_path = JSPath(self.path)
            if os.path.exists(file_path):
                self.send_response(200)
                self.send_header("Content-type", "text/javascript")
                self.end_headers()
                with open(file_path, "r") as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(404)                

        else:
            print "path", self.path
            print "headeres", self.headers
            self.send_response(404)


def HandleSet(ctx, query_string):
    query = util.ParseURLQuery(query_string)
    if "tempo" in query:
        ctx.clock_info.SetTempoBPM(float(query["tempo"]))

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
    ServerThread(None)
