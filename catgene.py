import platform
import uuid
import hashlib
import tkinter as tk
from tkinter import messagebox
import subprocess
import psutil

generated_result = ''
def get_machine_code():
    machine_info = platform.uname()
    mac_address = hex(uuid.getnode())[2:]
    cpu_info = str(platform.processor()) + str(psutil.cpu_count(logical=False)) + str(psutil.cpu_count(logical=True))
    disk_serial_number = get_disk_serial_number()
    mainboard_serial_number = get_mainboard_serial_number()
    machine_code = machine_info.node + mac_address + cpu_info + disk_serial_number + mainboard_serial_number
    return machine_code
def generate_user(machine_code):
    pre_key = 'hy'
    end_key = 'a'
    machine_code = pre_key + machine_code + end_key
    return hashlib.md5(machine_code.encode()).hexdigest()
def generate_key(machine_code):
    return hashlib.md5(machine_code.encode()).hexdigest()

def get_disk_serial_number():
    try:
        output = subprocess.check_output(['wmic', 'diskdrive', 'get', 'SerialNumber']).strip()
        return output.decode('utf-8').split('\n')[1]
    except:
        return None

def get_mainboard_serial_number():
    try:
        output = subprocess.check_output(['wmic', 'baseboard', 'get', 'SerialNumber']).strip()
        return output.decode('utf-8').split('\n')[1]
    except:
        return None

def on_generate_button_click():
    user_key = key_entry.get()
    no_seed = no_entry.get()
    generated_result = generate_key(user_key+no_seed)
    key_var.set(generated_result)

def copy_text():
    app.clipboard_clear()
    output = key_var.get()
    app.clipboard_append(output)

if __name__ == '__main__':
    app = tk.Tk()
    app.geometry("400x300")
    app.title("Key Verification")
    key_label = tk.Label(app, text="机器码")
    key_label.pack()
    key_entry = tk.Entry(app)
    key_entry.pack()
    no_label = tk.Label(app, text="产品号")
    no_label.pack()
    no_entry = tk.Entry(app)
    no_entry.pack()
    gene_button = tk.Button(app, text="生成", command=on_generate_button_click)
    gene_button.pack()
    key_var = tk.StringVar()
    key_var.set("还没好")

    key_label = tk.Label(app, textvariable=key_var)
    key_label.pack()
    key_var.set(generated_result)
    copy_button = tk.Button(app, text="Copy", command=copy_text)
    copy_button.pack()

    app.mainloop()