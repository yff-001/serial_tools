import serial
import serial.tools.list_ports
import struct
import json
import time
import threading

class Arduino(serial.Serial):
    def __init__(self):
        super().__init__()
        try:
            for port in serial.tools.list_ports.comports():
                if port.pid == 0x7523 and port.vid == 0x1a86:
                    self.port = port.device
            self.baudrate = 115200
            self.timeout = 0.1
            self.open()
        except Exception as e:
            print(e)

class Scanner(serial.Serial):
    def __init__(self, device):
        super().__init__()

        self.port = device
        self.baudrate = 115200
        self.timeout = 1
        self.open()

    def scan(self):
        self.write(b'\x02\x01\x01\x02\xe8\x03\x00\x00\x00\x00\x00\x00\x00\x00\x03\x0c')     # enable decoding, delay=1s (see manual)
        return self.readline()

class App():
    def __init__(self):
        self.arduino = Arduino()
        
        t_0 = threading.Thread(target=self.handle_serial)
        # t_0.daemon = True
        t_0.start()

        self.scanners = []

        for port in serial.tools.list_ports.comports():
            if port.pid == 0x5740 and port.vid == 0x0483:
                self.scanners.append(Scanner(port.device))

        # for position, scanner in enumerate(self.scanners):
        #     print(scanner)
        #     scanner.scan()

    def handle_serial(self):
        buffer = bytearray()
        while True:
            try:
                buffer = self.arduino.readline()
            except Exception as e:
                print(e)
                # break
            if buffer:
                print(f'[DEVICE] {buffer}')
                line = buffer.decode('utf-8')
                line_stripped = line.rstrip()
                j = json.loads(line_stripped)
                # print(j)
                # print(j['boot_id'], j['message_id'], j['method'])
                # break
                if j['method'] == 'hand_shake':
                    self.hand_shake(j['parameter'])
                elif j['method'] == 'upload_firmware':
                    self.upload_firmware(j['parameter'])

    def hand_shake(self, parameter):
        print(parameter)
        self.arduino.write("{\"ACK\":\"alive\"}\r".encode())

    def upload_firmware(self, parameter):
        self.scanners[parameter-1].scan()

def main():
    app = App()

if __name__ == "__main__":
    main()