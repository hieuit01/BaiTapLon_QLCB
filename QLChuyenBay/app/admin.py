from app import db, app, dao
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from app.models import SanBay, TuyenBay, LichChuyenBay, QuyDinh, User, UserRole, ChuyenBay
from flask_login import current_user, logout_user
from flask_admin import BaseView, expose
from flask import redirect, request, flash
from datetime import datetime

# class MyAdminIndexView(AdminIndexView):
#     @expose("/")
#     def index(self):
#         return self.render('admin/index.html', stats=dao.stats_flights())

admin = Admin(app, name='Flight Management', template_mode='bootstrap4')

class AuthenticatedView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role.__eq__(UserRole.ADMIN)

class UserView(AuthenticatedView):
    column_searchable_list = ['id', 'user_role', 'username']
    column_filters = ['user_role']
    can_view_details = True

class SanBayView(AuthenticatedView):
    column_searchable_list = ['ma_san_bay', 'ten_san_bay']
    column_filters = ['ma_san_bay', 'ten_san_bay']
    can_view_details = True


class LichChuyenBayView(AuthenticatedView):
    # Thêm formatters để hiển thị ngày theo định dạng mong muốn
    column_formatters = {
        'ngay_gio_khoi_hanh': lambda v, c, m, p: m.ngay_gio_khoi_hanh.strftime('%Y-%m-%d') if m.ngay_gio_khoi_hanh else ''
    }

    # Tìm kiếm và lọc dữ liệu
    column_searchable_list = ['ma_chuyen_bay']
    column_filters = ['ma_chuyen_bay', 'ngay_gio_khoi_hanh']
    can_view_details = True
    can_export = True

    # Chỉ định các trường được hiển thị trong form
    form_columns = ['ngay_gio_khoi_hanh', 'thoi_gian_bay_gio_phut', 'so_ghe_hang_1', 'so_ghe_hang_2', 'ma_chuyen_bay']

    # Tạo danh sách mã chuyến bay để hiển thị dưới dạng dropdown
    form_choices = {
        'ma_chuyen_bay': [(c.ma_chuyen_bay, f"{c.ma_chuyen_bay} - {c.ma_tuyen_bay}") for c in db.session.query(ChuyenBay).all()]
    }


class QuyDinhView(AuthenticatedView):
    column_formatters = {
        'thoi_gian_bay_toi_thieu': lambda v, c, m, p: m.thoi_gian_bay_toi_thieu.strftime(
            '%H:%M:%S') if m.thoi_gian_bay_toi_thieu else '',
        'thoi_gian_dung_toi_thieu': lambda v, c, m, p: m.thoi_gian_dung_toi_thieu.strftime(
            '%H:%M:%S') if m.thoi_gian_dung_toi_thieu else '',
        'so_gio_dat_ve_truoc': lambda v, c, m, p: m.so_gio_dat_ve_truoc.strftime(
            '%H:%M:%S') if m.so_gio_dat_ve_truoc else '',
        'so_gio_ban_ve_truoc': lambda v, c, m, p: m.so_gio_ban_ve_truoc.strftime(
            '%H:%M:%S') if m.so_gio_ban_ve_truoc else '',
    }
    column_list = ['so_luong_san_bay', 'thoi_gian_bay_toi_thieu', 'so_san_bay_trung_gian_toi_da', 'thoi_gian_dung_toi_thieu', 'thoi_gian_dung_toi_da', 'so_gio_dat_ve_truoc', 'so_gio_ban_ve_truoc']
    can_edit = True
    can_view_details = True


class MyView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated

class LogoutView(MyView):
    @expose("/")
    def index(self):
        logout_user()
        return redirect('/admin')



class StatsView(MyView):
    @expose("/", methods=["GET", "POST"])
    def index(self):
        # Lấy tháng và năm từ form, mặc định là tháng và năm hiện tại
        selected_month = request.form.get('month') or datetime.now().strftime('%Y-%m')

        try:
            # Tách năm và tháng từ giá trị `selected_month`
            selected_year, month = map(int, selected_month.split('-'))
        except (ValueError, IndexError):
            # Xử lý lỗi nếu giá trị không hợp lệ
            flash('Dữ liệu tháng không hợp lệ.', 'danger')
            return self.render('admin/stats.html', stats=None, selected_month=None)

        # Gọi hàm thống kê doanh thu theo tháng và năm
        stats = dao.revenue_stats_by_period(p='month', year=selected_year, month=month)

        # Kiểm tra nếu không có kết quả trả về
        if not stats:
            flash('Không có dữ liệu cho tháng và năm đã chọn.', 'warning')

        # Render template với dữ liệu thống kê
        return self.render(
            'admin/stats.html',
            stats=stats,
            selected_month=selected_month
        )


admin.add_view(SanBayView(SanBay, db.session))
admin.add_view(LichChuyenBayView(LichChuyenBay, db.session))
admin.add_view(QuyDinhView(QuyDinh, db.session))
admin.add_view(UserView(User, db.session))
admin.add_view(LogoutView(name='Đăng xuất'))
admin.add_view(StatsView(name='Thống kê - báo cáo', endpoint='stats'))


