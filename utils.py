from calendar import monthrange, weekday

def format_currency(amount):
    """Định dạng số tiền thành chuỗi với đơn vị VNĐ (ví dụ: 120.000 VNĐ)."""
    return f"{amount:,.0f} VNĐ".replace(",", ".")

def get_weeks_in_month(year, month):
    """Tạo danh sách các tuần trong tháng, mỗi ngày định dạng 'ngày/tháng'."""
    _, days = monthrange(year, month)
    weeks = []
    current_week = [None] * 7
    for day in range(1, days + 1):
        wday = weekday(year, month, day)
        current_week[wday] = f"{day}/{month}"
        if wday == 6 or day == days:
            weeks.append(current_week)
            current_week = [None] * 7
    return weeks