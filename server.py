import socket
import tornado.gen
import tornado.ioloop
import tornado.iostream
import tornado.tcpserver
import tornado.tcpclient
import json
import mongo
import postgres
from itertools import count


class EconomiTcpServer(object):
    connection_id = count(0, 1)

    def __init__(self, stream, mongo_conn, postgres_conn):
        super().__init__()
        self.mongo_connection = mongo_conn
        self.postgres_connection = postgres_conn
        self.stream = stream
        self.id = self.connection_id.__next__()
        self.stream.socket.setsockopt(
            socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.stream.socket.setsockopt(
            socket.IPPROTO_TCP, socket.SO_KEEPALIVE, 1)
        self.stream.set_close_callback(self.on_disconnect)

    def get_units(self, uid):
        return self.mongo_connection.get_units(uid)

    def get_unit(self, unit_id):
        return self.mongo_connection.get_unit(unit_id)

    def get_user_data(self, uid):
        return self.postgres_connection.get_data(uid)

    def set_user_data(self, ):


    @staticmethod
    def format_(obj, out=False):
        return bytes(f"{json.dumps(obj)}\n", "utf-8") if out else json.loads(obj.decode("utf-8"))

    @tornado.gen.coroutine
    def on_disconnect(self):
        self.log(f"Connection {self.id} disconnected")
        yield []

    @tornado.gen.coroutine
    def dispatch_client(self):
        try:
            while True:
                line = yield self.stream.read_until(b'\n')
                data = self.format_(line)
                self.log('got |%s|' % str(data))
                yield self.stream.write(self.format_(data['args'], out=True))
        except tornado.iostream.StreamClosedError:
            pass

    @tornado.gen.coroutine
    def on_connect(self):
        raddr = 'closed'
        try:
            raddr = '%s:%d' % self.stream.socket.getpeername()
        except Exception:
            pass
        self.log('new, %s' % raddr)

        yield self.dispatch_client()

    def log(self, msg, *args, **kwargs):
        print('[Connection %d] %s' % (self.id, msg))


class TcpServer(tornado.tcpserver.TCPServer):
    mongo_connection = mongo.MongoConnection()
    postgres_connection = postgres.PostgresConnection()

    @tornado.gen.coroutine
    def handle_stream(self, stream, address):
        """
        Called for each new connection, stream.socket is
        a reference to socket object
        """
        connection = EconomiTcpServer(stream, self.mongo_connection, self.postgres_connection)
        yield connection.on_connect()


def main():
    # configuration
    host = '0.0.0.0'
    port = 8008

    # tcp server
    server = TcpServer()
    server.listen(port, host)
    print("Listening on %s:%d..." % (host, port))

    # infinite loop
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
