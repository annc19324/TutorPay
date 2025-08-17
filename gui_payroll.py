import tkinter as tk
from tkinter import messagebox, ttk
import pytz
from datetime import datetime
import logging
import os
from database import Database
from utils import get_weeks_in_month, format_currency
from pdf_utils import export_to_pdf

class PayrollScreen:
    def __init__(self, root, username, back_callback):
        """Khởi tạo giao diện quản lý bảng lương."""
        self.root = root
        self.username = username
        self.back_callback = back_callback
        self.db = Database()
        self.root.title("TutorPay - Quản lý bảng lương")
        self.root.geometry("700x600")
        self.root.configure(bg="#F5F7FA")
        self.current_month = None
        self.current_year = None
        self.current_learner_id = None
        self.checkbuttons = []
        self.payrolls = []
        self.create_form_visible = False
        self.create_form_container = None
        self.style = ttk.Style()
        self.configure_styles()
        self.set_window_icon(self.root)
        self.center_window()
        self.show_payroll_list()

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

    def show_payroll_list(self):
        """Hiển thị danh sách bảng lương với khả năng tìm kiếm."""
        self.clear_screen()
        self.root.geometry("700x600")
        main_frame = tk.Frame(self.root, bg="#F5F7FA")
        main_frame.pack(expand=True, fill="both", padx=15, pady=15)

        header_frame = tk.Frame(main_frame, bg="#F5F7FA")
        header_frame.pack(fill="x")
        ttk.Label(header_frame, text="Quản lý bảng lương", style="Header.TLabel").pack(pady=10)

        search_frame = tk.Frame(main_frame, bg="#FFFFFF", bd=0, relief="flat")
        search_frame.pack(fill="x", pady=10)
        search_frame.configure(highlightbackground="#E0E0E0", highlightthickness=1)
        ttk.Label(search_frame, text="Tìm kiếm:").pack(side="left", padx=10, pady=5)
        search_entry = ttk.Entry(search_frame, style="TEntry")
        search_entry.pack(side="left", padx=5, pady=5, fill="x", expand=True)
        search_entry.bind("<KeyRelease>", lambda e: self.filter_payrolls(search_entry.get()))
        search_entry.focus_set()

        tree_frame = tk.Frame(main_frame, bg="#FFFFFF")
        tree_frame.pack(expand=True, fill="both", pady=10)
        self.tree = ttk.Treeview(tree_frame, columns=("Learner", "Month", "Year"), show="headings", height=8)
        self.tree.heading("Learner", text="Người học", anchor="center")
        self.tree.heading("Month", text="Tháng", anchor="center")
        self.tree.heading("Year", text="Năm", anchor="center")
        self.tree.column("Learner", width=300, anchor="center")
        self.tree.column("Month", width=100, anchor="center")
        self.tree.column("Year", width=100, anchor="center")
        self.tree.pack(side="left", fill="both", expand=True)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        vsb.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=vsb.set)

        hsb = ttk.Scrollbar(main_frame, orient="horizontal", command=self.tree.xview)
        hsb.pack(fill="x")
        self.tree.configure(xscrollcommand=hsb.set)

        self.payrolls = self.db.get_payrolls(self.username)
        if not self.payrolls:
            logging.info(f"Không tìm thấy bảng lương cho người dùng {self.username}")
        self.update_tree(self.payrolls)

        self.create_form_container = tk.Frame(main_frame, bg="#F5F7FA")
        self.create_form_container.pack(pady=5, fill="x")

        button_frame = tk.Frame(main_frame, bg="#F5F7FA")
        button_frame.pack(pady=10)
        self.create_button(button_frame, "Thêm", self.toggle_create_form, "#43A047")
        self.create_button(button_frame, "Xem", self.view_payroll, "#1E88E5")
        self.create_button(button_frame, "Xóa", self.delete_payroll, "#EF5350")
        self.create_button(button_frame, "Quay lại", self.back_callback, "#78909C")

        self.center_window()

    def update_tree(self, payrolls):
        """Cập nhật danh sách bảng lương trong Treeview."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        for month, year, learner_name, learner_id in payrolls:
            self.tree.insert("", "end", values=(learner_name, month, year), tags=(learner_id, month, year))

    def filter_payrolls(self, query):
        """Lọc danh sách bảng lương dựa trên từ khóa tìm kiếm."""
        query = query.lower()
        filtered = [(m, y, ln, lid) for m, y, ln, lid in self.payrolls if query in ln.lower() or query in f"{m}/{y}"]
        self.update_tree(filtered)

    def toggle_create_form(self):
        """Hiển thị hoặc ẩn form tạo bảng lương mới."""
        if self.create_form_visible:
            self.create_form_container.pack_forget()
            self.create_form_container = tk.Frame(self.root.winfo_children()[0], bg="#F5F7FA")
            self.create_form_container.pack(pady=5, fill="x")
            self.create_form_visible = False
        else:
            self.create_form_container.pack_forget()
            self.create_form_container = tk.Frame(self.root.winfo_children()[0], bg="#F5F7FA")
            self.create_form_container.pack(pady=5, fill="x")
            top = tk.Toplevel(self.root)
            top.title("Thêm Bảng Lương Mới")
            top.geometry("350x400")
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

            ttk.Label(frame, text="Thêm bảng lương mới", style="Header.TLabel").pack(pady=10)

            learners = self.db.get_learners(self.username)
            ttk.Label(frame, text="Người học:", background="#FFFFFF").pack(anchor="w", pady=5)
            learner_combo = ttk.Combobox(frame, values=[name for _, name in learners], state="readonly", style="TCombobox")
            learner_combo.pack(fill="x", pady=5)
            learner_combo.focus_set()

            ttk.Label(frame, text="Tháng:", background="#FFFFFF").pack(anchor="w", pady=5)
            vn_time = datetime.now(pytz.timezone('Asia/Ho_Chi_Minh'))
            current_month = vn_time.month
            current_year = vn_time.year
            month_combo = ttk.Combobox(frame, values=list(range(1, 13)), state="readonly", style="TCombobox")
            month_combo.set(current_month)
            month_combo.pack(fill="x", pady=5)

            ttk.Label(frame, text="Năm:", background="#FFFFFF").pack(anchor="w", pady=5)
            year_combo = ttk.Combobox(frame, values=list(range(2020, 2031)), state="readonly", style="TCombobox")
            year_combo.set(current_year)
            year_combo.pack(fill="x", pady=5)

            button_frame = tk.Frame(frame, bg="#FFFFFF")
            button_frame.pack(pady=10)
            self.create_button(button_frame, "Thêm",
                              lambda: self.create_payroll(learner_combo.get(), month_combo.get(), year_combo.get(), top),
                              "#43A047")

            learner_combo.bind("<Return>", lambda event: month_combo.focus_set())
            month_combo.bind("<Return>", lambda event: year_combo.focus_set())
            year_combo.bind("<Return>", lambda event: self.create_payroll(learner_combo.get(), month_combo.get(), year_combo.get(), top))
            self.create_form_visible = True

    def create_payroll(self, learner_name, month, year, top):
        """Tạo bảng lương mới."""
        try:
            month, year = int(month), int(year)
            learners = self.db.get_learners(self.username)
            learner_id = next((lid for lid, lname in learners if lname == learner_name), None)
            if not learner_id:
                messagebox.showerror("Lỗi", "Chọn người học hợp lệ.")
                return
            if self.db.create_payroll(self.username, month, year, learner_id):
                messagebox.showinfo("Thành công", f"Đã thêm bảng lương {month}/{year}!")
                top.destroy()
                self.show_payroll(month, year, learner_id)
            else:
                messagebox.showerror("Lỗi", f"Bảng lương {month}/{year} đã tồn tại.")
        except ValueError:
            messagebox.showerror("Lỗi", "Tháng hoặc năm không hợp lệ.")

    def view_payroll(self):
        """Xem chi tiết bảng lương được chọn."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Lỗi", "Chọn một bảng lương để xem.")
            return
        item = self.tree.selection()[0]
        learner_id, month, year = self.tree.item(item, "tags")
        learner_id, month, year = int(learner_id), int(month), int(year)
        logging.info(f"Đang xem bảng lương: learner_id={learner_id}, month={month}, year={year}")
        self.show_payroll(month, year, learner_id)

    def show_payroll(self, month, year, learner_id):
        """Hiển thị chi tiết bảng lương với lưới tuần."""
        self.current_month, self.current_year, self.current_learner_id = month, year, learner_id
        self.clear_screen()
        self.root.geometry("700x600")
        main_frame = tk.Frame(self.root, bg="#F5F7FA")
        main_frame.pack(expand=True, fill="both", padx=15, pady=15)

        learner_name = next((name for lid, name in self.db.get_learners(self.username) if lid == learner_id), "Không xác định")
        ttk.Label(main_frame, text=f"Bảng Lương {month}/{year} - {learner_name}", style="Header.TLabel").pack(pady=10)

        grid_frame = tk.Frame(main_frame, bg="#FFFFFF", bd=0, relief="flat")
        grid_frame.pack(pady=10, fill="both", expand=True)
        grid_frame.configure(highlightbackground="#E0E0E0", highlightthickness=1)

        days_of_week = ["T2", "T3", "T4", "T5", "T6", "T7", "CN"]
        for col, day in enumerate(days_of_week, 1):
            tk.Label(grid_frame, text=day, font=("Segoe UI", 11, "bold"), bg="#FFFFFF", width=8, borderwidth=1, relief="solid").grid(row=0, column=col, padx=1, pady=1, sticky="nsew")

        weeks = get_weeks_in_month(year, month)
        self.checkbuttons = []
        row = 1
        for week in weeks:
            tk.Label(grid_frame, text=f"Tuần {row}", font=("Segoe UI", 11), bg="#FFFFFF", width=8, borderwidth=1, relief="solid").grid(row=row, column=0, padx=1, pady=1, sticky="nsew")
            for col, day in enumerate(week, 1):
                if day:
                    checked = next((d[1] for d in self.db.get_payroll_data(self.username, month, year, learner_id) if d[0] == day), 0)
                    var = tk.BooleanVar(value=bool(checked))
                    cb = tk.Checkbutton(grid_frame, text=day, font=("Segoe UI", 11), variable=var,
                                        command=lambda d=day, v=var: self.update_day(d, v.get()),
                                        state="normal" if max(d[2] for d in self.db.get_payroll_data(self.username, month, year, learner_id)) > 0 else "disabled", bg="#FFFFFF")
                    cb.grid(row=row, column=col, padx=1, pady=1, sticky="nsew")
                    self.checkbuttons.append((day, var, cb))
                else:
                    tk.Label(grid_frame, text="", font=("Segoe UI", 11), bg="#FFFFFF", width=8, borderwidth=0, relief="flat").grid(row=row, column=col, padx=1, pady=1, sticky="nsew")
            row += 1

        for i in range(len(days_of_week) + 1):
            grid_frame.grid_columnconfigure(i, weight=1, uniform="column")
        for i in range(len(weeks) + 1):
            grid_frame.grid_rowconfigure(i, weight=1)

        summary_frame = tk.Frame(main_frame, bg="#FFFFFF")
        summary_frame.pack(pady=10, fill="x")
        sessions, fee = self.db.get_payroll_summary(self.username, month, year, learner_id)
        self.sessions_label = ttk.Label(summary_frame, text=f"Tổng buổi: {sessions}", font=("Segoe UI", 11))
        self.sessions_label.pack(pady=5)
        self.fee_label = ttk.Label(summary_frame, text=f"Phí: {format_currency(fee)}", font=("Segoe UI", 11))
        self.fee_label.pack(pady=5)

        button_frame = tk.Frame(main_frame, bg="#F5F7FA")
        button_frame.pack(pady=10)
        self.create_button(button_frame, "Cập nhật lương", self.show_update_salary_popup, "#1E88E5")
        self.create_button(button_frame, "Xuất PDF", self.export_pdf, "#43A047")
        self.create_button(button_frame, "Quay lại", self.show_payroll_list, "#78909C")

        self.center_window()

    def update_day(self, day, checked):
        """Cập nhật trạng thái điểm danh và tính lại tóm tắt."""
        default_salary = max(d[2] for d in self.db.get_payroll_data(self.username, self.current_month, self.current_year, self.current_learner_id))
        salary = default_salary if checked else 0
        if self.db.update_day(self.username, self.current_month, self.current_year, self.current_learner_id, day, checked, salary):
            data = self.db.get_payroll_data(self.username, self.current_month, self.current_year, self.current_learner_id)
            sessions = sum(1 for d in data if d[1])
            fee = sessions * default_salary
            self.db.update_payroll_summary(self.username, self.current_month, self.current_year, self.current_learner_id, sessions, fee)
            self.sessions_label.config(text=f"Tổng buổi: {sessions}")
            self.fee_label.config(text=f"Phí: {format_currency(fee)}")

    def show_update_salary_popup(self):
        """Hiển thị cửa sổ cập nhật lương mặc định."""
        top = tk.Toplevel(self.root)
        top.title("Cập nhật lương")
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

        ttk.Label(frame, text="Lương mặc định (VNĐ):", background="#FFFFFF").pack(anchor="w", pady=5)
        salary_entry = ttk.Entry(frame, style="TEntry")
        salary_entry.pack(fill="x", pady=5)
        salary_entry.focus_set()

        button_frame = tk.Frame(frame, bg="#FFFFFF")
        button_frame.pack(pady=10)
        self.create_button(button_frame, "Lưu",
                          lambda: self.save_salary(salary_entry.get(), top),
                          "#1E88E5")

        salary_entry.bind("<Return>", lambda event: self.save_salary(salary_entry.get(), top))

    def save_salary(self, salary, top):
        """Lưu lương mặc định và cập nhật dữ liệu."""
        try:
            salary = int(salary.replace(".", "").replace(",", ""))
            if salary < 0:
                messagebox.showerror("Lỗi", "Lương phải không âm.")
                return
            if self.db.update_default_salary(self.username, self.current_month, self.current_year, self.current_learner_id, salary):
                messagebox.showinfo("Thành công", "Lương đã được cập nhật!")
                top.destroy()
                for _, var, cb in self.checkbuttons:
                    cb.config(state="normal" if salary > 0 else "disabled")
                data = self.db.get_payroll_data(self.username, self.current_month, self.current_year, self.current_learner_id)
                for day, checked, _ in data:
                    if checked:
                        self.db.update_day(self.username, self.current_month, self.current_year, self.current_learner_id, day, checked, salary)
                sessions = sum(1 for d in data if d[1])
                fee = sessions * salary
                self.db.update_payroll_summary(self.username, self.current_month, self.current_year, self.current_learner_id, sessions, fee)
                self.show_payroll(self.current_month, self.current_year, self.current_learner_id)
        except ValueError:
            messagebox.showerror("Lỗi", "Lương phải là số.")

    def export_pdf(self):
        """Xuất bảng lương ra file PDF."""
        try:
            # Làm mới dữ liệu trước khi xuất
            data = self.db.get_payroll_data(self.username, self.current_month, self.current_year, self.current_learner_id)
            sessions, fee = self.db.get_payroll_summary(self.username, self.current_month, self.current_year, self.current_learner_id)
            logging.info(f"Dữ liệu bảng lương: {data}, Tổng buổi: {sessions}, Tổng phí: {fee}")
            if not data:
                messagebox.showerror("Lỗi", "Không có dữ liệu bảng lương để xuất. Vui lòng kiểm tra bảng lương.")
                return
            learner_name = next((name for lid, name in self.db.get_learners(self.username) if lid == self.current_learner_id), "Không xác định")
            # Truyền thêm sessions và fee để đảm bảo đồng bộ
            success, filename = export_to_pdf(self.username, self.current_month, self.current_year, data, learner_name, self.current_learner_id, sessions, fee)
            if success:
                messagebox.showinfo("Thành công", f"Đã xuất PDF tại: {filename}")
            else:
                messagebox.showerror("Lỗi", "Không thể xuất PDF. Vui lòng kiểm tra logs/app.log hoặc thử chọn thư mục khác.")
        except Exception as e:
            logging.error(f"Lỗi khi xuất PDF: {str(e)}")
            messagebox.showerror("Lỗi", f"Đã xảy ra lỗi khi xuất PDF: {str(e)}. Vui lòng kiểm tra logs/app.log.")

    def delete_payroll(self):
        """Xóa bảng lương được chọn."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Lỗi", "Chọn một bảng lương để xóa.")
            return
        item = self.tree.selection()[0]
        learner_id, month, year = self.tree.item(item, "tags")
        learner_id, month, year = int(learner_id), int(month), int(year)
        logging.info(f"Đang xóa bảng lương: learner_id={learner_id}, month={month}, year={year}")

        if messagebox.askyesno("Xác nhận", f"Xóa bảng lương {month}/{year}?"):
            if self.db.delete_payroll(self.username, month, year, learner_id):
                messagebox.showinfo("Thành công", f"Bảng lương {month}/{year} đã được xóa!")
                self.show_payroll_list()
            else:
                logging.error(f"Không thể xóa bảng lương: learner_id={learner_id}, month={month}, year={year}")
                messagebox.showerror("Lỗi", "Không thể xóa bảng lương. Vui lòng kiểm tra logs/app.log.")