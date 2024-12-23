from app.models import User, SanBay, ChuyenBay, TuyenBay, DatVeChuyenBay, VeChuyenBay, SanBayTrungGian, LichChuyenBay, ThanhToan, QuyDinh
from app import db, app
import hashlib
import cloudinary.uploader
from flask_login import current_user
from sqlalchemy import func
from datetime import datetime


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
    return session.query(SanBay.ten_san_bay).all()


# Tìm kiếm

# def get_airport_id_by_name(tinh_thanh):
#     airport = SanBay.query.filter(SanBay.tinh_thanh == tinh_thanh).first()
#     return airport.ma_san_bay if airport else None
#
# def search_flights(san_bay_di_name, san_bay_den_name, ngay_khoi_hanh):
#     # Chuyển đổi tên sân bay thành ID
#     san_bay_di_id = get_airport_id_by_name(san_bay_di_name)
#     san_bay_den_id = get_airport_id_by_name(san_bay_den_name)
#
#     # Nếu không tìm thấy ID sân bay, trả về danh sách rỗng
#     if not san_bay_di_id or not san_bay_den_id:
#         return []
#
#     # Tìm kiếm chuyến bay
#     return LichChuyenBay.query.join(ChuyenBay).filter(
#         ChuyenBay.san_bay_di == san_bay_di_id,
#         ChuyenBay.san_bay_den == san_bay_den_id,
#         LichChuyenBay.ngay_gio_khoi_hanh >= datetime.strptime(ngay_khoi_hanh, '%Y-%m-%d')
#     ).all()
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

# Thêm logic cho đặt vé

def save_booking_info(ho_ten, gioi_tinh, ngay_sinh, cmnd_ccd, so_dien_thoai, hang_ve, ma_lich_chuyen_bay, chon_cho):
    # Xác định giá vé dựa trên hạng vé
    gia_ve = 2000000 if hang_ve == 'HANG_1' else 1000000

    # Lấy thông tin chuyến bay
    lich_chuyen_bay = LichChuyenBay.query.get(ma_lich_chuyen_bay)

    # Kiểm tra số ghế còn lại của hạng vé
    if hang_ve == 'HANG_1' and lich_chuyen_bay.so_ghe_hang_1 > 0:
        lich_chuyen_bay.so_ghe_hang_1 -= 1
    elif hang_ve == 'HANG_2' and lich_chuyen_bay.so_ghe_hang_2 > 0:
        lich_chuyen_bay.so_ghe_hang_2 -= 1
    else:
        raise Exception("Số vé còn lại không đủ!")

    # Cập nhật lại thông tin số ghế của chuyến bay
    db.session.commit()

    # Thêm thông tin vé vào hệ thống
    ve = VeChuyenBay(
        ma_chuyen_bay=lich_chuyen_bay.ma_chuyen_bay,
        hang_ve=hang_ve,
        gia=gia_ve
    )
    db.session.add(ve)
    db.session.commit()

    # Thêm thông tin đặt vé
    dat_ve = DatVeChuyenBay(
        ho_ten=ho_ten,
        gioi_tinh=gioi_tinh,
        ngay_sinh=ngay_sinh,
        cmnd_ccd=cmnd_ccd,
        so_dien_thoai=so_dien_thoai,
        ma_ve=ve.ma_ve,
        ma_lich_chuyen_bay=ma_lich_chuyen_bay,
        chon_cho=chon_cho
    )
    db.session.add(dat_ve)
    db.session.commit()

    return dat_ve


# Xử lý thanh toán

def process_payment(ma_dat_ve, pttt):
    dat_ve = DatVeChuyenBay.query.get_or_404(ma_dat_ve)

    # Giả sử bạn đang xử lý thanh toán qua thẻ tín dụng hoặc ví MoMo
    if pttt == 'CREDIT_CARD':
        # Logic thanh toán qua thẻ tín dụng
        pass
    elif pttt == 'MOMO':
        # Logic thanh toán qua MoMo
        pass
    else:
        raise Exception("Phương thức thanh toán không hợp lệ")

    # Cập nhật trạng thái thanh toán thành công
    thanh_toan = ThanhToan(
        pttt=pttt,
        trang_thai='THANH_CONG',  # Thành công
        so_tien=dat_ve.ve_chuyen_bay_rel.gia,
        ma_dat_ve=ma_dat_ve
    )
    db.session.add(thanh_toan)
    db.session.commit()


# if __name__ == "__main__":
    # with app.app_context():
