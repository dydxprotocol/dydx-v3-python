import json
from threading import Thread
import websocket


class WSClient(websocket.WebSocketApp):

    callback = print

    @staticmethod
    def on_open(ws):
        WSClient.callback('-- connection established --')

    @staticmethod
    def on_close(ws, close_status_code, close_msg):
        WSClient.callback('-- connection closed --')

    @staticmethod
    def on_message(ws, message):
        if json.loads(message)['type'] == 'channel_data':
            WSClient.callback(message)

    @staticmethod
    def on_error(ws, message):
        WSClient.callback(message)

    def __init__(self, host):
        self.uri = host
        super().__init__(
            self.uri,
            on_open=self.on_open,
            on_close=self.on_close,
            on_message=self.on_message,
            on_error=self.on_error
            )
        self._thread = None
    
    def subscribe_to_orderbook(self, trading_pair):
        self.send({'type': "subscribe", "channel": "v3_orderbook", "id": trading_pair})

    def subscribe_to_trades(self, trading_pair):
        self.send({'type': "subscribe", "channel": "v3_trades", "id": trading_pair})

    def subscribe_to_markets(self):
        self.send({'type': "subscribe", "channel": "v3_markets"})
    
    def send(self, data, *args):
        super().send(json.dumps(data), *args)

    def start(self):
        if self._thread:
            return self._thread
        self._thread = Thread(target=self.run_forever, args=())
        self._thread.start()

    def stop(self):
        if not self._thread:
            return
        try:
            self.close()
            self._thread.join()
        finally:
            self._thread = None
