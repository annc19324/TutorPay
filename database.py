import sqlite3
import os
from pathlib import Path
import logging
from calendar import monthrange

# Thiết lập logging để ghi lại các sự kiện và lỗi
log_dir = os.path.join(Path.home(), "AppData", "Local", "TutorPay", "logs")
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(log_dir, "app.log"),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

class Database:
    def __init__(self):
        """Khởi tạo kết nối cơ sở dữ liệu và tạo thư mục lưu trữ."""
        app_data_dir = os.path.join(Path.home(), "AppData", "Local", "TutorPay")
        os.makedirs(app_data_dir, exist_ok=True)
        self.conn = sqlite3.connect(os.path.join(app_data_dir, "tutorpay.db"))
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        """Tạo các bảng trong cơ sở dữ liệu nếu chưa tồn tại."""
        cursor = self.conn.cursor()
        # Bảng users: lưu thông tin người dùng
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                fullname TEXT NOT NULL,
                password TEXT NOT NULL
            )
        ''')

        # Tạo tài khoản admin mặc định
        cursor.execute('''
            INSERT OR IGNORE INTO users (username, fullname, password)
            VALUES (?, ?, ?)
        ''', ('admin', 'Administrator', '123'))
        
        # Bảng learners: lưu thông tin người học
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learners (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                username TEXT,
                FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
            )
        ''')

        # Bảng payroll: lưu chi tiết bảng lương (ngày, trạng thái điểm danh, lương mỗi ngày)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payroll (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                month INTEGER,
                year INTEGER,
                learner_id INTEGER,
                day TEXT,
                checked INTEGER,
                salary INTEGER DEFAULT 0,
                UNIQUE(username, month, year, learner_id, day),
                FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE,
                FOREIGN KEY (learner_id) REFERENCES learners(id) ON DELETE CASCADE
            )
        ''')

        # Bảng payroll_sum: lưu tóm tắt bảng lương (tổng buổi, tổng phí)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payroll_sum (
                username TEXT,
                month INTEGER,
                year INTEGER,
                learner_id INTEGER,
                sessions INTEGER,
                fee INTEGER DEFAULT 0,
                UNIQUE(username, month, year, learner_id),
                FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE,
                FOREIGN KEY (learner_id) REFERENCES learners(id) ON DELETE CASCADE
            )
        ''')
        self.conn.commit()
        logging.info("Cơ sở dữ liệu đã được tạo và tài khoản admin được khởi tạo.")

    def register_user(self, username, fullname, password):
        """Đăng ký người dùng mới."""
        try:
            self.cursor.execute('''
                INSERT INTO users (username, fullname, password)
                VALUES (?, ?, ?)
            ''', (username, fullname, password))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def login_user(self, username, password):
        """Xác thực đăng nhập người dùng."""
        self.cursor.execute('''
            SELECT username, fullname FROM users WHERE username = ? AND password = ?
        ''', (username, password))
        return self.cursor.fetchone()

    def add_learner(self, username, name):
        """Thêm người học mới cho người dùng."""
        try:
            self.cursor.execute("INSERT INTO learners (name, username) VALUES (?, ?)", (name, username))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_learners(self, username):
        """Lấy danh sách người học của người dùng."""
        self.cursor.execute('SELECT id, name FROM learners WHERE username = ?', (username,))
        return self.cursor.fetchall()

    def update_learner(self, learner_id, name):
        """Cập nhật tên người học."""
        self.cursor.execute('UPDATE learners SET name = ? WHERE id = ?', (name, learner_id))
        self.conn.commit()

    def delete_learner(self, learner_id):
        """Xóa người học."""
        self.cursor.execute('DELETE FROM learners WHERE id = ?', (learner_id,))
        self.conn.commit()

    def create_payroll(self, username, month, year, learner_id):
        """Tạo bảng lương mới cho người học trong tháng/năm cụ thể."""
        try:
            self.cursor.execute("SELECT id FROM payroll WHERE username = ? AND month = ? AND year = ? AND learner_id = ?",
                               (username, month, year, learner_id))
            if self.cursor.fetchone():
                return False
            _, days = monthrange(year, month)
            for day in range(1, days + 1):
                day_str = f"{day}/{month}"
                self.cursor.execute("INSERT INTO payroll (username, month, year, learner_id, day, checked, salary) "
                                   "VALUES (?, ?, ?, ?, ?, ?, ?)",
                                   (username, month, year, learner_id, day_str, 0, 0))
            self.cursor.execute("INSERT OR REPLACE INTO payroll_sum (username, month, year, learner_id, sessions, fee) "
                               "VALUES (?, ?, ?, ?, ?, ?)",
                               (username, month, year, learner_id, 0, 0))
            self.conn.commit()
            logging.info(f"Đã tạo bảng lương cho {username} - {month}/{year} - Người học ID: {learner_id}")
            return True
        except sqlite3.Error as e:
            logging.error(f"Lỗi khi tạo bảng lương: {e}")
            return False

    def get_payrolls(self, username):
        """Lấy danh sách bảng lương của người dùng."""
        self.cursor.execute('''
            SELECT DISTINCT p.month, p.year, l.name, p.learner_id
            FROM payroll p
            JOIN learners l ON p.learner_id = l.id
            WHERE p.username = ?
            ORDER BY p.year DESC, p.month DESC
        ''', (username,))
        return self.cursor.fetchall()

    def get_payroll_data(self, username, month, year, learner_id):
        """Lấy chi tiết bảng lương (ngày, trạng thái điểm danh, lương)."""
        self.cursor.execute("SELECT day, checked, salary FROM payroll WHERE username = ? AND month = ? AND year = ? AND learner_id = ?",
                           (username, month, year, learner_id))
        return self.cursor.fetchall()

    def get_payroll_summary(self, username, month, year, learner_id):
        """Lấy tóm tắt bảng lương (tổng buổi, tổng phí)."""
        self.cursor.execute("SELECT sessions, fee FROM payroll_sum WHERE username = ? AND month = ? AND year = ? AND learner_id = ?",
                           (username, month, year, learner_id))
        result = self.cursor.fetchone()
        return result if result else (0, 0)

    def update_day(self, username, month, year, learner_id, day, checked, salary):
        """Cập nhật trạng thái điểm danh và lương cho một ngày cụ thể."""
        try:
            self.cursor.execute("UPDATE payroll SET checked = ?, salary = ? WHERE username = ? AND month = ? AND year = ? AND learner_id = ? AND day = ?",
                               (checked, salary, username, month, year, learner_id, day))
            self.conn.commit()
            logging.info(f"Ngày {day} được cập nhật cho {username} - {month}/{year} - Người học ID: {learner_id}")
            return True
        except sqlite3.Error as e:
            logging.error(f"Lỗi khi cập nhật ngày: {e}")
            return False

    def update_default_salary(self, username, month, year, learner_id, salary):
        """Cập nhật lương mặc định cho tất cả các ngày trong bảng lương."""
        try:
            self.cursor.execute("UPDATE payroll SET salary = ? WHERE username = ? AND month = ? AND year = ? AND learner_id = ?",
                               (salary, username, month, year, learner_id))
            self.conn.commit()
            logging.info(f"Lương mặc định cập nhật: {salary} cho {username} - {month}/{year} - Người học ID: {learner_id}")
            return True
        except sqlite3.Error as e:
            logging.error(f"Lỗi khi cập nhật lương mặc định: {e}")
            return False

    def update_payroll_summary(self, username, month, year, learner_id, sessions, fee):
        """Cập nhật tóm tắt bảng lương (tổng buổi, tổng phí)."""
        try:
            self.cursor.execute("INSERT OR REPLACE INTO payroll_sum (username, month, year, learner_id, sessions, fee) "
                               "VALUES (?, ?, ?, ?, ?, ?)",
                               (username, month, year, learner_id, sessions, fee))
            self.conn.commit()
            logging.info(f"Tóm tắt bảng lương cập nhật: {sessions} buổi, {fee} phí cho {username} - {month}/{year} - Người học ID: {learner_id}")
            return True
        except sqlite3.Error as e:
            logging.error(f"Lỗi khi cập nhật tóm tắt bảng lương: {e}")
            return False

    def delete_payroll(self, username, month, year, learner_id):
        """Xóa bảng lương và tóm tắt liên quan."""
        try:
            self.cursor.execute("DELETE FROM payroll WHERE username = ? AND month = ? AND year = ? AND learner_id = ?",
                               (username, month, year, learner_id))
            self.cursor.execute("DELETE FROM payroll_sum WHERE username = ? AND month = ? AND year = ? AND learner_id = ?",
                               (username, month, year, learner_id))
            self.conn.commit()
            logging.info(f"Bảng lương {month}/{year} đã xóa cho {username} - Người học ID: {learner_id}")
            return True
        except sqlite3.Error as e:
            logging.error(f"Lỗi khi xóa bảng lương: {e}")
            return False

    def delete_user(self, username):
        """Xóa người dùng và toàn bộ dữ liệu liên quan."""
        try:
            self.cursor.execute("DELETE FROM users WHERE username = ?", (username,))
            self.conn.commit()
            logging.info(f"Đã xóa người dùng {username} và dữ liệu liên quan.")
            return True
        except sqlite3.Error as e:
            logging.error(f"Lỗi khi xóa người dùng {username}: {e}")
            return False

    def update_password(self, username, new_password):
        """Cập nhật mật khẩu cho người dùng."""
        try:
            self.cursor.execute("UPDATE users SET password = ? WHERE username = ?",
                               (new_password, username))
            self.conn.commit()
            logging.info(f"Đã cập nhật mật khẩu cho người dùng {username}.")
            return True
        except sqlite3.Error as e:
            logging.error(f"Lỗi khi cập nhật mật khẩu cho {username}: {e}")
            return False

    def get_all_users(self):
        """Lấy danh sách tất cả người dùng."""
        self.cursor.execute('SELECT id, username, fullname FROM users')
        return self.cursor.fetchall()

    def add_user(self, username, fullname, password):
        """Thêm người dùng mới (dành cho admin)."""
        try:
            self.cursor.execute('''
                INSERT INTO users (username, fullname, password)
                VALUES (?, ?, ?)
            ''', (username, fullname, password))
            self.conn.commit()
            logging.info(f"Đã thêm người dùng {username} bởi admin.")
            return True
        except sqlite3.IntegrityError:
            logging.error(f"Tên người dùng {username} đã tồn tại.")
            return False

    def update_user(self, user_id, username, fullname, password):
        """Cập nhật thông tin người dùng (dành cho admin)."""
        try:
            self.cursor.execute('''
                UPDATE users SET username = ?, fullname = ?, password = ? WHERE id = ?
            ''', (username, fullname, password, user_id))
            self.conn.commit()
            logging.info(f"Đã cập nhật người dùng ID {user_id}.")
            return True
        except sqlite3.IntegrityError:
            logging.error(f"Tên người dùng {username} đã tồn tại khi cập nhật.")
            return False
        except sqlite3.Error as e:
            logging.error(f"Lỗi khi cập nhật người dùng ID {user_id}: {e}")
            return False

    def delete_user_by_id(self, user_id):
        """Xóa người dùng theo ID (dành cho admin)."""
        try:
            self.cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            self.conn.commit()
            logging.info(f"Đã xóa người dùng ID {user_id} bởi admin.")
            return True
        except sqlite3.Error as e:
            logging.error(f"Lỗi khi xóa người dùng ID {user_id}: {e}")
            return False

    def __del__(self):
        """Đóng kết nối cơ sở dữ liệu khi đối tượng bị hủy."""
        self.conn.close()