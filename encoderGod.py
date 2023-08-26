import platform
import uuid
import hashlib
import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import sys
import psutil
from multiprocessing import freeze_support
freeze_support()

def verify_key():
    user_key = key_entry.get()
    machine_code = get_machine_code()
    machine_code = generate_user(machine_code)
    current_key = generate_key(machine_code)
    if user_key == current_key:
        messagebox.showinfo("激活成功", "正在启动，感谢支持白键小店")
        save_data()
        app.withdraw()
        try:
            current_dir = os.path.dirname(__file__)
            exe_path = os.path.join(current_dir, 'gsl.exe')
            subprocess.run([exe_path], check=True, cwd=os.path.dirname(sys.executable), shell=True,
                           stdin=subprocess.PIPE,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            app.iconify()
            app.destroy()
        except subprocess.CalledProcessError as e:
            print(f"Error running gsl.exe: {e}")
        except FileNotFoundError:
            print("gsl.exe not found.")
    else:
        messagebox.showerror("激活码错误", "激活码错误,请重试(或联系白键小店)")


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
    no_key = 'pg1'
    machine_code = machine_code + no_key
    return hashlib.md5(machine_code.encode()).hexdigest()

def copy_text():
    app.clipboard_clear()
    machine_code = get_machine_code()
    machine_code = generate_user(machine_code)
    app.clipboard_append(machine_code)
    button_var.set("复制成功!请将用户id粘贴发送给白键小店客服领取激活码")

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

def save_data():
    with open(get_data_file_path(), "w") as file:
        content = key_entry.get()
        file.write(content)

def load_data():
    try:
        with open(get_data_file_path(), "r") as file:
            content = file.read()
            key_entry.insert(0, content)
    except FileNotFoundError:
        pass
def get_data_file_path():
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, "data.txt")
    else:
        return "data.txt"


if __name__ == '__main__':
    app = tk.Tk()
    app.title("桌宠验证")


    key_var = tk.StringVar()
    key_var.set("请点击下方复制按钮获取用户码(发送给白键小店客服领取激活码)")

    key_label = tk.Label(app, textvariable=key_var)
    key_label.pack()

    button_var = tk.StringVar()
    button_var.set("复制")
    copy_button = tk.Button(app, textvariable=button_var, command=copy_text)
    copy_button.pack()
    key_entry = tk.Entry(app)
    key_entry.pack()
    load_data()

    verify_button = tk.Button(app, text="启动", command=verify_key)
    verify_button.pack()
    app.mainloop()



