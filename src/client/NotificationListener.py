import threading


class NotificationListener(threading.Thread):
    def __init__(self, s, port, killListener):
        self.s = s
        self.port = port
        self.killListener = killListener
        super().__init__()

    def run(self):
        print('self s =', self.s)
        print(f'Client is listening to notifications on port {self.port}')
        self.s.listen(1)
        print('Listen..')
        conn, addr = self.s.accept()
        print('Server connected to notification socket. conn, addr =', conn, addr)
        while not self.killListener.is_set():
            notification = conn.recv(1024)
            # will handle based on notification type
            print('Notification:', notification.decode())

        self.s.close()
