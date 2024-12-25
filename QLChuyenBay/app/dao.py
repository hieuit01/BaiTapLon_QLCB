from app.models import (User, SanBay, ChuyenBay, HangVe, TuyenBay, DatVeChuyenBay, VeChuyenBay, SanBayTrungGian, LichChuyenBay,
                        ThanhToan, QuyDinh, TrangThaiThanhToan, PTTT)
from app import db, app
import hashlib
import cloudinary.uploader
from flask_login import current_user
from sqlalchemy import func, case
from datetime import datetime
from sqlalchemy.orm import aliased


def add_user(name, username, password, avatar):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

    u = User(name=name, username=username, password=password,
             avatar='https://res.cloudinary.com/dxxwcby8l/image/upload/v1690528735/cg6clgelp8zjwlehqsst.jpg')

    if avatar:
        res = cloudinary.uploader.upload(avatar)
        u.avatar = res.get('secure_url')

    db.session.add(u)
    db.session.commit()

def auth_user(username, password, role=None):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

    u = User.query.filter(User.username.__eq__(username.strip()),
                          User.password.__eq__(password))
    if role:
        u = u.filter(User.user_role.__eq__(role))

    return u.first()

def get_user_by_id(id):
    return User.query.get(id)

def get_all_airports():
    return SanBay.query.all()

def get_airport_id_by_name(tinh_thanh):
    airport = SanBay.query.filter(SanBay.tinh_thanh == tinh_thanh).first()
    return airport.ma_san_bay if airport else None

def search_flights(san_bay_di_name, san_bay_den_name, ngay_khoi_hanh):
    # Chuyển đổi tên sân bay thành ID
    san_bay_di_id = get_airport_id_by_name(san_bay_di_name)
    san_bay_den_id = get_airport_id_by_name(san_bay_den_name)

    # Nếu không tìm thấy ID sân bay, trả về danh sách rỗng
    if not san_bay_di_id or not san_bay_den_id:
        return []

    # Tìm kiếm các lịch chuyến bay thông qua tuyến bay
    flights = (
        LichChuyenBay.query
        .join(ChuyenBay, LichChuyenBay.ma_chuyen_bay == ChuyenBay.ma_chuyen_bay)
        .join(TuyenBay, ChuyenBay.ma_tuyen_bay == TuyenBay.ma_tuyen_bay)
        .filter(
            TuyenBay.san_bay_di == san_bay_di_id,
            TuyenBay.san_bay_den == san_bay_den_id,
            LichChuyenBay.ngay_gio_khoi_hanh >= datetime.strptime(ngay_khoi_hanh, '%Y-%m-%d')
        )
        .all()
    )
    return flights


def save_booking(ma_lich_chuyen_bay, ho_ten, cmnd_ccd, ngay_sinh, so_dien_thoai, hang_ve, selected_seats):

    try:
        lich_chuyen_bay = LichChuyenBay.query.with_for_update().get(ma_lich_chuyen_bay)
        if not lich_chuyen_bay:
            raise Exception("Không tìm thấy lịch chuyến bay.")

        last_seat_id = None  # Để lưu mã đặt vé cuối cùng
        for seat in selected_seats:
            # Kiểm tra ghế đã đặt chưa
            existing_booking = DatVeChuyenBay.query.filter_by(
                ma_lich_chuyen_bay=ma_lich_chuyen_bay, chon_cho=seat
            ).first()
            if existing_booking:
                raise Exception(f"Ghế {seat} đã được đặt. Vui lòng chọn ghế khác.")

            # Giảm số lượng ghế trống
            if hang_ve == "HANG_1":
                if lich_chuyen_bay.so_ghe_hang_1 <= 0:
                    raise Exception("Hết ghế hạng 1.")
                lich_chuyen_bay.so_ghe_hang_1 -= 1
            elif hang_ve == "HANG_2":
                if lich_chuyen_bay.so_ghe_hang_2 <= 0:
                    raise Exception("Hết ghế hạng 2.")
                lich_chuyen_bay.so_ghe_hang_2 -= 1

            # Thêm vé chuyến bay
            ve = VeChuyenBay(
                ma_chuyen_bay=lich_chuyen_bay.ma_chuyen_bay,
                hang_ve=hang_ve,
                gia=2000000 if hang_ve == "HANG_1" else 1000000
            )
            db.session.add(ve)
            db.session.flush()  # Đẩy vé vào session để lấy ID

            # Thêm thông tin đặt vé
            dat_ve = DatVeChuyenBay(
                ho_ten=ho_ten,
                gioi_tinh='Nam',
                ngay_sinh=ngay_sinh,
                cmnd_ccd=cmnd_ccd,
                so_dien_thoai=so_dien_thoai,
                ma_lich_chuyen_bay=ma_lich_chuyen_bay,
                chon_cho=seat,
                ma_ve=ve.ma_ve
            )
            db.session.add(dat_ve)
            db.session.flush()  # Đẩy đặt vé vào session để lấy ID

            # Lưu mã đặt vé cuối cùng
            last_seat_id = dat_ve.ma_dat_ve

        db.session.commit()
        return last_seat_id

    except Exception as e:
        db.session.rollback()
        raise Exception(f"Lỗi khi đặt vé: {str(e)}")


def luu_thanh_toan(pttt, so_tien, ma_user, ma_dat_ve):
    try:
        # Lưu thông tin thanh toán vào cơ sở dữ liệu
        thanh_toan = ThanhToan(
            pttt=PTTT[pttt],
            trang_thai=TrangThaiThanhToan.DA_THANH_TOAN,
            so_tien=so_tien,
            ma_user=ma_user,
            ma_dat_ve=ma_dat_ve
        )
        db.session.add(thanh_toan)
        db.session.commit()
        return True, thanh_toan  # Trả về kết quả thành công và đối tượng thanh toán
    except Exception as e:
        db.session.rollback()
        return False, str(e)  # Trả về kết quả thất bại và thông báo lỗi



def revenue_stats_by_period(p='month', year=datetime.now().year, month=None):
    SanBayDi = aliased(SanBay)  # Alias cho sân bay đi
    SanBayDen = aliased(SanBay)  # Alias cho sân bay đến

    # Đảm bảo p là 'month' (vì bạn chỉ lọc theo tháng)
    if p != 'month':
        raise ValueError("Giá trị 'p' phải là 'month'")

    # Câu truy vấn
    query = db.session.query(
        func.extract(p, ThanhToan.ngay_thanh_toan).label("thoi_gian"),
        ChuyenBay.ma_chuyen_bay.label("ma_chuyen_bay"),
        SanBayDi.ten_san_bay.label("san_bay_di"),
        SanBayDi.tinh_thanh.label("tinh_thanh_di"),
        SanBayDi.quoc_gia.label("quoc_gia_di"),
        SanBayDen.ten_san_bay.label("san_bay_den"),
        SanBayDen.tinh_thanh.label("tinh_thanh_den"),
        SanBayDen.quoc_gia.label("quoc_gia_den"),
        func.sum(ThanhToan.so_tien).label("tong_doanh_thu"),
        func.count(DatVeChuyenBay.ma_dat_ve).label("tong_so_ve"),
        func.count(
            case(
                (VeChuyenBay.hang_ve == HangVe.HANG_1, 1)
            )
        ).label("so_ve_hang_1"),
        func.count(
            case(
                (VeChuyenBay.hang_ve == HangVe.HANG_2, 1)
            )
        ).label("so_ve_hang_2")
    ).join(
        DatVeChuyenBay, DatVeChuyenBay.ma_dat_ve == ThanhToan.ma_dat_ve
    ).join(
        VeChuyenBay, VeChuyenBay.ma_ve == DatVeChuyenBay.ma_ve
    ).join(
        LichChuyenBay, LichChuyenBay.ma_lich_chuyen_bay == DatVeChuyenBay.ma_lich_chuyen_bay
    ).join(
        ChuyenBay, ChuyenBay.ma_chuyen_bay == LichChuyenBay.ma_chuyen_bay
    ).join(
        TuyenBay, TuyenBay.ma_tuyen_bay == ChuyenBay.ma_tuyen_bay
    ).join(
        SanBayDi, SanBayDi.ma_san_bay == TuyenBay.san_bay_di
    ).join(
        SanBayDen, SanBayDen.ma_san_bay == TuyenBay.san_bay_den
    ).filter(
        ThanhToan.trang_thai == TrangThaiThanhToan.DA_THANH_TOAN
    )

    # Lọc theo tháng và năm
    if month:
        query = query.filter(func.extract('month', ThanhToan.ngay_thanh_toan) == month)
    if year:
        query = query.filter(func.extract('year', ThanhToan.ngay_thanh_toan) == year)

    # Nhóm và sắp xếp theo tháng
    query = query.group_by(
        func.extract(p, ThanhToan.ngay_thanh_toan),  # Nhóm theo tháng
        ChuyenBay.ma_chuyen_bay,
        SanBayDi.ten_san_bay, SanBayDi.tinh_thanh, SanBayDi.quoc_gia,
        SanBayDen.ten_san_bay, SanBayDen.tinh_thanh, SanBayDen.quoc_gia
    ).order_by(
        func.extract(p, ThanhToan.ngay_thanh_toan)  # Sắp xếp theo tháng
    )

    return query.all()





if __name__ == "__main__":
    with app.app_context():
        print(revenue_stats_by_period())
