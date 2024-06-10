#   this version works with fixture version 0.4.6
#   changed UI and device find logic
#
#   copy script along with msi_logo.png into a virtual environment with pyinstaller 
#   run command to package:
#   pyinstaller --onefile --noconsole --add-data "msi_logo.png;." grizzle_app_v_1_2.py 

import csv, os, struct, time, threading, datetime
import tkinter
import serial
import serial.tools.list_ports
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from tkinter.messagebox import showwarning
from PIL import ImageTk, Image

# this function is for packaging script into executable
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class Model(serial.Serial):
    def __init__(self):
        super().__init__()

        self.baudrate = 115200
        self.timeout = 0.1

        self.header = ["Date/Time", "QR CODE", "POWER ON", "GROUND", "PILOT STATE A", "PILOT STATE B", "DIODE", "OVER CURRENT",
        "GFCI_L1_LOW LEAKAGE", "GFCI_L1_HIGH LEAKAGE", "GFCI_L2_LOW LEAKAGE", "GFCI_L2_HIGH LEAKAGE", "STUCK RELAY"]

    def find_device(self):
        found_device = False
        for port in serial.tools.list_ports.comports():
            if port.pid == 0x7523 and port.vid == 0x1a86:
                self.port = port.device
                self.description = port.description
                found_device= True
                # print(self.description)
        if found_device is True:
            return 0
        else:
            return 1

    def get_status(self):
        # buffer = bytearray()
        # if self.find_device() == 0:
        #     print("get status ...")
        #     if self.is_open is not True:
        #         print("brand new port, will open it ...")
        #         self.open()
        self.write(b'\x16')         # SYN
        buffer = self.read(1)
        print(buffer)
        return buffer

    def start_test(self):
        try:
            self.write(b'\x30')
        except Exception as e:
            print(e)
        return

    def abort_test(self):
        try:
            self.write(b'\x31')
        except Exception as e:
            print(e)
        return

    def next_test(self):
        try:
            self.write(b'\x33')
        except Exception as e:
            print(e)
        return
    
    def port_listen(self, num_bytes):
        buffer = bytearray()
        t_0 = time.time()
        while True:
            try:
                buffer = self.readline()
            except Exception as e:
                print(e)
                break
            if buffer:
                print(f'device returns: {buffer}')
                break
            if time.time() - t_0 > 45:
                break
        return buffer

    def save(self, serial_number, data):
        dir_name = 'log'
        file_name = serial_number

        if not os.path.exists(dir_name):
            os.mkdir(dir_name)
            # print("Directory", dir_name, "created")
        else:
            pass
            # print("Directory", dir_name, "already exists")

        with open(dir_name + '/' + file_name + '.csv', 'w') as f:
            writer = csv.writer(f)
            writer.writerow(self.header)
            writer.writerow(data)

# navigation frame
class navigation_frame(ttk.Frame):
    def __init__(self, container):
        super().__init__(container)

        container.columnconfigure(0, weight=3)
        container.columnconfigure(1, weight=1)

        container.rowconfigure(0, weight=1)
        container.rowconfigure(1, weight=1)
        container.rowconfigure(2, weight=1)
        container.rowconfigure(3, weight=1)
        container.rowconfigure(4, weight=1)
        container.rowconfigure(5, weight=1)
        container.rowconfigure(6, weight=1)
        container.rowconfigure(7, weight=1)
        container.rowconfigure(8, weight=1)
        container.rowconfigure(9, weight=1)
        container.rowconfigure(10, weight=1)
        container.rowconfigure(11, weight=9)

        self.str_run_time = '0'
        self.stopped = False
        self.t_0 = 0

        self.info = ttk.Label(container, text='Designed for United Chargers by', font=('TkDefaultFont',12))

        self.png = Image.open(resource_path("msi_logo.png"))
        self.img = ImageTk.PhotoImage(self.png)
        self.logo = ttk.Label(container, image=self.img)

        self.device_status_text = tk.StringVar()
        self.device_status_text.set('Device: ')
        self.device_status = ttk.Label(container, textvariable=self.device_status_text)
        
        self.connect_button = ttk.Button(container, text='Find Device',command=self.connect_button_clicked)
        
        self.test_button_state = 0
        self.test_button = ttk.Button(container, text='Run',command=self.run_button_clicked)

        self.clear_button = ttk.Button(container, text='Clear Results',command=self.clear_button_clicked)
        
        self.serial_number = None
        self.serial_number_temp = tk.StringVar()
        
        self.serial_number_label = ttk.Label(container, text="Serial Number")
        
        self.serial_number_entry = ttk.Entry(container, textvariable=self.serial_number_temp)

        self.operator_number_label = ttk.Label(container, text="Operator Number")
        
        self.operator_number_entry = ttk.Entry(container,)

        self.run_time = ttk.Label(container, text='Run time: ' + self.str_run_time)
        self.version_number = ttk.Label(container, text="Versoin 1.2")
        
        self.info.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.logo.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.connect_button.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        self.device_status.grid(row=3, column=0, sticky="ew", padx=5, pady=5)
        self.test_button.grid(row=4, column=0, sticky="ew", padx=5, pady=5)
        self.clear_button.grid(row=5, column=0, sticky="ew", padx=5, pady=5)
        self.serial_number_label.grid(row=6, column=0, sticky="ew", padx=5, pady=5)
        self.serial_number_entry.grid(row=7, column=0, sticky="ew", padx=5, pady=5)
        self.operator_number_label.grid(row=8, column=0, sticky="ew", padx=5, pady=5)
        self.operator_number_entry.grid(row=9, column=0, sticky="ew", padx=5, pady=5)
        self.run_time.grid(row=10, column=0, sticky="sew", padx=5, pady=5)
        self.version_number.grid(row=11, column=0, sticky="s", padx=5, pady=5)

        self.controller = None

    def set_controller(self, controller):
        self.controller = controller

    def connect_button_clicked(self):
        if self.controller:
            self.controller.find_device()

    def run_button_clicked(self):
        if self.test_button_state == 0:
            system_status = self.controller.get_status()
            if system_status == 0:
                self.serial_number = self.serial_number_temp.get()
                if self.serial_number == '':
                    print("show warning")
                    showwarning(title=None,message='Please scan serial number before proceeding!')
                else:
                    self.test_button_state = 1
                    self.test_button.configure(text="Abort")
                    self.stopped =False
                    if self.controller:
                        self.controller.display_state('Test running ...', "#F4D03F")
                        self.start_timer()
                        self.controller.start_test()
            elif system_status == 2:
                print("show warning")
                showwarning(title=None,message='Variable DC seems to be disconnected')
            elif system_status == 1:
                print("show warning")
                showwarning(title=None,message='AC power seems to be disconnected or lid is not closed')
            elif system_status == 3:
                print("show warning")
                showwarning(title=None,message='AC power seems to be disconnected or lid is not closed. DC may also be down')

        elif self.test_button_state == 1:
            self.test_button_state = 0
            if self.controller:
                self.controller.display_state('Aborting test ...', "#F4D03F")
                self.controller.abort_test()
                self.test_button.state(['disabled'])                                            # button text 'Run' is updated in controoler -> mainloop()

    def clear_button_clicked(self):
        if self.test_button_state == 0 and self.controller.state == 0:
            self.controller.clear_test()
            self.controller.display_state('Ready', "#F4D03F")
            self.serial_number_entry.delete(0, tk.END)
            self.serial_number = None
            self.serial_number_entry.focus_set()

    def start_timer(self):
        self.t_0 = time.time()
        self.update_timer()

    def update_timer(self):
        self.run_time.configure(text='Run time: ' + str(datetime.timedelta(seconds=time.time() - self.t_0)))

        if not self.stopped:
            self.run_time.after(1000, lambda:self.update_timer())

# test frame
class test_frame(ttk.Frame):
    def __init__(self, container):
        super().__init__(container)

        self.container = container
        
        self.display_state = tk.StringVar()
        self.display_state.set('Ready')

        self.test_state_style = ttk.Style(self)
        self.test_state_style.configure('large.TLabel', anchor="center", foreground="#FFFFFF", background="#F4D03F", font=('TkDefaultFont',20))

        # width is number of characters
        self.test_state = ttk.Label(self.container, textvariable=self.display_state, style='large.TLabel', width=20)
        self.test_state.pack(padx=5, pady=5, fill=tk.BOTH)

        self.cards = []

        # set controller
        self.controller = None

    def set_controller(self, controller):
        self.controller = controller

    def add_test(self, test, direction):
        card = ttk.Label(self.container, text=test)
        card.pack(ipadx=10, anchor=direction)
        self.cards.append(card)

    def clear_test(self):
        for card in self.cards:
            card.destroy()
        self.cards.clear()

class Controller():
    def __init__(self, model, view, test):
        self.model = model
        self.view = view
        self.test = test
        self.state = 0
        self.system_initialized = 0
        self.test_result_data = []

    def find_device(self):
        if self.model.find_device() == 0:
            self.view.device_status_text.set('Device: ' + self.model.description)
            self.model.open()
            time.sleep(1)
            self.keep_alive()
        else:
            self.view.device_status_text.set('Device: ')

    def get_status(self):
        system_status = self.model.get_status()
        if system_status:
            return 0
            # if system_status[0] == 0x50 and system_status[1] == 0x50:
            #     return 0
            # elif system_status[0] == 0x50 and system_status[1] == 0x46:
            #     print("ac down or limit switch open")
            #     return 1
            # elif system_status[0] == 0x46 and system_status[1] == 0x50:
            #     print("variable dc down")
            #     return 2
            # elif system_status[0] == 0x46 and system_status[1] == 0x46:
            #     print("variable dc down and ac down/limit switch open")
            #     return 3

    # this functioin should pull device every second
    def keep_alive(self):
        print("keep alive")
        # self.model.write(b'\x16')
        # print(self.model.read(1))
        self.view.after(1000, lambda: self.keep_alive())

    def start_test(self):
        self.state = 1
        self.test_result_data.clear()                                                           # clear list, otherwise previous tests result data will be written to the same .csv file
        self.test_result_data.append(str(datetime.datetime.now()))
        self.test_result_data.append(self.view.serial_number)

        if self.test.cards:                                                                     # clear test results from window if there any
            self.test.clear_test()
            # print(len(self.test.cards))

        self.view.start_timer()

        self.model.start_test()                                                                 # run test

        a = threading.Thread(target=self.task_1)                                                # hanlde communication with fixture in a thread
        a.daemon = True
        a.start()
        
    def abort_test(self):
        self.model.abort_test()
        self.view.stopped = True
        self.system_initialized = 0

    def reset_fixture(self):
        self.model.abort_test()

    def display_state(self, label_state, color):
        self.test.display_state.set(label_state)
        self.test.test_state_style.configure('large.TLabel', background=color)

    def clear_test(self):
        if self.test.cards:                                                                     # clear test results from window if there any
            self.test.clear_test()

    def set_ready(self):
        self.test.display_state.set('Ready')

    def task_1(self):
        test_pass = 0

        for item in self.model.header[2:]:
            self.test.add_test(item, 'center')

            if item == 'POWER ON':
                test_1_fail = 0
                # buffer = self.model.port_listen(12)
                # if buffer:
                #     test_result = struct.unpack('cchhhhh', buffer)
                    
                #     if test_result[0] == b'P':
                #         self.test.add_test('LED: OK', 'w')
                #     elif test_result[0] == b'F':
                #         self.test.add_test('LED: FAILED', 'w')
                #         test_1_fail += 1
                #     if test_result[1] == b'P':
                #         self.test.add_test('Stuck Relay: OK', 'w')
                #     elif test_result[1] == b'F':
                #         self.test.add_test('Stuck Relay: FAILED', 'w')
                #         test_1_fail += 1

                #     tp35 = test_result[2] * 0.0083 - 17.0335
                #     if tp35 < 12.48 and tp35 > 11.52:
                #         self.test.add_test('TP35: ' + f'{tp35:.2f}' + 'V', 'w')
                #     else:
                #         self.test.add_test('TP35: ' + f'{tp35:.2f}' + 'V', 'w')
                #         test_1_fail += 1

                #     tp21 = test_result[3] * 0.0083 - 17.0335
                #     if tp21 < 12.48 and tp21 > 11.52:
                #         self.test.add_test('TP21: ' + f'{tp21:.2f}' + 'V', 'w')
                #     else:
                #         self.test.add_test('TP21: ' + f'{tp21:.2f}' + 'V', 'w')
                #         test_1_fail += 1

                #     tp22 = test_result[4] * 0.0083 - 17.0335
                #     if tp22 > -12.48 and tp22 < -11.52:
                #         self.test.add_test('TP22: ' + f'{tp22:.2f}' + 'V', 'w')
                #     else:
                #         self.test.add_test('TP22: ' + f'{tp22:.2f}' + 'V', 'w')
                #         test_1_fail += 1

                #     tp26 = test_result[6] * 0.0083 - 17.0335
                #     if tp26 < 1.39 and tp26 > 0.75:
                #         self.test.add_test('TP26: ' + f'{tp26:.2f}' + 'V', 'w')
                #     else:
                #         self.test.add_test('TP26: ' + f'{tp26:.2f}' + 'V', 'w')
                #         test_1_fail += 1

                #     if test_1_fail == 0:
                #         self.test.add_test('pass', 'e')
                #         self.test_result_data.append('P')
                #         test_pass += 1
                #     else:
                #         self.test.add_test('fail', 'e')
                #         self.test_result_data.append('F')
                # else:
                #     break

            elif item == 'GROUND':
                test_2_fail = 0
                # buffer = self.model.port_listen(6)
                # if buffer:
                #     test_result = struct.unpack('hhh', buffer)
                    
                #     if test_result[0] == 1:
                #         self.test.add_test('LED: OK', 'w')
                #         test_2_fail += 0
                #     else:
                #         self.test.add_test('LED: FAILED', 'w')
                #         test_2_fail += 1
                #     if test_result[1] == 1:
                #         self.test.add_test('BUZZER: OK', 'w')
                #         test_2_fail += 0
                #     else:
                #         self.test.add_test('BUZZER: FAILED', 'w')
                #         test_2_fail += 1
                #     tp38 = (test_result[2]-2045)*0.0085
                #     if tp38 < 3.43 and tp38 > 3.17:
                #         self.test.add_test('TP38: ' + f'{tp38:.2f}' + 'V', 'w')
                #         test_2_fail += 0
                #     else:
                #         self.test.add_test('TP38: ' + f'{tp38:.2f}' + 'V', 'w')
                #         test_2_fail += 1

                #     if test_2_fail == 0:
                #         self.test.add_test('pass', 'e')
                #         self.test_result_data.append('P')
                #         test_pass += 1
                #     else:
                #         self.test.add_test('fail', 'e')
                #         self.test_result_data.append('F')
                # else:
                #     break

            else:                                                                               # all other tests send two bytes of information
                pass
                # buffer = self.model.port_listen(2)
                # if buffer:
                #     test_result = struct.unpack('cc', buffer)

                #     if test_result[1] == b'P':
                #         self.test.add_test('pass', 'e')
                #         test_pass += 1

                #     if test_result[1] == b'F':
                #         self.test.add_test("#" + test_result[0].decode('utf-8') + " FAIL**", 'e')
                    
                #     self.test_result_data.append(test_result[1].decode('utf-8'))
                # else:
                #     break

            time.sleep(3)
            
            if self.view.stopped:
                break
            else:    
                self.model.next_test()                                                          # last next_test command triggers _abort() in fsm in fixture

        if test_pass == 11:
            self.display_state('Test Passed', '#28B463')
        else:
            self.display_state('Test Failed', "#C0392B")

        self.model.save(self.view.serial_number, self.test_result_data)
        self.view.stopped = True                                                                # stop timer
        self.system_initialized = 0

        self.view.test_button_state = 0
        self.view.test_button.configure(text="Run")
        self.view.test_button.state(['!disabled'])
        self.state = 0

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("GRIZZLE Automated Test")

        self.app_width = 750
        self.app_height = 650
        self.centre_x = int(self.winfo_screenwidth()/2 - self.app_width/2)
        self.centre_y = int(self.winfo_screenheight()/2 - self.app_height/2)

        self.geometry(f'{self.app_width}x{self.app_height}+{self.centre_x}+{self.centre_y}')
        self.minsize(self.app_width,self.app_height)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=5)

        container_1 = ttk.Frame(self)
        container_2 = ttk.Frame(self)

        container_1.grid(column=0,row=0,sticky=tk.NSEW)
        container_2.grid(column=1,row=0,sticky=tk.NSEW)

        # create a model
        model = Model()

        # create a view and place it on root window
        view = navigation_frame(container_1)
        test = test_frame(container_2)

        # create a controller
        self.controller = Controller(model, view, test)

        test.set_controller(self.controller)
        view.set_controller(self.controller)

    def on_closing(self):
        try:
            self.controller.reset_fixture()
        except:
            pass
        finally:
            self.destroy()

if __name__ == "__main__":
    app = App()
    # app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()