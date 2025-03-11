from time import sleep
import bleson
from bleson import get_default_adapter, Peripheral, Service, Characteristic, CHAR_WRITE

bleson.set_use_descriptors(True)

adapter = get_default_adapter()

peripheral = Peripheral(adapter)

MICROBIT_LED_SERVICE = "0000dfb0-0000-1000-8000-00805f9b34fb"
MICROBIT_LED_CHAR = "0000dfb1-0000-1000-8000-00805f9b34fb"

def on_data_received(bytes):
    print(bytes)

led_service = Service(MICROBIT_LED_SERVICE)
led_write_char = Characteristic(MICROBIT_LED_CHAR, CHAR_WRITE)
led_write_char.on_data_received = on_data_received

led_service.add_characteristic(led_write_char)

peripheral.add_service(led_service)

peripheral.start()
sleep(2)
peripheral.stop()