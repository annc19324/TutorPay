import tkinter as tk
from tkinter import messagebox, ttk
from database import Database
import os

class LearnerScreen:
    def __init__(self, root, username, callback):
        """Khởi tạo giao diện quản lý người học."""
        self.root = root
        self.username = username
        self.callback = callback
        self.db = Database()
        self.root.title("TutorPay - Quản lý người học")
        self.root.geometry("700x600")
        self.root.configure(bg="#F5F7FA")
        self.style = ttk.Style()
        self.configure_styles()
        self.set_window_icon(self.root)
        self.center_window()
        self.show_learner_screen()

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

    def show_learner_screen(self):
        """Hiển thị giao diện quản lý người học."""
        self.clear_screen()
        self.root.geometry("700x600")
        main_frame = tk.Frame(self.root, bg="#F5F7FA")
        main_frame.pack(expand=True, fill="both", padx=15, pady=15)

        header_frame = tk.Frame(main_frame, bg="#F5F7FA")
        header_frame.pack(fill="x")
        ttk.Label(header_frame, text="Quản lý người học", style="Header.TLabel").pack(pady=10)

        form_frame = tk.Frame(main_frame, bg="#FFFFFF", bd=0, relief="flat")
        form_frame.pack(fill="x", pady=10)
        form_frame.configure(highlightbackground="#E0E0E0", highlightthickness=1)

        ttk.Label(form_frame, text="Tên người học:").pack(side="left", padx=10, pady=5)
        self.learner_name_entry = ttk.Entry(form_frame, style="TEntry")
        self.learner_name_entry.pack(side="left", padx=5, pady=5, fill="x", expand=True)
        self.learner_name_entry.bind("<Return>", lambda event: self.add_learner())
        self.create_button(form_frame, "Thêm", self.add_learner, "#43A047").pack(side="left", padx=10)

        tree_frame = tk.Frame(main_frame, bg="#FFFFFF")
        tree_frame.pack(expand=True, fill="both", pady=10)
        columns = ("ID", "Tên người học")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=8)
        self.tree.heading("ID", text="ID", anchor="center")
        self.tree.heading("Tên người học", text="Tên người học", anchor="center")
        self.tree.column("ID", width=100, anchor="center")
        self.tree.column("Tên người học", width=400, anchor="center")
        self.tree.pack(side="left", fill="both", expand=True)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        vsb.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=vsb.set)

        button_frame = tk.Frame(main_frame, bg="#F5F7FA")
        button_frame.pack(pady=10)
        self.create_button(button_frame, "Chỉnh sửa", self.show_edit_learner_popup, "#1E88E5")
        self.create_button(button_frame, "Xóa", self.delete_learner, "#EF5350")
        self.create_button(button_frame, "Quay lại", self.callback, "#78909C")

        self.load_learners()
        self.center_window()

    def add_learner(self):
        """Thêm người học mới."""
        name = self.learner_name_entry.get()
        if not name:
            messagebox.showerror("Lỗi", "Vui lòng nhập tên người học.")
            return
        if self.db.add_learner(self.username, name):
            messagebox.showinfo("Thành công", "Đã thêm người học!")
            self.load_learners()
            self.learner_name_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Lỗi", "Không thể thêm người học. Vui lòng thử lại.")

    def load_learners(self):
        """Tải danh sách người học vào Treeview."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        learners = self.db.get_learners(self.username)
        for learner in learners:
            self.tree.insert("", tk.END, values=learner)

    def show_edit_learner_popup(self):
        """Hiển thị cửa sổ chỉnh sửa tên người học."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Lỗi", "Vui lòng chọn người học để chỉnh sửa.")
            return
        
        learner_id = self.tree.item(selected_item)["values"][0]
        current_name = self.tree.item(selected_item)["values"][1]

        top = tk.Toplevel(self.root)
        top.title("Chỉnh sửa người học")
        top.geometry("350x200")
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

        ttk.Label(frame, text="Tên người học:", background="#FFFFFF").pack(anchor="w", pady=5)
        name_entry = ttk.Entry(frame, style="TEntry")
        name_entry.pack(fill="x", pady=5)
        name_entry.insert(0, current_name)

        button_frame = tk.Frame(frame, bg="#FFFFFF")
        button_frame.pack(pady=10)
        self.create_button(button_frame, "Lưu",
                          lambda: self.save_new_name(learner_id, name_entry.get(), top),
                          "#1E88E5")

        name_entry.focus_set()
        name_entry.bind("<Return>", lambda event: self.save_new_name(learner_id, name_entry.get(), top))

    def save_new_name(self, learner_id, new_name, top):
        """Lưu tên người học đã chỉnh sửa."""
        if not new_name:
            messagebox.showerror("Lỗi", "Vui lòng nhập tên người học.")
            return
        self.db.update_learner(learner_id, new_name)
        messagebox.showinfo("Thành công", "Đã cập nhật người học!")
        self.load_learners()
        top.destroy()

    def delete_learner(self):
        """Xóa người học được chọn."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Lỗi", "Vui lòng chọn người học để xóa.")
            return
        learner_id = self.tree.item(selected_item)["values"][0]
        if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xóa người học này?"):
            self.db.delete_learner(learner_id)
            messagebox.showinfo("Thành công", "Đã xóa người học!")
            self.load_learners()