import json
import multiprocessing as mp
import numpy as np
import time
from bluepy import btle         # pip install bluepy: src - https://ianharvey.github.io/bluepy-doc/, requires - mac / linux
from collections import deque
from EvalRelayClient import relay_client_process
# from pynput import keyboard     # pip install pynput: src - https://pypi.org/project/pynput/
from queue import Full, Empty

# Constants
BLE_TIMEOUT = 0.1                                               # threshold, in s
BLE_SVC_VENDOR_SPEC = "0000dfb0-0000-1000-8000-00805f9b34fb"    # Handle: 35
BLE_CHR_SERIAL = "0000dfb1-0000-1000-8000-00805f9b34fb"         # Handle: 36
P1_MAC_ADDR = ["B4:99:4C:89:19:8F", "34:08:E1:2A:29:6C", "34:08:E1:2A:24:94", "34:08:E1:2A:24:D1"]
P2_MAC_ADDR = ["34:08:E1:2A:1C:54", "34:08:E1:2A:24:C5", "34:08:E1:2A:24:D6", "50:65:83:77:57:EB"]
MPU_CYCLE_DELAY = 32
MPU_CYCLE_TIME = 0.035
GLOVE_PACKET_PREAMBLE = 0xaa
GLOVE_PACKET_LEN = 17
GUN_PACKET_LEN = 5
VEST_PACKET_LEN = 5

# Global Variables
beetles_to_relay_queue = mp.Queue()
relay_to_beetles_queue = mp.Queue()

# For Data Collection - TODO: walk, logout, boxing, fencing, golf, badminton, reload, bomb, shield
__data_collect__ = True
__json_name__ = "action_name.json"


# Interface with External Comms
def relay_main():
    # num_players = int(input("Enter the number of players: "))
    # server_ip = input("Enter the server ip: ")
    # if server_ip == "u96":
    server_ip = "172.26.191.109"
    SEND_PORT = 8000
    RECV_PORT = 8080

    try:
        send_thread = mp.Process(target=relay_client_process, args=(server_ip, SEND_PORT, beetles_to_relay_queue))
        recv_thread = mp.Process(target=relay_client_process, args=(server_ip, RECV_PORT, relay_to_beetles_queue))

        send_thread.start()
        send_thread.join()
        recv_thread.start()
        recv_thread.join()

    except KeyboardInterrupt:
        print("Exiting")
        send_thread.terminate()
        recv_thread.terminate()


# Calculates CRC24 using a linear shift register, ref: Bluetooth Core Specifications 6.0
def crc(crcdata):
    crcinit = [0x55, 0x55, 0x55]
    for crcbyte in crcdata:
        for i in range(8):
            shiftbit = (crcinit[2] >> 7) ^ ((crcbyte >> i) & 0x1)
            crcinit[2] <<= 1
            if crcinit[1] & 0x80: crcinit[2] |= 0x01
            crcinit[1] <<= 1
            if crcinit[0] & 0x80: crcinit[1] |= 0x01
            crcinit[0] <<= 1
            if shiftbit:
                crcinit[0] ^= 0x5B
                crcinit[1] ^= 0x06
            crcinit[0] &= 0xFF
            crcinit[1] &= 0xFF
            crcinit[2] &= 0xFF
    return crcinit


def main():
    # temp1 = BLEPlayer(1)
    temp2 = BLEPlayer(2)
    # relay_main()
    while True: pass


# Classes
class GloveDelegate(btle.DefaultDelegate):
    def __init__(self, rx_buffer_: deque):
        btle.DefaultDelegate.__init__(self)
        self.rx_buffer = rx_buffer_

    def handleNotification(self, cHandle, data):
        # dispose front byte if preamble check fail
        while self.rx_buffer and self.rx_buffer[0] != GLOVE_PACKET_PREAMBLE:
            self.rx_buffer.popleft()
        if cHandle == 37 and (len(list(data)) + len(self.rx_buffer) <= self.rx_buffer.maxlen):
            for data_byte in list(data):
                self.rx_buffer.append(data_byte)
        # print(f"Received {list(data)} from glove, buffer has {len(self.rx_buffer)} bytes")

class GunDelegate(btle.DefaultDelegate):
    def __init__(self, rx_buffer_: deque):
        btle.DefaultDelegate.__init__(self)
        self.rx_buffer = rx_buffer_

    def handleNotification(self, cHandle, data):
        if cHandle == 37 and (len(list(data)) + len(self.rx_buffer) <= self.rx_buffer.maxlen):
            for data_byte in list(data):
                self.rx_buffer.append(data_byte)
        # print(f"Received {list(data)} from gun, buffer has {len(self.rx_buffer)} bytes")

class VestDelegate(btle.DefaultDelegate):
    def __init__(self, rx_buffer_: deque):
        btle.DefaultDelegate.__init__(self)
        self.rx_buffer = rx_buffer_

    def handleNotification(self, cHandle, data):
        if cHandle == 37 and (len(list(data)) + len(self.rx_buffer) <= self.rx_buffer.maxlen):
            for data_byte in list(data):
                self.rx_buffer.append(data_byte)
        # print(f"Received {list(data)} from vest, buffer has {len(self.rx_buffer)} bytes")

class BLEPlayer:
    def __init__(self, playerID):
        # BLE Management Vars
        self.mpuDataSync = [mp.RLock(), mp.RLock(), mp.RLock()]
        self.macAddrList = P1_MAC_ADDR if (playerID == 1) else P2_MAC_ADDR
        self.connStatus = [mp.Value('i', 0), mp.Value('i', 0), mp.Value('i', 0), mp.Value('i', 0)]

        # Player State Vars
        ## Server-side
        self.playerID = playerID
        self.serverHP = mp.Value('i', 100)
        self.beetleHP = mp.Value('i', 100)
        self.serverBullets = mp.Value('i', 6)
        self.beetleBullets = mp.Value('i', 6)
        ## Beetle-side
        self.rGloveActionStart = mp.Value('i', 0)
        self.lGloveActionStart = mp.Value('i', 0)
        self.rGloveMPU = mp.Queue(64)
        self.lGloveMPU = mp.Queue(64)
        self.vestMPU = mp.Queue(64)
        self.irDetected = mp.Value('i', 0)
        self.gunFired = mp.Value('i', 0)

        # BLE Handling Processes
        self.rgProcess = mp.Process(target=self.gloveBLE, args=(self.connStatus[0], self.macAddrList[0], self.mpuDataSync[0], self.rGloveActionStart, self.rGloveMPU))
        self.lgProcess = mp.Process(target=self.gloveBLE, args=(self.connStatus[1], self.macAddrList[1], self.mpuDataSync[1], self.lGloveActionStart, self.lGloveMPU))
        self.gunProcess = mp.Process(target=self.gunBLE, args=(self.connStatus[2], self.macAddrList[2], self.serverBullets, self.beetleBullets, self.gunFired))
        self.vestProcess = mp.Process(target=self.vestBLE, args=(self.connStatus[3], self.macAddrList[3], self.serverHP, self.beetleHP, self.irDetected))    # , self.mpuDataSync[2], self.vestMPU
        self.mainProcess = mp.Process(target=self.run)
        # Beetle update tokens
        self.gunProcess.updateBtle = mp.Event()
        self.vestProcess.updateBtle = mp.Event()
        # Process exit tokens
        self.rgProcess.exit = mp.Event()
        self.lgProcess.exit = mp.Event()
        self.gunProcess.exit = mp.Event()
        self.vestProcess.exit = mp.Event()
        self.isProgramActive = mp.Value('b', 1)  # Exit token for data handling process

        self.rgProcess.start()
        self.lgProcess.start()
        self.gunProcess.start()
        self.vestProcess.start()
        self.mainProcess.start()

    def __del__(self):
        self.rgProcess.exit.set()
        self.lgProcess.exit.set()
        self.gunProcess.exit.set()
        self.vestProcess.exit.set()
        self.isProgramActive.value = 0
        print("Terminating BLE Processes...")
        self.rgProcess.join()
        self.lgProcess.join()
        self.gunProcess.join()
        self.vestProcess.join()
        self.mainProcess.join()
        print(f"Player {self.playerID} BLE Terminated")

    def run(self):
        tLastParse = 0
        dataCycleLatency = 0
        actionCD = time.time()
        prevGunFired = 0
        playerMpuData = []
        dataCollect = [] if __data_collect__ else None
        
        while self.isProgramActive.value:
            if time.time() - tLastParse > MPU_CYCLE_TIME:       # Run every interval of expected packet
                tLastParse = time.time()
                readGunFired = self.gunFired.value              # Format Dictionary for JSON conversion
                gameData = {
                    'player_id':self.playerID,
                    'gun_fired':(prevGunFired != readGunFired), # boolean
                    'IR_Sensor':self.irDetected.value,          # ctypes.c_int
                    'imu_data':[]                               # empty if no action detected, else 64 frames of MPU data
                }
                if prevGunFired != readGunFired:                # update history value if changed
                    prevGunFired = readGunFired
                
                readRAS = self.rGloveActionStart.value
                readLAS = self.lGloveActionStart.value
                startDataCollect = (readRAS == 1 or readLAS == 1) and dataCycleLatency == 0 and (time.time() - actionCD > 4)
                if startDataCollect or 0 < dataCycleLatency < MPU_CYCLE_DELAY:
                    if dataCycleLatency == 0:
                        actionCD = time.time()
                        print(f"Player {self.playerID}: action detected\n")
                    dataCycleLatency += 1
                if dataCycleLatency == MPU_CYCLE_DELAY:
                    with self.mpuDataSync[0]:
                        while len(playerMpuData) < 64:
                            try:
                                playerMpuData.append(self.rGloveMPU.get_nowait())
                            except Empty:
                                playerMpuData.append([0] * 6)
                                # print("debug: access error")
                    with self.mpuDataSync[1]:
                        for dataEntry in playerMpuData:
                            try:
                                dataEntry.extend(self.lGloveMPU.get_nowait())
                            except Empty:
                                dataEntry.extend([0] * 6)
                                # print("debug: access error")
                    # with self.mpuDataSync[2]:
                    #     for dataEntry in playerMpuData:
                    #         try:
                    #             dataEntry.extend(self.vestMPU.get_nowait())
                    #         except Empty:
                    #             dataEntry.extend([0] * 6)
                                # print("debug: access error")
                    gameData["imu_data"].extend(playerMpuData)
                    if dataCollect is not None:
                        dataCollect.append(playerMpuData.copy())
                        with open(__json_name__, "w") as outfile:
                            json.dump(dataCollect, outfile)
                    playerMpuData.clear()
                    dataCycleLatency = 0
                    beetles_to_relay_queue.put(json.dumps(gameData))
                elif gameData["gun_fired"] == True or gameData["IR_Sensor"] != 0:
                    beetles_to_relay_queue.put(json.dumps(gameData))

                if self.playerID == 2:
                    updateStr = f'Player {self.playerID}: connStatus (r - {self.connStatus[0].value}, l - {self.connStatus[1].value}, g - {self.connStatus[2].value}, v - {self.connStatus[3].value}), ready - {(time.time() - actionCD > 5)}'
                    if dataCollect is not None:
                        updateStr += f', nSets - {len(dataCollect)}'
                    print(f'{updateStr:>100}', end='\r')
    
    def ble_send(self, chrObj, header, serverData):
        """
        chrObj - Bluepy Characteristic Object: used for chrObj.write()\n
        header - Reserved (4 bits), SYN, RST, ACK, NACK\n
        serverData - nBullets / HP from server
        """
        payload = [header, serverData]
        payload.extend(crc(payload))
        for payload_byte in payload:
            chrObj.write(int.to_bytes(payload_byte))
        return payload

    def ble_retransmit(self, chrObj, tx_buffer):
        for payload_byte in tx_buffer:
            chrObj.write(int.to_bytes(payload_byte))
    
    def updateBullets(self, nBullets):
        self.serverBullets = nBullets
        self.gunProcess.updateBtle.set()

    def updateHP(self, nHP):
        self.serverHP = nHP
        self.vestProcess.updateBtle.set()

    # BLE process loop for gloves
    def gloveBLE(self, connStatus, ble_addr, mpuDataSync, actionStart, mpuData: mp.Queue):
        while not mp.current_process().exit.is_set():
            try:
                rx_buffer = deque(maxlen=GLOVE_PACKET_LEN * 6)
                device = btle.Peripheral(ble_addr)
                device.setDelegate(GloveDelegate(rx_buffer))

                # main event loop, no handshake
                connStatus.value = 1
                while not mp.current_process().exit.is_set():
                    if device.waitForNotifications(0.1) and len(rx_buffer) >= GLOVE_PACKET_LEN:
                        while len(rx_buffer) >= GLOVE_PACKET_LEN:
                            rx_packet = list()
                            for i in range(GLOVE_PACKET_LEN):
                                rx_packet.append(rx_buffer.popleft())
                            if crc(rx_packet[0:14]) == rx_packet[14:17]:
                                try:
                                    if mpuDataSync.acquire(block=False):
                                        if mpuData.full():
                                            mpuData.get()
                                        mpuData.put_nowait([np.int16(np.uint16(rx_packet[1] | rx_packet[2] << 8)).item(), np.int16(np.uint16(rx_packet[3] | rx_packet[4] << 8)).item(), np.int16(np.uint16(rx_packet[5] | rx_packet[6] << 8)).item(), np.int16(np.uint16(rx_packet[7] | rx_packet[8] << 8)).item(), np.int16(np.uint16(rx_packet[9] | rx_packet[10] << 8)).item(), np.int16(np.uint16(rx_packet[11] | rx_packet[12] << 8)).item()])
                                        mpuDataSync.release()
                                except Full:
                                    pass
                                actionStart.value = (rx_packet[13] != 0)
                device.disconnect()
            except btle.BTLEException as e:
                # print(e)
                pass
            except Exception as e:
                # print(e)
                pass
            finally:
                device = None
                connStatus.value = 0

    # BLE process loop for gun
    def gunBLE(self, connStatus, ble_addr, nBulletsSvr, nBulletsBtle, isGunFired):
        while not mp.current_process().exit.is_set():
            device = btle.Peripheral()
            try:
                # BLE Setup
                rx_buffer = deque(maxlen=GUN_PACKET_LEN * 6)
                device.connect(ble_addr)
                device.setDelegate(GunDelegate(rx_buffer))
                serial_chr = device.getServiceByUUID(BLE_SVC_VENDOR_SPEC).getCharacteristics(BLE_CHR_SERIAL)[0]
                retransmit_count = 0
                
                # handshake loop
                handshakeInProg = True
                while handshakeInProg:
                    self.ble_send(serial_chr, 0x08, nBulletsSvr.value)    # periodically send SYN
                    if device.waitForNotifications(1) and len(rx_buffer) >= GUN_PACKET_LEN:
                        rx_packet = list()
                        for i in range(GUN_PACKET_LEN):
                            rx_packet.append(rx_buffer.popleft())
                        while len(rx_buffer) > 0:
                            if rx_packet[0] == 0x0a and crc(rx_packet[0:2]) == rx_packet[2:5]:
                                handshakeInProg = False             # SYN_ACK received, exit loop
                                retransmit_count = 0
                                rx_buffer.clear()
                            else:
                                rx_packet.pop(0)
                                rx_packet.append(rx_buffer.popleft())
                    if handshakeInProg:
                        if retransmit_count == 3:
                            self.ble_send(serial_chr, 0x04, nBulletsSvr.value)
                            device.disconnect()
                            raise Exception("BLE device disconnected during handshake")
                        retransmit_count += 1
                        time.sleep(0.1)
                self.ble_send(serial_chr, 0x02, nBulletsSvr.value)        # send ACK
                retransmit_count = 0

                # main event loop
                tx_buffer = None
                tx_millis = 0
                last_tx = 0
                connStatus.value = 1
                while not mp.current_process().exit.is_set():
                    # Process incoming packets
                    if device.waitForNotifications(0.1) and len(rx_buffer) >= GUN_PACKET_LEN:
                        while len(rx_buffer) > 0 and (rx_packet[0] >> 4) != 0:
                            rx_packet.pop(0)
                            rx_packet.append(rx_buffer.popleft())
                        while len(rx_buffer) >= GUN_PACKET_LEN:
                            rx_packet = list()
                            for i in range(GUN_PACKET_LEN):
                                rx_packet.append(rx_buffer.popleft())
                            if (rx_packet[0] >> 4) == 0 and crc(rx_packet[0:2]) == rx_packet[2:5]:
                                # parse payload data
                                nBulletsBtle.value = rx_packet[1] >> 4
                                isGunFired.value = rx_packet[1] & 1
                                
                                # parse header
                                match rx_packet[0]:
                                    case 0x01:  # NACK, retransmit packet
                                        self.ble_retransmit(serial_chr, tx_buffer)
                                        tx_millis = time.time()
                                        retransmit_count += 1
                                    case 0x02:  # ACK
                                        tx_buffer = None
                                        tx_millis = 0
                                        retransmit_count = 0
                                    case 0x04:  # RST
                                        # print("Resetting connection")
                                        device.disconnect()
                                        raise Exception("RST: BLE device disconnected")
                                    case 0x0a:  # SYN_ACK
                                        self.ble_send(serial_chr, 0x02, nBulletsSvr.value)
                                        last_tx = time.time()
                                    case 0x00: # ACK required (gun fired)
                                        self.ble_send(serial_chr, 0x02, nBulletsSvr.value)
                                        last_tx = time.time()
                    
                    # Retransmit on timeout (or disconnect after 5 retransmits)
                    if tx_millis > 0 and (time.time() - tx_millis > BLE_TIMEOUT):
                        last_tx = time.time()
                        if retransmit_count < 5:
                            self.ble_retransmit(serial_chr, tx_buffer)
                            tx_millis = time.time()
                            retransmit_count += 1
                        else:
                            self.ble_send(serial_chr, 0x04, nBulletsSvr.value)
                            break
                    
                    # Update gun's nBullets
                    if tx_millis == 0 and tx_buffer == None and mp.current_process().updateBtle.is_set():
                        mp.current_process().updateBtle.clear()
                        tx_buffer = self.ble_send(serial_chr, 0x00, nBulletsSvr.value)
                        tx_millis = time.time()
                        last_tx = time.time()

                    # Upkeep active BLE connection
                    if time.time() - last_tx > 0.1:
                        self.ble_send(serial_chr, 0x08, nBulletsSvr.value)
                        self.ble_send(serial_chr, 0x02, nBulletsSvr.value)
                        last_tx = time.time()
                device.disconnect()
            except btle.BTLEException as e:
                # print(e)
                pass
            except Exception as e:
                # print(e)
                pass
            finally:
                if device is not None:
                    device.disconnect()
                    device = None
                connStatus.value = 0

    # BLE process loop for vest
    def vestBLE(self, connStatus, ble_addr, nHPSvr, nHPBtle, irDetected, mpuDataSync = None, mpuData: mp.Queue = None):
        while not mp.current_process().exit.is_set():
            device = btle.Peripheral()
            try:
                # BLE Setup
                rx_buffer = deque(maxlen=VEST_PACKET_LEN * 6)
                device.connect(ble_addr)
                device.setDelegate(VestDelegate(rx_buffer))
                serial_chr = device.getServiceByUUID(BLE_SVC_VENDOR_SPEC).getCharacteristics(BLE_CHR_SERIAL)[0]
                retransmit_count = 0
                
                # handshake loop
                connStatus.value = 1
                handshakeInProg = True
                while handshakeInProg:
                    self.ble_send(serial_chr, 0x08, nHPSvr.value)    # periodically send SYN
                    if device.waitForNotifications(1) and len(rx_buffer) >= VEST_PACKET_LEN:
                        rx_packet = list()
                        for i in range(VEST_PACKET_LEN):
                            rx_packet.append(rx_buffer.popleft())
                        while len(rx_buffer) > 0:
                            if rx_packet[0] == 0x0a and crc(rx_packet[0:-3]) == rx_packet[-3:]:
                                handshakeInProg = False             # SYN_ACK received, exit loop
                                retransmit_count = 0
                                rx_buffer.clear()
                            else:
                                rx_packet.pop(0)
                                rx_packet.append(rx_buffer.popleft())
                    if handshakeInProg:
                        if retransmit_count == 3:
                            self.ble_send(serial_chr, 0x04, nHPSvr.value)
                            device.disconnect()
                            raise Exception("BLE device disconnected during handshake")
                        retransmit_count += 1
                        time.sleep(0.1)
                self.ble_send(serial_chr, 0x02, nHPSvr.value)        # send ACK
                retransmit_count = 0

                # main event loop
                tx_buffer = None
                tx_millis = 0
                last_tx = 0
                connStatus.value = 1
                while not mp.current_process().exit.is_set():
                    # Process incoming packets
                    if device.waitForNotifications(0.1) and len(rx_buffer) >= VEST_PACKET_LEN:
                        while len(rx_buffer) > 0 and (rx_packet[0] >> 4) != 0:
                            rx_packet.pop(0)
                            rx_packet.append(rx_buffer.popleft())
                        while len(rx_buffer) >= VEST_PACKET_LEN:
                            rx_packet = list()
                            for i in range(VEST_PACKET_LEN):
                                rx_packet.append(rx_buffer.popleft())
                            if (rx_packet[0] >> 4) == 0 and crc(rx_packet[0:-3]) == rx_packet[-3:]:
                                # parse payload data
                                nHPBtle.value = rx_packet[1] >> 1
                                irDetected.value = rx_packet[1] & 1
                                
                                # parse header
                                match rx_packet[0]:
                                    case 0x01:  # NACK, retransmit packet
                                        self.ble_retransmit(serial_chr, tx_buffer)
                                        tx_millis = time.time()
                                        retransmit_count += 1
                                    case 0x02:  # ACK
                                        tx_buffer = None
                                        tx_millis = 0
                                        retransmit_count = 0
                                    case 0x04:  # RST
                                        # print("Resetting connection")
                                        device.disconnect()
                                        raise Exception("RST: BLE device disconnected")
                                    case 0x0a:  # SYN_ACK
                                        self.ble_send(serial_chr, 0x02, nHPSvr.value)
                                        last_tx = time.time()
                                    case 0x00: # ACK required (gun fired)
                                        self.ble_send(serial_chr, 0x02, nHPSvr.value)
                                        last_tx = time.time()
                    
                    # Retransmit on timeout (or disconnect after 5 retransmits)
                    if tx_millis > 0 and (time.time() - tx_millis > BLE_TIMEOUT):
                        last_tx = time.time()
                        if retransmit_count < 5:
                            self.ble_retransmit(serial_chr, tx_buffer)
                            tx_millis = time.time()
                            retransmit_count += 1
                        else:
                            self.ble_send(serial_chr, 0x04, nHPSvr.value)
                            break
                    
                    # Update gun's nBullets
                    if tx_millis == 0 and tx_buffer == None and mp.current_process().updateBtle.is_set():
                        mp.current_process().updateBtle.clear()
                        tx_buffer = self.ble_send(serial_chr, 0x00, nHPSvr.value)
                        tx_millis = time.time()
                        last_tx = time.time()

                    # Upkeep active BLE connection
                    if time.time() - last_tx > 0.1:
                        self.ble_send(serial_chr, 0x08, nHPSvr.value)
                        self.ble_send(serial_chr, 0x02, nHPSvr.value)
                        last_tx = time.time()
                device.disconnect()
            except btle.BTLEException as e:
                # print(e)
                pass
            except Exception as e:
                # print(e)
                pass
            finally:
                if device is not None:
                    device.disconnect()
                    device = None
                connStatus.value = 0


if __name__ == "__main__":
    main()


# Packet Formats (from LSByte / MSBit):
## Glove to Relay: 17 bytes
    # 1 byte preamble
    # 12 bytes mpuData
    # 1 byte actionStart
    # 3 bytes CRC
## Gun to Relay: 5 bytes
    # 1 byte header (Reserved - 4 bits, SYN, RST, ACK, NACK)
    # 1 byte data (nBulletsBtle - 4 bits, reserved - 3 bits cleared, isGunFired - 1 bit)
    # 3 bytes CRC
## Vest to Relay: 17 bytes
    # 1 byte header (Reserved - 4 bits, SYN, RST, ACK, NACK)
    # 12 bytes mpuData  (TODO: Existance is TBC)
    # 1 byte data (health - 7 bits, irDetected - 1 bit)
    # 3 bytes CRC
## Relay to Gun / Vest: 5 bytes
    # 1 byte header (Reserved - 4 bits, SYN, RST, ACK, NACK)
    # 1 byte nBulletsSvr / serverHP
    # 3 bytes CRC


# Debug BLE: sudo btmon -i hci0