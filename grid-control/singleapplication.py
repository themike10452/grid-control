from PyQt5 import QtWidgets, QtCore, QtNetwork


class SingleApplication(QtWidgets.QMainWindow):
    def __init__(self, argv, key):
        super().__init__()

        self._memory = QtCore.QSharedMemory(self)
        self._memory.setKey(key)
        if self._memory.attach():
            self._other_instance = True
        else:
            self._other_instance = False
            if not self._memory.create(1):
                raise RuntimeError(self._memory.errorString())

    def other_instance_running(self):
        return self._other_instance


class SingleApplicationWithMessaging(SingleApplication):
    _server = None
    _message_event = QtCore.pyqtSignal(str)

    def __init__(self, argv, key):
        super().__init__(argv, key)

        self._key = key

        if self._server is None:
            self._server = QtNetwork.QLocalServer(self)

        if not self.other_instance_running():
            self._server.newConnection.connect(self._handle_message)
            self._server.listen(self._key)

    def _handle_message(self):
        socket = self._server.nextPendingConnection()
        if socket.waitForReadyRead(1000):
            self._message_event.emit(bytes(socket.readAll().data()).decode())
            socket.disconnectFromServer()

    def send_message(self, message, timeout=1000):
        if self.other_instance_running():
            socket = QtNetwork.QLocalSocket(self)
            socket.connectToServer(self._key, QtCore.QIODevice.WriteOnly)
            if socket.waitForConnected(1000):
                socket.write(str(message).encode())
                socket.waitForBytesWritten(timeout)

    def set_app_message_handler(self, handler):
        self._message_event.connect(handler)
