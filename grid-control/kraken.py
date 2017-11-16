import usb.core
import usb.util
import threading
from datetime import datetime


class Kraken:
    _vid = 0x1e71
    _pid = 0x170e
    _read_interval = 0.5

    _devlock = threading.Lock()
    _dev = None
    _is_supported = False
    _status = None
    _last_update_time = datetime.min

    @staticmethod
    def init():
        with Kraken._devlock:
            if Kraken._dev is None:
                Kraken._dev = usb.core.find(idVendor=Kraken._vid, idProduct=Kraken._pid)

                if Kraken._dev is not None:
                    Kraken._dev.set_configuration()
                    Kraken._is_supported = True
                else:
                    Kraken._is_supported = False
                    print('Kraken not detected')

    @staticmethod
    def is_supported():
        return Kraken._is_supported

    @staticmethod
    def read_fan_rpm():
        with Kraken._devlock:
            if Kraken._dev is not None:
                status = Kraken._read_status()
                fs = status[3] << 8 | status[4]
                return fs
            else:
                return 0

    @staticmethod
    def read_pump_rpm():
        with Kraken._devlock:
            if Kraken._dev is not None:
                status = Kraken._read_status()
                ps = status[5] << 8 | status[6]
                return ps
            else:
                return 0

    @staticmethod
    def read_liquid_temp():
        with Kraken._devlock:
            if Kraken._dev is not None:
                status = Kraken._read_status()
                lt = status[1] + status[2] / 10
                return lt
            else:
                return 0

    @staticmethod
    def set_fan_speed(speed):
        with Kraken._devlock:
            if Kraken._dev is not None:
                Kraken._dev.write(0x01, [0x02, 0x4d, 0x00, 0x00, speed])

    @staticmethod
    def set_pump_speed(speed):
        with Kraken._devlock:
            if Kraken._dev is not None:
                Kraken._dev.write(0x01, [0x02, 0x4d, 0x40, 0x00, speed])

    @staticmethod
    def dispose():
        with Kraken._devlock:
            if Kraken._dev is not None:
                usb.util.dispose_resources(Kraken._dev)
                Kraken._dev = None

    @staticmethod
    def _read_status():
        # Limit the number of usb read requests
        if (datetime.now() - Kraken._last_update_time).total_seconds() >= Kraken._read_interval:
            Kraken._status = Kraken._dev.read(0x81, 64)
            Kraken._last_update_time = datetime.now()
        return Kraken._status
