import tkinter as tk
from tkinter import messagebox, ttk
from database import Database
import os

class AccountScreen:
    def __init__(self, root, username, callback):
        """Khởi tạo giao diện quản lý tài khoản."""
        self.root = root
        self.username = username
        self.callback = callback
        self.db = Database()
        self.root.title("TutorPay - Quản lý tài khoản")
        self.root.geometry("700x600")
        self.root.configure(bg="#F5F7FA")
        self.style = ttk.Style()
        self.configure_styles()
        self.set_window_icon(self.root)
        self.center_window()
        self.show_account_screen()

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
        self.root.geometry("700x600")
        self.root.grid_rowconfigure(0, weight=0)
        self.root.grid_columnconfigure(0, weight=0)
        self.root.update_idletasks()

    def create_button(self, frame, text, command, bg_color):
        """Tạo nút với hiệu ứng hover."""
        button = ttk.Button(frame, text=text, command=command, style="TButton")
        button.configure(cursor="hand2")
        button.bind("<Enter>", lambda e: button.configure(style="Hover.TButton"))
        button.bind("<Leave>", lambda e: button.configure(style="TButton"))
        button.pack(side="left", padx=5, pady=5)
        return button

    def toggle_password(self, entry, var):
        """Chuyển đổi giữa hiển thị và ẩn mật khẩu."""
        entry.config(show='' if var.get() else '*')

    def show_account_screen(self):
        """Hiển thị giao diện quản lý tài khoản."""
        self.clear_screen()
        self.root.geometry("700x600")
        main_frame = tk.Frame(self.root, bg="#F5F7FA")
        main_frame.pack(expand=True, fill="both", padx=15, pady=15)

        header_frame = tk.Frame(main_frame, bg="#F5F7FA")
        header_frame.pack(fill="x")
        ttk.Label(header_frame, text="Quản lý tài khoản", style="Header.TLabel").pack(pady=10)

        form_frame = tk.Frame(main_frame, bg="#FFFFFF", bd=0, relief="flat")
        form_frame.pack(fill="x", pady=10)
        form_frame.configure(highlightbackground="#E0E0E0", highlightthickness=1)

        ttk.Label(form_frame, text="Tên người dùng:").pack(side="left", padx=10, pady=5)
        self.username_entry = ttk.Entry(form_frame, style="TEntry")
        self.username_entry.pack(side="left", padx=5, pady=5, fill="x", expand=True)
        self.username_entry.bind("<Return>", lambda event: self.fullname_entry.focus_set())

        ttk.Label(form_frame, text="Họ và tên:").pack(side="left", padx=10, pady=5)
        self.fullname_entry = ttk.Entry(form_frame, style="TEntry")
        self.fullname_entry.pack(side="left", padx=5, pady=5, fill="x", expand=True)
        self.fullname_entry.bind("<Return>", lambda event: self.add_user())

        self.create_button(form_frame, "Thêm", self.add_user, "#43A047").pack(side="left", padx=10)

        tree_frame = tk.Frame(main_frame, bg="#FFFFFF")
        tree_frame.pack(expand=True, fill="both", pady=10)
        columns = ("ID", "Tên người dùng", "Họ và tên")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=8)
        self.tree.heading("ID", text="ID", anchor="center")
        self.tree.heading("Tên người dùng", text="Tên người dùng", anchor="center")
        self.tree.heading("Họ và tên", text="Họ và tên", anchor="center")
        self.tree.column("ID", width=100, anchor="center")
        self.tree.column("Tên người dùng", width=200, anchor="center")
        self.tree.column("Họ và tên", width=300, anchor="center")
        self.tree.pack(side="left", fill="both", expand=True)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        vsb.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=vsb.set)

        button_frame = tk.Frame(main_frame, bg="#F5F7FA")
        button_frame.pack(pady=10)
        self.create_button(button_frame, "Chỉnh sửa", self.show_edit_user_popup, "#1E88E5")
        self.create_button(button_frame, "Xóa", self.delete_user, "#EF5350")
        self.create_button(button_frame, "Quay lại", self.callback, "#78909C")

        self.load_users()
        self.center_window()

    def add_user(self):
        """Thêm tài khoản mới."""
        username = self.username_entry.get()
        fullname = self.fullname_entry.get()
        password = "123"
        if not username or not fullname:
            messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin.")
            return
        if self.db.add_user(username, fullname, password):
            messagebox.showinfo("Thành công", f"Đã thêm tài khoản {username} với mật khẩu mặc định '123'!")
            self.load_users()
            self.username_entry.delete(0, tk.END)
            self.fullname_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Lỗi", "Tên người dùng đã tồn tại hoặc không thể thêm tài khoản.")

    def load_users(self):
        """Tải danh sách tài khoản vào Treeview."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        users = self.db.get_all_users()
        for user in users:
            self.tree.insert("", tk.END, values=user)

    def show_edit_user_popup(self):
        """Hiển thị cửa sổ chỉnh sửa tài khoản."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Lỗi", "Vui lòng chọn tài khoản để chỉnh sửa.")
            return
        
        user_id = self.tree.item(selected_item)["values"][0]
        current_username = self.tree.item(selected_item)["values"][1]
        current_fullname = self.tree.item(selected_item)["values"][2]

        top = tk.Toplevel(self.root)
        top.title("Chỉnh sửa tài khoản")
        top.geometry("350x380")
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

        ttk.Label(frame, text="Tên người dùng:", background="#FFFFFF").pack(anchor="w", pady=5)
        username_entry = ttk.Entry(frame, style="TEntry")
        username_entry.pack(fill="x", pady=5)
        username_entry.insert(0, current_username)

        ttk.Label(frame, text="Họ và tên:", background="#FFFFFF").pack(anchor="w", pady=5)
        fullname_entry = ttk.Entry(frame, style="TEntry")
        fullname_entry.pack(fill="x", pady=5)
        fullname_entry.insert(0, current_fullname)

        ttk.Label(frame, text="Mật khẩu mới:", background="#FFFFFF").pack(anchor="w", pady=5)
        password_entry = ttk.Entry(frame, show='*', style="TEntry")
        password_entry.pack(fill="x", pady=5)

        show_password_var = tk.BooleanVar()
        show_password_check = ttk.Checkbutton(frame, text="Hiện mật khẩu", variable=show_password_var,
                                             command=lambda: self.toggle_password(password_entry, show_password_var),
                                             style="TCheckbutton")
        show_password_check.pack(anchor="w", padx=10, pady=5)

        button_frame = tk.Frame(frame, bg="#FFFFFF")
        button_frame.pack(pady=10)
        self.create_button(button_frame, "Lưu",
                          lambda: self.save_user(user_id, username_entry.get(), fullname_entry.get(), password_entry.get(), top),
                          "#1E88E5")

        username_entry.focus_set()
        username_entry.bind("<Return>", lambda event: fullname_entry.focus_set())
        fullname_entry.bind("<Return>", lambda event: password_entry.focus_set())
        password_entry.bind("<Return>", lambda event: self.save_user(user_id, username_entry.get(), fullname_entry.get(), password_entry.get(), top))

    def save_user(self, user_id, username, fullname, password, top):
        """Lưu thông tin tài khoản đã chỉnh sửa."""
        if not username or not fullname:
            messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin.")
            return
        password = password if password else "123"
        if self.db.update_user(user_id, username, fullname, password):
            messagebox.showinfo("Thành công", "Đã cập nhật tài khoản!")
            self.load_users()
            top.destroy()
        else:
            messagebox.showerror("Lỗi", "Không thể cập nhật tài khoản. Tên người dùng có thể đã tồn tại.")

    def delete_user(self):
        """Xóa tài khoản được chọn."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Lỗi", "Vui lòng chọn tài khoản để xóa.")
            return
        user_id = self.tree.item(selected_item)["values"][0]
        username = self.tree.item(selected_item)["values"][1]
        if username == 'admin':
            messagebox.showerror("Lỗi", "Không thể xóa tài khoản admin!")
            return
        if messagebox.askyesno("Xác nhận", f"Bạn có chắc chắn muốn xóa tài khoản {username}?"):
            if self.db.delete_user_by_id(user_id):
                messagebox.showinfo("Thành công", f"Đã xóa tài khoản {username}!")
                self.load_users()
            else:
                messagebox.showerror("Lỗi", "Không thể xóa tài khoản. Vui lòng thử lại.")