import platform
import requests
import uuid
import hashlib
import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import sys
import psutil

# 这里写你的产品名，url以后换服务器会变
url = ""
no_key = ""

def verify_product_key(product_key, machine_code):
    data = {
        "machine_code": machine_code,
        "product_key": product_key,
        "product_name": no_key
    }
    response = requests.post(url, json=data)
    return response.json()

def verify_key(auto=False):
    user_key = key_entry.get()
    machine_code = get_machine_code()
    machine_code = generate_user(machine_code)
    current_key = generate_key(machine_code)
    if user_key == current_key:
        if not auto:
            messagebox.showinfo("激活成功",  "点击确认启动，感谢支持白键桌宠")
        save_data()
        app.withdraw()
        try:
            current_dir = os.path.dirname(__file__)
            exe_path = os.path.join(current_dir, 'gsl.exe')
            subprocess.run([exe_path], check=True, cwd=os.path.dirname(sys.executable), shell=True,
                           stdin=subprocess.PIPE,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            app.destroy()
            sys.exit()
        except subprocess.CalledProcessError as e:
            print(f"Error running gsl.exe: {e}")
        except FileNotFoundError:
            print("gsl.exe not found.")
    else:
        if not auto:
            messagebox.showerror("激活码错误", "激活码错误,请重试(或联系白键小店)")

def run_gsl():
    try:
        current_dir = os.path.dirname(__file__)
        exe_path = os.path.join(current_dir, 'gsl.exe')
        subprocess.run([exe_path], check=True, cwd=os.path.dirname(sys.executable), shell=True, stdin=subprocess.PIPE,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print(f"Error running gsl.exe: {e}")
    except FileNotFoundError:
        print("gsl.exe not found.")

def get_machine_code():
    # 移除了主机名(node)部分，只保留硬件信息
    cpu_info = str(platform.processor()) + str(psutil.cpu_count(logical=False)) + str(psutil.cpu_count(logical=True))
    mainboard_serial_number = get_mainboard_serial_number()
    # 仅使用CPU信息和主板序列号
    machine_code = cpu_info + mainboard_serial_number
    return machine_code

def generate_user(machine_code):
    pre_key = 'hy'
    end_key = 'a'
    machine_code = pre_key + machine_code + end_key
    return hashlib.md5(machine_code.encode()).hexdigest()

def generate_key(machine_code):
    machine_code = machine_code + no_key
    return hashlib.md5(machine_code.encode()).hexdigest()

def endback_verify():
    machine_code = get_machine_code()
    machine_code = generate_user(machine_code)
    product_key = key_shop.get()
    res = verify_product_key(product_key, machine_code)
    print(res)
    message = res["message"]
    key_var.set(message)
    response_key = res["response_key"]
    key_entry.insert(0, response_key)
    


def get_disk_serial_number():
    try:
        command = r"powershell -Command \"Get-CimInstance Win32_DiskDrive | Select-Object -ExpandProperty SerialNumber -First 1 | ForEach-Object { $_.Trim() }\""
        output = subprocess.check_output(command, shell=True).decode('utf-8').strip()
        return output if output else "UnknownDiskSerial"
    except Exception as e:
        print(f"Error getting disk serial: {e}")
        return "UnknownDiskSerial"

def get_mainboard_serial_number():
    try:
        command = r"powershell -Command \"Get-CimInstance Win32_BaseBoard | Select-Object -ExpandProperty SerialNumber | ForEach-Object { $_.Trim() }\""
        output = subprocess.check_output(command, shell=True).decode('utf-8').strip()
        return output if output else "UnknownMBoardSerial"
    except Exception as e:
        print(f"Error getting mainboard serial: {e}")
        return "UnknownMBoardSerial"

def save_data():
    with open("可莉.txt", "w") as file:
        content = key_entry.get()
        file.write(content)

def load_data():
    try:
        with open("可莉.txt", "r") as file:
            content = file.read()
            key_entry.insert(0, content)
    except FileNotFoundError:
        pass

def auto_verify():
    user_key = key_entry.get()
    if user_key:
        machine_code = get_machine_code()
        machine_code_user = generate_user(machine_code)
        current_key = generate_key(machine_code_user)
        if user_key == current_key:
            verify_key(auto=True)

if __name__ == '__main__':
    app = tk.Tk()
    app.title("桌宠验证")

    key_var = tk.StringVar()
    key_var.set("请输入购买得到的激活码")

    key_label = tk.Label(app, textvariable=key_var)
    key_label.pack()

    key_shop = tk.Entry(app)
    key_shop.pack()

    button_var = tk.StringVar()
    button_var.set("激活")
    copy_button = tk.Button(app, textvariable=button_var, command=endback_verify)
    copy_button.pack()

    key_entry = tk.Entry(app)
    key_entry.pack()
    load_data()

    verify_button = tk.Button(app, text="启动", command=lambda: verify_key())
    verify_button.pack()

    # 自动验证（延迟100ms确保GUI初始化完成）
    app.after(100, auto_verify)

    app.mainloop()