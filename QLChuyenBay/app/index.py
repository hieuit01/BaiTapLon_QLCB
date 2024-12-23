import dao
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from app import app, login, db
from flask_login import login_user, logout_user, login_required, current_user
from app.models import UserRole, LichChuyenBay, HangVe, ThanhToan, DatVeChuyenBay, TrangThaiThanhToan
from datetime import datetime
from dao import search_flights

# Trang chủ
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/findflight")
def find_flight():
    try:
        # Lấy danh sách tỉnh thành
        airports = dao.get_chuyenbay_airports()
        if not airports:
            flash("Không tìm thấy sân bay nào.", "warning")
        return render_template('findflight.html', airports=airports)
    except Exception as e:
        flash(f"Lỗi khi lấy danh sách sân bay: {str(e)}", "danger")
        return render_template('findflight.html', airports=[])

@app.route("/register", methods=['get', 'post'])
def register_view():
    err_msg = ''
    if request.method.__eq__('POST'):
        password = request.form.get('password')
        confirm = request.form.get('confirm')

        if password.__eq__(confirm):
            data = request.form.copy()
            del data['confirm']

            avatar = request.files.get('avatar')
            dao.add_user(avatar=avatar, **data)

            return redirect('/login')
        else:
            err_msg = 'Mật khẩu không khớp!'

    return render_template('register.html', err_msg=err_msg)

@app.route("/login", methods=['get', 'post'])
def login_process():
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')

        u = dao.auth_user(username=username, password=password)
        if u:
            login_user(u)

            next = request.args.get('next')
            return redirect('/' if next is None else next)

    return render_template('login.html')

@app.route("/login-admin", methods=['post'])
def login_admin_process():
    username = request.form.get('username')
    password = request.form.get('password')

    u = dao.auth_user(username=username, password=password, role=UserRole.ADMIN)
    if u:
        login_user(u)

    return redirect('/admin')

# # Trang tìm kiếm chuyến bay
# @app.route('/tim-chuyen', methods=['GET', 'POST'])
# def tim_chuyen():
#     if request.method == 'POST':
#         san_bay_di = request.form.get('san_bay_di')
#         san_bay_den = request.form.get('san_bay_den')
#         ngay_khoi_hanh = request.form.get('ngay_khoi_hanh')
#
#         flights = dao.search_flights(san_bay_di, san_bay_den, ngay_khoi_hanh)
#
#         if flights:
#             return render_template('ketqua.html', flights=flights)
#         else:
#             error_message = "Không tìm thấy chuyến bay phù hợp."
#             return render_template('ketqua.html', error_message=error_message)
#
#     return render_template('findflight.html')

@app.route('/tim-chuyen', methods=['GET', 'POST'])
def tim_chuyen():
    if request.method == 'POST':
        san_bay_di = request.form.get('san_bay_di')
        san_bay_den = request.form.get('san_bay_den')
        ngay_khoi_hanh = request.form.get('ngay_khoi_hanh')

        # Validate input
        if not san_bay_di or not san_bay_den or not ngay_khoi_hanh:
            error_message = "Vui lòng nhập đầy đủ thông tin."
            return render_template('findflight.html', error_message=error_message)

        try:
            flights = search_flights(san_bay_di, san_bay_den, ngay_khoi_hanh)

            if flights:
                return render_template('ketqua.html', flights=flights)
            else:
                error_message = "Không tìm thấy chuyến bay phù hợp."
                return render_template('ketqua.html', error_message=error_message)

        except Exception as e:
            error_message = f"Đã xảy ra lỗi: {str(e)}"
            return render_template('findflight.html', error_message=error_message)

    return render_template('findflight.html')

@app.route('/datve/<int:ma_lich_chuyen_bay>', methods=['GET', 'POST'])
def dat_ve(ma_lich_chuyen_bay):
    lich_chuyen_bay = LichChuyenBay.query.get_or_404(ma_lich_chuyen_bay)

    # Kiểm tra số vé còn lại của các hạng vé
    hang_1_left = lich_chuyen_bay.so_ghe_hang_1 > 0
    hang_2_left = lich_chuyen_bay.so_ghe_hang_2 > 0

    if not hang_1_left and not hang_2_left:
        # Nếu không còn vé cho cả 2 hạng
        error_message = "Không còn vé cho chuyến bay này."
        return render_template('ketqua.html', error_message=error_message)

    # Đã có vé, tiếp tục xử lý như bình thường
    booked_seats = [dv.chon_cho for dv in DatVeChuyenBay.query.filter_by(ma_lich_chuyen_bay=ma_lich_chuyen_bay).all()]

    if request.method == 'POST':
        ho_ten = request.form.get('ho_ten')
        gioi_tinh = request.form.get('gioi_tinh')
        ngay_sinh = request.form.get('ngay_sinh')
        cmnd_ccd = request.form.get('cmnd_ccd')
        so_dien_thoai = request.form.get('so_dien_thoai')
        hang_ve = request.form.get('hang_ve')
        chon_cho = request.form.get('chon_cho')

        if not ho_ten or not gioi_tinh or not ngay_sinh or not cmnd_ccd or not so_dien_thoai or not chon_cho:
            flash('Vui lòng điền đầy đủ thông tin và chọn chỗ ngồi.', 'danger')
            return redirect(request.url)

        if int(chon_cho) in booked_seats:
            flash('Chỗ ngồi đã được đặt. Vui lòng chọn chỗ khác.', 'danger')
            return redirect(request.url)

        dat_ve = dao.save_booking_info(
            ho_ten, gioi_tinh, ngay_sinh, cmnd_ccd, so_dien_thoai, hang_ve, ma_lich_chuyen_bay, chon_cho
        )

        return redirect(url_for('thanh_toan', ma_dat_ve=dat_ve.ma_dat_ve))

    return render_template('datve.html', lich_chuyen_bay=lich_chuyen_bay, booked_seats=booked_seats)


@app.route('/thanh-toan/<int:ma_dat_ve>', methods=['GET', 'POST'])
def thanh_toan(ma_dat_ve):
    dat_ve = DatVeChuyenBay.query.get_or_404(ma_dat_ve)

    # Kiểm tra đăng nhập chỉ khi nhấn nút thanh toán (khi POST)
    if request.method == 'POST':
        # Kiểm tra đăng nhập trước khi thực hiện thanh toán
        if not current_user.is_authenticated:
            flash('Bạn cần đăng nhập để thực hiện thanh toán.', 'danger')
            return redirect(url_for('login', next=request.url))

        # Lấy thông tin phương thức thanh toán từ form
        pttt = request.form.get('pttt')

        if not pttt:
            flash('Vui lòng chọn phương thức thanh toán.', 'danger')
            return redirect(request.url)

        try:
            # Giả sử bạn có một hàm trong dao để xử lý thanh toán
            dao.process_payment(ma_dat_ve, pttt)
            flash('Thanh toán thành công!', 'success')
        except Exception as e:
            # Nếu thanh toán thất bại, rollback giao dịch
            db.session.rollback()
            flash('Thanh toán thất bại. Vui lòng thử lại.', 'danger')
            return redirect(request.url)

        # Sau khi thanh toán thành công, chuyển đến trang chủ (hoặc trang khác nếu cần)
        return redirect(url_for('index'))

    # Render trang thanh toán với thông tin vé (khi GET)
    return render_template('thanhtoan.html', dat_ve=dat_ve)


@app.route("/logout")
def logout_process():
    logout_user()
    return redirect('/login')

@login.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id)

if __name__ == "__main__":
    with app.app_context():
        from app import admin
        app.run(debug=True)
