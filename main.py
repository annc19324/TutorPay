import tkinter as tk
from gui_login import LoginScreen

if __name__ == "__main__":
    """Khởi động ứng dụng TutorPay."""
    root = tk.Tk()
    app = LoginScreen(root)
    root.mainloop()