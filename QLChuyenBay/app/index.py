from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db, login
from app.models import UserRole, LichChuyenBay, DatVeChuyenBay, VeChuyenBay, ThanhToan, TrangThaiThanhToan, PTTT, User
from datetime import datetime
from flask_login import LoginManager
import json, logging
import dao

login_manager = LoginManager(app)
login_manager.login_view = 'login_process'
login_manager.login_message = "Vui lòng đăng nhập để tiếp tục."

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Trang chủ
@app.route("/")
def index():
    airports = dao.get_all_airports()
    return render_template("index.html", airports=airports)


# Đăng ký
@app.route("/register", methods=['GET', 'POST'])
def register_view():
    err_msg = ''
    if request.method == 'POST':
        password = request.form.get('password')
        confirm = request.form.get('confirm')

        if password == confirm:
            data = request.form.to_dict()
            data.pop('confirm', None)
            avatar = request.files.get('avatar')
            try:
                dao.add_user(avatar=avatar, **data)
                return redirect(url_for('login_process'))
            except Exception as e:
                err_msg = f"Đã có lỗi xảy ra: {e}"
        else:
            err_msg = 'Mật khẩu không khớp!'
    return render_template('register.html', err_msg=err_msg)



@app.route("/login", methods=['GET', 'POST'])
def login_process():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = dao.auth_user(username=username, password=password)

        if user:
            login_user(user)
            next_page = request.args.get('next', '/')
            return redirect(next_page)
        flash("Sai tên đăng nhập hoặc mật khẩu!", "danger")
    return render_template('login.html')



# Đăng xuất
@app.route("/logout")
def logout_process():
    logout_user()
    return redirect(url_for('login_process'))


# Tìm chuyến bay
@app.route('/tim-chuyen', methods=['GET', 'POST'])
def tim_chuyen():
    if request.method == 'POST':
        san_bay_di = request.form.get('san_bay_di')
        san_bay_den = request.form.get('san_bay_den')
        ngay_khoi_hanh = request.form.get('ngay_khoi_hanh')

        if not san_bay_di or not san_bay_den or not ngay_khoi_hanh:
            error_message = "Vui lòng nhập đầy đủ thông tin."
            return render_template('findflight.html', error_message=error_message)

        try:
            flights = dao.search_flights(san_bay_di, san_bay_den, ngay_khoi_hanh)
            if flights:
                return render_template('ketqua.html', flights=flights)
            else:
                error_message = "Không tìm thấy chuyến bay phù hợp."
                return render_template('ketqua.html', error_message=error_message)
        except Exception as e:
            error_message = f"Đã xảy ra lỗi: {str(e)}"
            return render_template('findflight.html', error_message=error_message)

    airports = dao.get_all_airports()
    return render_template('findflight.html', airports=airports)


# Đặt vé
# @app.route('/dat-ve/<int:ma_lich_chuyen_bay>', methods=['GET', 'POST'])
# def dat_ve(ma_lich_chuyen_bay):
#     if request.method == 'GET':
#         lich_chuyen_bay = LichChuyenBay.query.get_or_404(ma_lich_chuyen_bay)
#         booked_seats = [
#             dv.chon_cho for dv in DatVeChuyenBay.query.filter_by(ma_lich_chuyen_bay=ma_lich_chuyen_bay)
#         ]
#         return render_template('datve.html', lich_chuyen_bay=lich_chuyen_bay, booked_seats=booked_seats)
#
#     elif request.method == 'POST':
#         try:
#             ho_ten = request.form['ho_ten']
#             cmnd_ccd = request.form['cmnd_ccd']
#             ngay_sinh = datetime.strptime(request.form['ngay_sinh'], '%Y-%m-%d')
#             so_dien_thoai = request.form['so_dien_thoai']
#             hang_ve = request.form['hang_ve']
#             selected_seats = json.loads(request.form['selected_seats'])
#
#             if not selected_seats:
#                 raise Exception("Vui lòng chọn ít nhất một ghế.")
#
#             data_list = []
#             for seat in selected_seats:
#                 data_list.append({
#                     'ho_ten': ho_ten,
#                     'gioi_tinh': 'Nam',
#                     'ngay_sinh': ngay_sinh,
#                     'cmnd_ccd': cmnd_ccd,
#                     'so_dien_thoai': so_dien_thoai,
#                     'hang_ve': hang_ve,
#                     'chon_cho': int(seat),
#                 })
#
#             dao.save_multiple_bookings(data_list, ma_lich_chuyen_bay)
#
#             flash("Đặt vé thành công!", "success")
#             return redirect(url_for('thanh_toan', ma_dat_ve=data_list[-1]['chon_cho']))
#
#         except Exception as e:
#             flash(f"Lỗi khi đặt vé: {str(e)}", "danger")
#             return redirect(request.url)

@app.route('/dat-ve/<int:ma_lich_chuyen_bay>', methods=['GET', 'POST'])
def dat_ve(ma_lich_chuyen_bay):
    if request.method == 'GET':
        # Lấy thông tin lịch chuyến bay
        lich_chuyen_bay = LichChuyenBay.query.get_or_404(ma_lich_chuyen_bay)
        # Lấy danh sách ghế đã đặt
        booked_seats = [
            dv.chon_cho for dv in DatVeChuyenBay.query.filter_by(ma_lich_chuyen_bay=ma_lich_chuyen_bay)
        ]
        return render_template('datve.html', lich_chuyen_bay=lich_chuyen_bay, booked_seats=booked_seats)

    elif request.method == 'POST':
        try:
            # Lấy dữ liệu từ form
            ho_ten = request.form['ho_ten']
            cmnd_ccd = request.form['cmnd_ccd']
            ngay_sinh = datetime.strptime(request.form['ngay_sinh'], '%Y-%m-%d')
            so_dien_thoai = request.form['so_dien_thoai']
            hang_ve = request.form['hang_ve']
            selected_seats = json.loads(request.form['selected_seats'])

            if not selected_seats:
                raise Exception("Vui lòng chọn ít nhất một ghế.")

            # Gọi DAO để xử lý đặt vé và lấy mã đặt vé của ghế cuối cùng
            last_seat_id = dao.save_booking(
                ma_lich_chuyen_bay=ma_lich_chuyen_bay,
                ho_ten=ho_ten,
                cmnd_ccd=cmnd_ccd,
                ngay_sinh=ngay_sinh,
                so_dien_thoai=so_dien_thoai,
                hang_ve=hang_ve,
                selected_seats=selected_seats
            )

            flash("Đặt vé thành công!", "success")
            # Chuyển hướng đến trang thanh toán
            return redirect(url_for('thanh_toan', ma_dat_ve=last_seat_id))

        except Exception as e:
            flash(f"Lỗi khi đặt vé: {str(e)}", "danger")
            return redirect(request.url)



# Thanh toán
@app.route('/thanh-toan/<int:ma_dat_ve>', methods=['GET', 'POST'])
@login_required
def thanh_toan(ma_dat_ve):
    # Lấy thông tin đặt vé
    dat_ve = DatVeChuyenBay.query.get_or_404(ma_dat_ve)
    ve = VeChuyenBay.query.get_or_404(dat_ve.ma_ve)
    user = current_user

    if request.method == 'POST':
        try:
            # Lấy phương thức thanh toán từ form
            pttt = request.form.get('pttt')

            if not pttt:
                flash("Vui lòng chọn phương thức thanh toán.", "danger")
                return redirect(request.url)

            # Lưu thông tin thanh toán
            dao.luu_thanh_toan(pttt, ve.gia, user.id, ma_dat_ve)

            flash("Thanh toán thành công!", "success")
            return redirect(url_for('index'))

        except Exception as e:
            db.session.rollback()
            flash(f"Lỗi khi thanh toán: {str(e)}", "danger")
            return redirect(request.url)

    return render_template('thanhtoan.html', dat_ve=dat_ve, ve=ve)



# Tải người dùng vào session
@login.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id)


if __name__ == "__main__":
    with app.app_context():
        from app import admin
        app.run(debug=True)
