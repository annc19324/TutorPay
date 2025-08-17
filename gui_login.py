import tkinter as tk
from tkinter import messagebox, ttk
import webbrowser
from database import Database
from gui_learner import LearnerScreen
from gui_payroll import PayrollScreen
from gui_account import AccountScreen
from PIL import Image, ImageTk
import os

class LoginScreen:
    def __init__(self, root):
        """Khởi tạo giao diện đăng nhập."""
        self.root = root
        self.root.title("TutorPay - Đăng nhập")
        self.root.geometry("500x400")
        self.root.configure(bg="#F5F7FA")
        self.db = Database()
        self.current_user = None
        self.current_fullname = None
        self.style = ttk.Style()
        self.configure_styles()
        self.set_window_icon(self.root)
        self.center_window()
        self.show_login()

    def configure_styles(self):
        """Cấu hình kiểu dáng cho các widget."""
        self.style.configure("TEntry", padding=8, font=("Segoe UI", 11))
        self.style.configure("TButton", padding=8, font=("Segoe UI", 11, "bold"))
        self.style.configure("TLabel", background="#FFFFFF", font=("Segoe UI", 11))
        self.style.configure("Header.TLabel", font=("Segoe UI", 20, "bold"), foreground="#1E88E5")
        self.style.configure("SubHeader.TLabel", font=("Segoe UI", 11), foreground="#37474F")
        self.style.configure("Treeview", font=("Segoe UI", 11), rowheight=30)
        self.style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"))
        self.style.configure("TCombobox", padding=8, font=("Segoe UI", 11))
        self.style.configure("Hover.TButton", background="#1565C0", foreground="#1565C0")
        self.style.configure("TCheckbutton", background="#FFFFFF", font=("Segoe UI", 11))

    def set_window_icon(self, window):
        """Đặt biểu tượng cửa sổ thành annc19324.ico."""
        try:
            icon_path = os.path.join(os.path.dirname(__file__), "annc19324.ico")
            if os.path.exists(icon_path):
                window.iconbitmap(icon_path)
            else:
                print("Icon file not found; skipping icon setting.")
        except tk.TclError as e:
            print(f"Error setting icon: {e}. Skipping icon setting.")

    def center_window(self):
        """Căn giữa cửa sổ trên màn hình."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def clear_screen(self):
        """Xóa tất cả widget trên màn hình và đặt lại cấu hình cửa sổ."""
        for widget in self.root.winfo_children():
            widget.destroy()
        self.root.geometry("500x400")
        self.root.grid_rowconfigure(0, weight=0)
        self.root.grid_columnconfigure(0, weight=0)
        self.root.update_idletasks()

    def create_button(self, frame, text, command, bg_color):
        """Tạo nút với hiệu ứng hover."""
        button = ttk.Button(frame, text=text, command=command, style="TButton")
        button.configure(cursor="hand2")
        button.bind("<Enter>", lambda e: button.configure(style="Hover.TButton"))
        button.bind("<Leave>", lambda e: button.configure(style="TButton"))
        return button

    def toggle_password(self, entry, var):
        """Chuyển đổi giữa hiển thị và ẩn mật khẩu."""
        entry.config(show='' if var.get() else '*')

    def show_login(self):
        """Hiển thị giao diện đăng nhập."""
        self.clear_screen()
        self.root.geometry("500x400")
        main_frame = tk.Frame(self.root, bg="#F5F7FA")
        main_frame.pack(expand=True, fill="both", padx=15, pady=15)

        header_frame = tk.Frame(main_frame, bg="#F5F7FA")
        header_frame.pack(fill="x")
        ttk.Label(header_frame, text="TutorPay", style="Header.TLabel").pack(pady=5)
        ttk.Label(header_frame, text="Quản lý lương gia sư", style="SubHeader.TLabel").pack()

        form_frame = tk.Frame(main_frame, bg="#FFFFFF")
        form_frame.pack(padx=15, pady=15, fill="x")
        form_frame.configure(highlightbackground="#E0E0E0", highlightthickness=1)

        ttk.Label(form_frame, text="Tên người dùng:").pack(anchor="w", padx=10, pady=5)
        username_entry = ttk.Entry(form_frame, style="TEntry")
        username_entry.pack(fill="x", padx=10, pady=5)

        ttk.Label(form_frame, text="Mật khẩu:").pack(anchor="w", padx=10, pady=5)
        password_entry = ttk.Entry(form_frame, show='*', style="TEntry")
        password_entry.pack(fill="x", padx=10, pady=5)

        show_password_var = tk.BooleanVar()
        show_password_check = ttk.Checkbutton(form_frame, text="Hiện mật khẩu", variable=show_password_var,
                                             command=lambda: self.toggle_password(password_entry, show_password_var),
                                             style="TCheckbutton")
        show_password_check.pack(anchor="w", padx=10, pady=5)

        self.username_entry = username_entry
        self.password_entry = password_entry

        button_frame = tk.Frame(main_frame, bg="#F5F7FA")
        button_frame.pack(pady=10, fill="x")
        login_button = self.create_button(button_frame, "Đăng nhập",
                                         lambda: self.login(username_entry.get(), password_entry.get()),
                                         "#1E88E5")
        login_button.pack(side="left", padx=5, fill="x", expand=True)
        register_button = self.create_button(button_frame, "Đăng ký",
                                            self.show_register,
                                            "#43A047")
        register_button.pack(side="left", padx=5, fill="x", expand=True)
        forgot_button = self.create_button(button_frame, "Quên mật khẩu",
                                          self.forgot_password,
                                          "#78909C")
        forgot_button.pack(side="left", padx=5, fill="x", expand=True)

        username_entry.focus_set()
        username_entry.bind("<Return>", lambda event: password_entry.focus_set())
        password_entry.bind("<Return>", lambda event: self.login(username_entry.get(), password_entry.get()))
        login_button.bind("<Return>", lambda event: self.login(username_entry.get(), password_entry.get()))
        register_button.bind("<Return>", lambda event: self.show_register())
        forgot_button.bind("<Return>", lambda event: self.forgot_password())

        self.center_window()

    def show_register(self):
        """Hiển thị giao diện đăng ký."""
        self.clear_screen()
        self.root.geometry("500x480")
        main_frame = tk.Frame(self.root, bg="#F5F7FA")
        main_frame.pack(expand=True, fill="both", padx=15, pady=15)

        header_frame = tk.Frame(main_frame, bg="#F5F7FA")
        header_frame.pack(fill="x")
        ttk.Label(header_frame, text="TutorPay", style="Header.TLabel").pack(pady=5)
        ttk.Label(header_frame, text="Tạo tài khoản mới", style="SubHeader.TLabel").pack()

        form_frame = tk.Frame(main_frame, bg="#FFFFFF")
        form_frame.pack(padx=15, pady=15, fill="x")
        form_frame.configure(highlightbackground="#E0E0E0", highlightthickness=1)

        ttk.Label(form_frame, text="Tên người dùng:").pack(anchor="w", padx=10, pady=5)
        username_entry = ttk.Entry(form_frame, style="TEntry")
        username_entry.pack(fill="x", padx=10, pady=5)

        ttk.Label(form_frame, text="Họ và tên:").pack(anchor="w", padx=10, pady=5)
        fullname_entry = ttk.Entry(form_frame, style="TEntry")
        fullname_entry.pack(fill="x", padx=10, pady=5)

        ttk.Label(form_frame, text="Mật khẩu:").pack(anchor="w", padx=10, pady=5)
        password_entry = ttk.Entry(form_frame, show='*', style="TEntry")
        password_entry.pack(fill="x", padx=10, pady=5)

        show_password_var = tk.BooleanVar()
        show_password_check = ttk.Checkbutton(form_frame, text="Hiện mật khẩu", variable=show_password_var,
                                             command=lambda: self.toggle_password(password_entry, show_password_var),
                                             style="TCheckbutton")
        show_password_check.pack(anchor="w", padx=10, pady=5)

        self.username_entry = username_entry
        self.fullname_entry = fullname_entry
        self.password_entry = password_entry

        button_frame = tk.Frame(main_frame, bg="#F5F7FA")
        button_frame.pack(pady=10, fill="x")
        register_button = self.create_button(button_frame, "Đăng ký",
                                            lambda: self.register(username_entry.get(), fullname_entry.get(), password_entry.get()),
                                            "#43A047")
        register_button.pack(side="left", padx=5, fill="x", expand=True)
        back_button = self.create_button(button_frame, "Quay lại",
                                        self.show_login,
                                        "#78909C")
        back_button.pack(side="left", padx=5, fill="x", expand=True)

        username_entry.focus_set()
        username_entry.bind("<Return>", lambda event: fullname_entry.focus_set())
        fullname_entry.bind("<Return>", lambda event: password_entry.focus_set())
        password_entry.bind("<Return>", lambda event: self.register(username_entry.get(), fullname_entry.get(), password_entry.get()))
        register_button.bind("<Return>", lambda event: self.register(username_entry.get(), fullname_entry.get(), password_entry.get()))
        back_button.bind("<Return>", lambda event: self.show_login())

        self.center_window()

    def login(self, username, password):
        """Xử lý đăng nhập người dùng."""
        if not username or not password:
            messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin!")
            return
        user = self.db.login_user(username, password)
        if user:
            self.current_user, self.current_fullname = user
            self.show_main()
        else:
            messagebox.showerror("Lỗi", "Tên người dùng hoặc mật khẩu sai!")

    def register(self, username, fullname, password):
        """Xử lý đăng ký người dùng mới."""
        if not username or not fullname or not password:
            messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin!")
            return
        if self.db.register_user(username, fullname, password):
            messagebox.showinfo("Thành công", "Đăng ký thành công!")
            self.show_login()
        else:
            messagebox.showerror("Lỗi", "Tên người dùng đã tồn tại!")

    def forgot_password(self):
        """Hiển thị thông tin khôi phục mật khẩu."""
        top = tk.Toplevel(self.root)
        top.title("Quên Mật Khẩu")
        top.geometry("400x220")
        top.configure(bg="#F5F7FA")
        self.set_window_icon(top)

        top.update_idletasks()
        width = top.winfo_width()
        height = top.winfo_height()
        x = (self.root.winfo_width() - width) // 2 + self.root.winfo_x()
        y = (self.root.winfo_height() - height) // 2 + self.root.winfo_y()
        top.geometry(f"{width}x{height}+{x}+{y}")

        frame = tk.Frame(top, bg="#FFFFFF", bd=0, relief="flat")
        frame.pack(expand=True, fill="both", padx=15, pady=15)
        frame.configure(highlightbackground="#E0E0E0", highlightthickness=1)

        ttk.Label(frame, text="Vui lòng liên hệ tài khoản admin để khôi phục mật khẩu.", background="#FFFFFF", wraplength=350).pack(pady=5)
        ttk.Label(frame, text="Nếu chưa biết tài khoản admin, liên hệ:", background="#FFFFFF", wraplength=350).pack(pady=5)
        
        link_label = tk.Label(frame, text="https://www.facebook.com/annc19324", fg="blue", cursor="hand2", background="#FFFFFF", font=("Segoe UI", 11, "underline"))
        link_label.pack(pady=5)
        link_label.bind("<Button-1>", lambda e: webbrowser.open("https://www.facebook.com/annc19324"))

        button_frame = tk.Frame(frame, bg="#FFFFFF")
        button_frame.pack(pady=10)
        close_button = self.create_button(button_frame, "Đóng", top.destroy, "#78909C")
        close_button.pack(side="left", padx=5)

        close_button.bind("<Return>", lambda event: top.destroy())

    def show_main(self):
        """Hiển thị giao diện chính sau khi đăng nhập với nhiều chức năng."""
        self.clear_screen()
        self.root.geometry("600x400")
        main_frame = tk.Frame(self.root, bg="#F5F7FA")
        main_frame.pack(expand=True, fill="both", padx=15, pady=15)

        header_frame = tk.Frame(main_frame, bg="#F5F7FA")
        header_frame.pack(fill="x")
        ttk.Label(header_frame, text=f"Xin chào, {self.current_fullname}", style="Header.TLabel").pack(pady=5)
        ttk.Label(header_frame, text="Chọn chức năng", style="SubHeader.TLabel").pack()

        button_frame = tk.Frame(main_frame, bg="#F5F7FA")
        button_frame.pack(pady=20, fill="both", expand=True)

        buttons = [
            ("Quản lý người học", lambda: LearnerScreen(self.root, self.current_user, self.show_main), "#1E88E5"),
            ("Quản lý bảng lương", lambda: PayrollScreen(self.root, self.current_user, self.show_main), "#1E88E5"),
            ("Hỗ trợ", self.support, "#1E88E5"),
            ("Ủng hộ", self.show_donate, "#43A047"),
            ("Xóa dữ liệu", self.delete_account, "#EF5350"),
            ("Đổi mật khẩu", self.show_change_password, "#1E88E5"),
        ]

        if self.current_user == 'admin':
            buttons.append(("Quản lý tài khoản", lambda: AccountScreen(self.root, self.current_user, self.show_main), "#1E88E5"))
        
        buttons.append(("Đăng xuất", self.show_login, "#EF5350"))

        for i, (text, command, color) in enumerate(buttons):
            row = i // 2
            col = i % 2
            btn = self.create_button(button_frame, text, command, color)
            btn.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            btn.bind("<Return>", lambda event, cmd=command: cmd())

        for i in range(2):
            button_frame.grid_columnconfigure(i, weight=1)
        for i in range((len(buttons) + 1) // 2):
            button_frame.grid_rowconfigure(i, weight=1)

        self.center_window()

    def support(self):
        """Hiển thị thông tin hỗ trợ."""
        messagebox.showinfo("Hỗ trợ", "Liên hệ hỗ trợ qua email: annc19324@gmail.com")

    def show_donate(self):
        """Hiển thị mã QR ủng hộ."""
        top = tk.Toplevel(self.root)
        top.title("Ủng hộ TutorPay")
        top.geometry("400x450")
        top.configure(bg="#F5F7FA")
        self.set_window_icon(top)

        top.update_idletasks()
        width = top.winfo_width()
        height = top.winfo_height()
        x = (self.root.winfo_width() - width) // 2 + self.root.winfo_x()
        y = (self.root.winfo_height() - height) // 2 + self.root.winfo_y()
        top.geometry(f"{width}x{height}+{x}+{y}")

        frame = tk.Frame(top, bg="#FFFFFF", bd=0, relief="flat")
        frame.pack(expand=True, fill="both", padx=15, pady=15)
        frame.configure(highlightbackground="#E0E0E0", highlightthickness=1)

        try:
            qr_path = os.path.join(os.path.dirname(__file__), "annc19324.jpg")
            qr_image = Image.open(qr_path)
            qr_image = qr_image.resize((300, 300), Image.Resampling.LANCZOS)
            qr_photo = ImageTk.PhotoImage(qr_image)
            qr_label = tk.Label(frame, image=qr_photo, bg="#FFFFFF")
            qr_label.image = qr_photo
            qr_label.pack(pady=10)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải mã QR: {e}")
            top.destroy()
            return

        ttk.Label(frame, text="Quét mã QR để ủng hộ TutorPay", background="#FFFFFF", font=("Segoe UI", 11)).pack(pady=5)

        button_frame = tk.Frame(frame, bg="#FFFFFF")
        button_frame.pack(pady=10)
        close_button = self.create_button(button_frame, "Đóng", top.destroy, "#78909C")
        close_button.pack(side="left", padx=5)

        close_button.bind("<Return>", lambda event: top.destroy())

    def delete_account(self):
        """Xóa toàn bộ dữ liệu của tài khoản hiện tại."""
        if self.current_user == 'admin':
            messagebox.showerror("Lỗi", "Tài khoản admin không thể bị xóa!")
            return
        if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xóa toàn bộ dữ liệu của tài khoản này? Hành động này không thể hoàn tác."):
            if self.db.delete_user(self.current_user):
                messagebox.showinfo("Thành công", "Đã xóa toàn bộ dữ liệu của tài khoản!")
                self.current_user = None
                self.current_fullname = None
                self.show_login()
            else:
                messagebox.showerror("Lỗi", "Không thể xóa dữ liệu. Vui lòng thử lại.")

    def show_change_password(self):
        """Hiển thị cửa sổ đổi mật khẩu."""
        top = tk.Toplevel(self.root)
        top.title("Đổi mật khẩu")
        top.geometry("350x320")
        top.configure(bg="#F5F7FA")
        self.set_window_icon(top)

        top.update_idletasks()
        width = top.winfo_width()
        height = top.winfo_height()
        x = (self.root.winfo_width() - width) // 2 + self.root.winfo_x()
        y = (self.root.winfo_height() - height) // 2 + self.root.winfo_y()
        top.geometry(f"{width}x{height}+{x}+{y}")

        frame = tk.Frame(top, bg="#FFFFFF", bd=0, relief="flat")
        frame.pack(expand=True, fill="both", padx=15, pady=15)
        frame.configure(highlightbackground="#E0E0E0", highlightthickness=1)

        ttk.Label(frame, text="Mật khẩu hiện tại:", background="#FFFFFF").pack(anchor="w", pady=5)
        current_password_entry = ttk.Entry(frame, show='*', style="TEntry")
        current_password_entry.pack(fill="x", pady=5)

        show_current_var = tk.BooleanVar()
        show_current_check = ttk.Checkbutton(frame, text="Hiện mật khẩu", variable=show_current_var,
                                            command=lambda: self.toggle_password(current_password_entry, show_current_var),
                                            style="TCheckbutton")
        show_current_check.pack(anchor="w", padx=10, pady=5)

        ttk.Label(frame, text="Mật khẩu mới:", background="#FFFFFF").pack(anchor="w", pady=5)
        new_password_entry = ttk.Entry(frame, show='*', style="TEntry")
        new_password_entry.pack(fill="x", pady=5)

        show_new_var = tk.BooleanVar()
        show_new_check = ttk.Checkbutton(frame, text="Hiện mật khẩu", variable=show_new_var,
                                         command=lambda: self.toggle_password(new_password_entry, show_new_var),
                                         style="TCheckbutton")
        show_new_check.pack(anchor="w", padx=10, pady=5)

        button_frame = tk.Frame(frame, bg="#FFFFFF")
        button_frame.pack(pady=10)
        save_button = self.create_button(button_frame, "Lưu",
                                        lambda: self.change_password(
                                            current_password_entry.get(),
                                            new_password_entry.get(),
                                            top
                                        ),
                                        "#1E88E5")
        save_button.pack(side="left", padx=5)

        current_password_entry.focus_set()
        current_password_entry.bind("<Return>", lambda event: new_password_entry.focus_set())
        new_password_entry.bind("<Return>", lambda event: self.change_password(
            current_password_entry.get(), new_password_entry.get(), top
        ))
        save_button.bind("<Return>", lambda event: self.change_password(
            current_password_entry.get(), new_password_entry.get(), top
        ))

    def change_password(self, current_password, new_password, top):
        """Xử lý đổi mật khẩu."""
        if not current_password or not new_password:
            messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin!")
            return
        user = self.db.login_user(self.current_user, current_password)
        if not user:
            messagebox.showerror("Lỗi", "Mật khẩu hiện tại không đúng!")
            return
        if self.db.update_password(self.current_user, new_password):
            messagebox.showinfo("Thành công", "Mật khẩu đã được cập nhật!")
            top.destroy()
        else:
            messagebox.showerror("Lỗi", "Không thể cập nhật mật khẩu. Vui lòng thử lại.")