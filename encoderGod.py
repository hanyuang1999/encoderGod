import platform
import uuid
import hashlib
import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import sys

def verify_key():
    user_key = key_entry.get()
    current_key = generate_key(get_machine_code())
    if user_key == current_key:
        messagebox.showinfo("Success", "Key verified. Starting application.")
        try:
            current_dir = os.path.dirname(__file__)
            exe_path = os.path.join(current_dir, 'gsl.exe')
            subprocess.run([exe_path], check=True,cwd=os.path.dirname(sys.executable),shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            print(f"Error running gsl.exe: {e}")
        except FileNotFoundError:
            print("gsl.exe not found.")
    else:
        messagebox.showerror("Error", "Invalid key. Please try again.")

def get_machine_code():
    machine_info = platform.uname()
    mac_address = hex(uuid.getnode())[2:]
    machine_code = machine_info.node + mac_address
    return machine_code
def generate_key(machine_code):
    no_key = 'pg1'
    machine_code = machine_code + no_key
    return hashlib.md5(machine_code.encode()).hexdigest()

def copy_text():
    app.clipboard_clear()
    original_string = key_var.get()
    colon_index = original_string.index(":")  # 找到冒号的索引位置
    result = original_string[colon_index + 1:]  # 截取冒号后面的内容
    app.clipboard_append(result)


if __name__ == '__main__':
    machine_code = get_machine_code()
    app = tk.Tk()
    app.title("桌宠验证")


    key_var = tk.StringVar()
    key_var.set("你的机器码:"+machine_code)

    key_label = tk.Label(app, textvariable=key_var)
    key_label.pack()

    copy_button = tk.Button(app, text="Copy", command=copy_text)
    copy_button.pack()
    key_entry = tk.Entry(app)
    key_entry.pack()

    verify_button = tk.Button(app, text="Verify Key", command=verify_key)
    verify_button.pack()
    app.mainloop()



