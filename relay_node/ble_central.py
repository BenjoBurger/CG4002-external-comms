from bluepy import btle         # pip install bluepy: src - https://ianharvey.github.io/bluepy-doc/, requires - mac / linux
import multiprocessing as mp
import time
# from pynput import keyboard     # pip install pynput: src - https://pypi.org/project/pynput/
from collections import deque
import json

from EvalRelayClient import relay_client_process

# BLE GATT constants:
BLE_TIMEOUT = 0.1                                               # threshold, in s
BLE_SVC_VENDOR_SPEC = "0000dfb0-0000-1000-8000-00805f9b34fb"    # Handle: 35
BLE_CHR_SERIAL = "0000dfb1-0000-1000-8000-00805f9b34fb"         # Handle: 36
BITS_PER_PACKET = 96
bleDispatcher = [None, None]

beetles_to_relay_queue = None
relay_to_beetles_queue = None

def connectBeetles():
    def playerProcessDispatch(pID):
        blePlayerList = BLEPlayer(pID)
        blePlayerList.run()
        while not mp.current_process().exit.is_set(): pass
        blePlayerList.stop()

    bleDispatcher[0] = mp.Process(target=playerProcessDispatch, args=([1]))
    bleDispatcher[1] = mp.Process(target=playerProcessDispatch, args=([2]))   # TODO: comment out if only 1 player
    if bleDispatcher[0] is not None:
        bleDispatcher[0].exit = mp.Event()
        bleDispatcher[0].start()
    if bleDispatcher[1] is not None:
        bleDispatcher[1].exit = mp.Event()
        bleDispatcher[1].start()

def disconnectBeetles():
    print(f"Disconnecting BLE")
    if bleDispatcher[0] is not None:
        bleDispatcher[0].exit.set()
        bleDispatcher[0].join()
    if bleDispatcher[1] is not None:
        bleDispatcher[1].exit.set()
        bleDispatcher[1].join()
    print(f"BLE stopped")

#benjamin
def relay_main():
    server_ip = input("Enter the server ip: ")
    if server_ip == "u96":
        server_ip = "172.26.190.163"

    try:
        beetles_to_relay_queue = mp.Queue()
        relay_to_beetles_queue = mp.Queue()

        relay_thread = mp.Process(target=relay_client_process, args=(server_ip, beetles_to_relay_queue, relay_to_beetles_queue))
        
        relay_thread.start()
        relay_thread.join()

    except KeyboardInterrupt:
        print("Exiting")
        relay_thread.terminate()

def receive_from_relay():
    while True:
        if not relay_to_beetles_queue.empty():
            data = relay_to_beetles_queue.get()
            print(f"Data received: {data}", end="\n\n")

# Main synchronous function, for easier integration with External Comms components
def main():
    connectBeetles()
    relay_main()
    disconnectBeetles()
    # player1_BLE = BLEPlayer(1)
    # player2_BLE = BLEPlayer(2)

    # def keyPress(key):
    #     if key == keyboard.Key.space:
    #         player1_BLE.stop()
    #         # player2_BLE.stop()

    # listener = keyboard.Listener(on_press=keyPress)
    # listener.start()
    # player1_BLE.run()
    # player2_BLE.run()

## Classes:
class BLEDelegate(btle.DefaultDelegate):
    def __init__(self, rx_buffer_):
        btle.DefaultDelegate.__init__(self)
        self.rx_buffer = rx_buffer_

    def handleNotification(self, cHandle, data):
        # if random.random() < 0.1:   # Demo: 10% random drop
        #     return
        # data = random_corrupt(data) # Demo: 10% random corrupt
        # print(f"Received {list(data)} from handle: {cHandle}")
        if cHandle == 37:
            if len(list(data)) < 20:
                return
            for data_byte in list(data):
                self.rx_buffer.append(data_byte)

class BLEPlayer(object):
    def __init__(self, playerID):
        self.playerID = playerID
        # Beetle MAC addresses per player (right, left , gun, vest)
        if playerID == 1:
            MAC_ADDR_LIST = ["B4:99:4C:89:19:8F", "34:08:E1:2A:29:6C", "34:08:E1:2A:24:94", "34:08:E1:2A:24:D1"]
        else:
            MAC_ADDR_LIST = ["50:65:83:77:57:EB", "34:08:E1:2A:24:D6", "", ""]   # TODO: get MAC addresses for player2
        self.isProgramActive = mp.Value('b', 1)  # Program terminates after setting to 0 and disconnecting all beetles
        # Interface from game engine to beetle
        self.btleCommandDict = { "rGlove":mp.Array('i', [0] * 16), "lGlove":mp.Array('i', [0] * 16), "gun":mp.Array('i', [0] * 16), "vest":mp.Array('i', [0] * 16) }
        
        # Right Glove Data
        self.rGloveMPU = mp.Array('i', [0] * 6)
        self.rGloveActionStart = mp.Value('i', 0)
        # Left Glove Data
        self.lGloveMPU = mp.Array('i', [0] * 6)
        self.lGloveActionStart = mp.Value('i', 0)
        # Vest Data
        self.health = mp.Value('i', 100)
        self.vestMPU = mp.Array('i', [0] * 6)
        self.IR_Sensor = mp.Value('i', 0)
        # Gun Data
        self.nBullets = mp.Value('i', 6)
        self.gunshotFlag = mp.Value('i', 0)

        # State data history
        self.prevGunFlag = 0
        self.prevRActionStart = 0
        self.prevLActionStart = 0
        self.mpuData = []

        # BLE Connection Process Objects
        self.rgProcess = mp.Process(target=self.ble_peri, args=(MAC_ADDR_LIST[0], self.btleCommandDict["rGlove"], self.rGloveActionStart, self.rGloveMPU))
        self.lgProcess = mp.Process(target=self.ble_peri, args=(MAC_ADDR_LIST[1], self.btleCommandDict["lGlove"], self.lGloveActionStart, self.lGloveMPU))
        self.gunProcess = mp.Process(target=self.ble_peri, args=(MAC_ADDR_LIST[2], self.btleCommandDict["gun"], None, None, None, self.nBullets, self.gunshotFlag))
        self.vestProcess = mp.Process(target=self.ble_peri, args=(MAC_ADDR_LIST[3], self.btleCommandDict["vest"], None, self.vestMPU, self.health, None, None, self.IR_Sensor))

        # setup exit tokens
        self.rgProcess.exit = mp.Event()
        self.lgProcess.exit = mp.Event()
        self.gunProcess.exit = mp.Event()
        self.vestProcess.exit = mp.Event()

    def run(self):
        self.rgProcess.start()
        self.lgProcess.start()
        self.gunProcess.start()
        self.vestProcess.start()
        
        updateStr = f''
        while self.isProgramActive.value:
            tempFlag = self.gunshotFlag.value
            gameData = {
                'health':self.health.value, # ctypes.c_int
                'bullets':self.nBullets.value, # ctypes.c_int
                'gunFired':(self.prevGunFlag != tempFlag), # boolean
                'IR_Sensor':self.IR_Sensor.value # ctypes.c_int
            }
            if self.prevGunFlag != tempFlag:
                self.prevGunFlag = tempFlag
            with open("gameData.json", "w") as outfile:
                json.dump(gameData, outfile)

            tempRAS = self.rGloveActionStart.value
            tempLAS = self.lGloveActionStart.value
            startDataCollect = (tempRAS != self.prevRActionStart or tempLAS != self.prevLActionStart) and len(self.mpuData) == 0
            self.prevRActionStart = tempRAS
            self.prevLActionStart = tempLAS
            playerMPUFrame = []
            playerMPUFrame.extend(self.rGloveMPU)
            playerMPUFrame.extend(self.lGloveMPU)
            playerMPUFrame.extend(self.vestMPU)
            if startDataCollect or 0 < len(self.mpuData) < 64:
                self.mpuData.append(playerMPUFrame)
            if len(self.mpuData) == 64:
                with open("mpuData.json", "w") as outfile:
                    json.dump(self.mpuData, outfile)
                    beetles_to_relay_queue(json.dumps(gameData))
                self.mpuData.clear()

            if self.playerID == 1:
                updateStr = f'Player {self.playerID}: mpuData - {playerMPUFrame}, gameData - {gameData}'
                print(f'{updateStr:>200}', end='\r')
            # if gameData["IR_Sensor"]:
            #     print("passed\n")
            time.sleep(0.025)

        self.rgProcess.join()
        self.lgProcess.join()
        self.gunProcess.join()
        self.vestProcess.join()

    def stop(self):
        self.isProgramActive.value = 0
        self.rgProcess.exit.set()
        self.lgProcess.exit.set()
        self.gunProcess.exit.set()
        self.vestProcess.exit.set()
    
    def reload(self):
        self.btleCommandDict["gun"][1] = 0xff

    # Implements an instance of BLE connection to a peripheral Bluno
    def ble_peri(self, ble_addr, btleTxPayloadDict, actionStart=None, mpuData=None, health=None, nBullets=None, gunshotFlag=None, IR_Sensor=None):
        # Calculates CRC24 for a list of byte-sized elements
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

        # Creates a packet using a single byte header object input, and transmits the 20-byte packet using bluepy.btle.characteristic.write()
        # Returns a list of byte elements of 20-byte packet transmited
        def ble_send(header, chrObj):
            with btleTxPayloadDict.get_lock():
                cmd_data = btleTxPayloadDict
            payload = [header]
            payload.extend(cmd_data)   # Get LED and gameCMD data
            payload.extend(crc(payload))    # Appending CRC24 value to header byte and 16-byte payload
            # print(f"debug log: sending {payload} to {chrObj.peripheral.addr}")                                                        # Demo: log packet sent
            # print(f"sending {payload} to {chrObj.peripheral.addr}", file=open(LOG_FILE_DICT[chrObj.peripheral.addr], 'a'))
            for payload_byte in payload:
                chrObj.write(int.to_bytes(payload_byte))
            return payload
        
        # Writes an existing 20-byte packet (tx_buffer) to a bluepy characteristic object (chrObj)
        def ble_retransmit(tx_buffer, signalStop, chrObj):
            # print(f"debug log: retransmit packet to {chrObj.peripheral.addr}")                                                        # Demo: log packet retransmit
            payload = tx_buffer[0:16]
            payload[0] |= signalStop
            payload.extend(crc(payload))
            # print(f"retransmit {tx_buffer} to {chrObj.peripheral.addr}", file=open(LOG_FILE_DICT[chrObj.peripheral.addr], 'a'))
            for payload_byte in tx_buffer:
                chrObj.write(int.to_bytes(payload_byte))

        while not mp.current_process().exit.is_set():
            # setup
            nCorrupt = 0
            rx_buffer = deque(maxlen=100)
            retransmit_count = 0
            tx_buffer = None
            tx_millis = 0
            isCMDPending = 0
            signalStop = 0
            
            try:
                device = btle.Peripheral(ble_addr)
                device.setDelegate(BLEDelegate(rx_buffer))
                serial_chr = device.getServiceByUUID(BLE_SVC_VENDOR_SPEC).getCharacteristics(BLE_CHR_SERIAL)[0]

                # handshake loop
                while True: 
                    ble_send(0x08 | signalStop, serial_chr)  # periodically resend SYN
                    if device.waitForNotifications(1):
                        if len(rx_buffer) > 19:
                            rx_packet = list()
                            for i in range(20):
                                rx_packet.append(rx_buffer.popleft())
                            if rx_packet[0] == 0x0a and crc(rx_packet[0:17]) == rx_packet[17:20]:
                                break   # stop periodic SYN once verified SYN_ACK received
                    
                    if retransmit_count == 3:
                        device.disconnect()
                        raise Exception("BLE device disconnected")
                    retransmit_count += 1
                    time.sleep(0.1)
                ble_send(0x02 | signalStop, serial_chr)  # complete handshake, ACK
                retransmit_count = 0

                # main event loop
                while True:
                    # Set stop_and_wait signal based on available rx_buffer space
                    if (len(rx_buffer) >= 80 or isCMDPending != 0) and signalStop == 0:
                        signalStop = 0xf0
                    if len(rx_buffer) <= 20 and signalStop != 0 and isCMDPending == 0:
                        signalStop = 0
                    
                    if device.waitForNotifications(1) and len(rx_buffer) > 19:
                        rx_packet = list()
                        for i in range(20):
                            rx_packet.append(rx_buffer.popleft())   # move complete packet from incoming buffer for processing
                        # print(f"recieved {rx_packet} from {device.addr}", file=open(LOG_FILE_DICT[device.addr], 'a'))                                  # Demo: log received packet
                        if crc(rx_packet[0:17]) == rx_packet[17:20]:    # check crc of packet
                            # parse payload data
                            # if (gunshotFlag != (rx_packet[15] & 1)):
                            #     temp = ' '
                            #     print(f'{temp:>200}', end='\r')
                            #     print(f'gun fired from address: {device.addr}, {rx_packet[15] >> 4} bullets left') # Demo: show gunshot receipt
                            if mpuData is not None:
                                mpuData[0] = rx_packet[1] | rx_packet[2] << 8
                                mpuData[1] = rx_packet[3] | rx_packet[4] << 8
                                mpuData[2] = rx_packet[5] | rx_packet[6] << 8
                                mpuData[3] = rx_packet[7] | rx_packet[8] << 8
                                mpuData[4] = rx_packet[9] | rx_packet[10] << 8
                                mpuData[5] = rx_packet[11] | rx_packet[12] << 8
                            if actionStart is not None:
                                actionStart.value = rx_packet[13]
                            if health is not None:
                                health.value = rx_packet[14]
                            if nBullets is not None:
                                nBullets.value = rx_packet[15] >> 4
                            if gunshotFlag is not None:
                                gunshotFlag.value = rx_packet[15] & 1
                            if IR_Sensor is not None:
                                IR_Sensor.value = rx_packet[16]
                            
                            # parse header
                            match rx_packet[0]:
                                case 0x01:  # NACK, retransmit packet
                                    ble_retransmit(tx_buffer, signalStop, serial_chr)
                                    tx_millis = time.time()
                                    retransmit_count += 1
                                case 0x02:  # ACK
                                    tx_millis = 0
                                    retransmit_count = 0
                                case 0x04:  # RST
                                    # print("Resetting connection")
                                    break
                                case 0xf0:  # periodic notify
                                    continue
                                # case _: # ACK required (SYN_ACK, button press, IR receive, gunshot, health, start of motion)
                                #     # print("Bulno cmd or flag")
                                #     ble_send(0x02 | signalStop, serial_chr)
                                #     tx_millis = 0
                        else:
                            # corrupted or fragmented packet
                            if nCorrupt == 2:
                                rx_buffer.clear()
                                nCorrupt = 0
                            else:
                                nCorrupt += 1
                    
                    # react to data
                    if nBullets is not None:
                        if nBullets.value == 6 and btleTxPayloadDict[1] == 0xff and isCMDPending != 0:   # clear reload cmd
                            btleTxPayloadDict[1] = 0
                            isCMDPending = 0
                        if btleTxPayloadDict[1] == 0xff and isCMDPending == 0:   # send reload cmd
                            tx_buffer = ble_send(0xf0, serial_chr)
                            tx_millis = time.time()
                            isCMDPending = 1
                            # rx_buffer.clear()
                            # while True:
                            #     ble_send(0xf0, serial_chr)
                            #     if device.waitForNotifications(1):
                            #         if len(rx_buffer) > 19:
                            #             rx_packet = list()
                            #             for i in range(20):
                            #                 rx_packet.append(rx_buffer.popleft())
                            #             # print('\n')
                            #             # print(rx_packet)
                            #             if rx_packet[0] == 0x02 and crc(rx_packet[0:17]) == rx_packet[17:20]:
                            #                 break
                            #     if retransmit_count == 5:
                            #         device.disconnect()
                            #         raise Exception("BLE device disconnected")
                            #     retransmit_count += 1
                            # retransmit_count = 0
                            # btleTxPayloadDict[1] = 0
                    
                    # retransmit (or disconnect after 3 retransmits) on timeout
                    if tx_millis > 0 and (time.time() - tx_millis > BLE_TIMEOUT):
                        if retransmit_count < 20:
                            ble_retransmit(tx_buffer, signalStop, serial_chr)
                            tx_millis = time.time()
                            retransmit_count += 1
                        else:
                            ble_send(0x04 | signalStop, serial_chr)
                            break
                device.disconnect()
            except btle.BTLEException as e:
                # print(e)
                pass
            except Exception as e:
                # print(e.with_traceback())
                pass
            finally:
                device = None


## Payload Data Unit format (20 bytes, starting from least significant):
# header - 1 byte
    # periodic notify | signalStop - 4 bits
    # SYN, RST, ACK, NACK - 1 bit each
# payload - 16 bytes
    # from beetle:
        # accel{ x, y, z } - 6 bytes
        # gyro{ x, y, z } - 6 bytes

        # actionStart - 1 byte
        # health - 1 byte

        # nBullets - 4 bits
        # reserved - 3 bits cleared
        # gunshot flag - 1 bit

        # IR_rcv - 8 bit
    # from laptop: only read if SYN/RST/ACK/NACK flags are cleared
        # LED control - 1 byte
        # game engine cmd - 15 byte, clear header
            # reload cmd: [0xff, 0x00 * 14]
# CRC24 - 3 bytes


if __name__ == "__main__":
    main()
