from __future__ import annotations

import json
import threading
import uuid
from typing import Any

import paho.mqtt.client as mqtt


class GestureMqttClient:
    def __init__(
        self,
        *,
        host: str,
        port: int,
        username: str,
        password: str,
        client_id_prefix: str,
    ) -> None:
        client_id = f"{client_id_prefix}-{uuid.uuid4().hex[:8]}"
        self._client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=client_id)
        self._client.username_pw_set(username=username, password=password)
        self._client.reconnect_delay_set(min_delay=1, max_delay=10)
        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect
        self._host = host
        self._port = port
        self._connected = False
        self._lock = threading.Lock()

    @property
    def is_connected(self) -> bool:
        with self._lock:
            return self._connected

    def _on_connect(  # noqa: PLR0913
        self,
        _client: mqtt.Client,
        _userdata: Any,
        _flags: Any,
        reason_code: mqtt.ReasonCode,
        _properties: Any,
    ) -> None:
        with self._lock:
            self._connected = reason_code.value == 0

    def _on_disconnect(
        self,
        _client: mqtt.Client,
        _userdata: Any,
        _disconnect_flags: Any,
        _reason_code: mqtt.ReasonCode,
        _properties: Any,
    ) -> None:
        with self._lock:
            self._connected = False

    def connect(self) -> None:
        self._client.connect(self._host, self._port, keepalive=60)
        self._client.loop_start()

    def publish(self, topic: str, payload: dict[str, Any], *, qos: int, retain: bool = False) -> bool:
        serialized = json.dumps(payload, separators=(",", ":"))
        info = self._client.publish(topic, serialized, qos=qos, retain=retain)
        return info.rc == mqtt.MQTT_ERR_SUCCESS

    def close(self) -> None:
        self._client.loop_stop()
        self._client.disconnect()

