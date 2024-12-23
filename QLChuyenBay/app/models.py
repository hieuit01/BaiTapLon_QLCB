import hashlib
import json
from datetime import datetime
from enum import Enum as BaseEnum
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Enum, Time, Boolean
from sqlalchemy.orm import relationship

from app import db, app


# Các Enums
class HangVe(BaseEnum):
    HANG_1 = "Hạng 1"
    HANG_2 = "Hạng 2"


class GioiTinh(BaseEnum):
    NAM = 'Nam'
    NU = 'Nữ'


class PTTT(BaseEnum):
    TIEN_MAT = "Tiền mặt"
    THE_TIN_DUNG = "Thẻ tín dụng"
    CHUYEN_KHOAN = "Chuyển khoản"


class TrangThaiThanhToan(BaseEnum):
    DA_THANH_TOAN = "Đã thanh toán"
    CHUA_THANH_TOAN = "Chưa thanh toán"


class UserRole(BaseEnum):
    ADMIN = 1
    NHAN_VIEN = 2
    KHACH_HANG = 3


# Các Models
class User(db.Model, UserMixin):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    username = Column(String(100), nullable=False, unique=True)
    password = Column(String(100), nullable=False)
    avatar = Column(String(255), default="https://res.cloudinary.com/dxxwcby8l/image/upload/v1690528735/cg6clgelp8zjwlehqsst.jpg")
    active = Column(Boolean, default=True)
    user_role = Column(Enum(UserRole), default=UserRole.KHACH_HANG)


    def __str__(self):
        return self.username

    def get_role(self):
        return self.user_role

class SanBay(db.Model):
    __tablename__ = 'san_bay'
    ma_san_bay = Column(Integer, primary_key=True, autoincrement=True)
    ten_san_bay = Column(String(255), nullable=False)
    tinh_thanh = Column(String(255), nullable=False)
    quoc_gia = Column(String(255), nullable=False)

    def __str__(self):
        return self.ten_san_bay


# class ChuyenBay(db.Model):
#     __tablename__ = 'chuyen_bay'
#     ma_chuyen_bay = Column(Integer, primary_key=True, autoincrement=True)
#     san_bay_di = Column(Integer, ForeignKey('san_bay.ma_san_bay'), nullable=False)
#     san_bay_den = Column(Integer, ForeignKey('san_bay.ma_san_bay'), nullable=False)
#     san_bay_di_rel = relationship("SanBay", foreign_keys=[san_bay_di])
#     san_bay_den_rel = relationship("SanBay", foreign_keys=[san_bay_den])


class TuyenBay(db.Model):
    __tablename__ = 'tuyen_bay'
    ma_tuyen_bay = Column(Integer, primary_key=True, autoincrement=True)
    san_bay_di = Column(Integer, ForeignKey('san_bay.ma_san_bay'), nullable=False)
    san_bay_den = Column(Integer, ForeignKey('san_bay.ma_san_bay'), nullable=False)
    san_bay_di_rel = relationship("SanBay", foreign_keys=[san_bay_di], backref='tuyen_bay_di', lazy=True)
    san_bay_den_rel = relationship("SanBay", foreign_keys=[san_bay_den], backref='tuyen_bay_den', lazy=True)

    # Quan hệ một tuyến bay có nhiều chuyến bay
    chuyen_bay_rel = relationship("ChuyenBay", backref='tuyen_bay', lazy=True)

    def __str__(self):
        return f"Tuyến bay từ {self.san_bay_di_rel.ten_san_bay} đến {self.san_bay_den_rel.ten_san_bay}"


class ChuyenBay(db.Model):
    __tablename__ = 'chuyen_bay'
    ma_chuyen_bay = Column(Integer, primary_key=True, autoincrement=True)
    ma_tuyen_bay = Column(Integer, ForeignKey('tuyen_bay.ma_tuyen_bay'), nullable=False)

    def __str__(self):
        return f"Chuyến bay số {self.ma_chuyen_bay}"


class LichChuyenBay(db.Model):
    __tablename__ = 'lich_chuyen_bay'
    ma_lich_chuyen_bay = Column(Integer, primary_key=True, autoincrement=True)
    ngay_gio_khoi_hanh = Column(DateTime, nullable=False)
    thoi_gian_bay_gio_phut = Column(Time, nullable=False)
    ma_chuyen_bay = Column(Integer, ForeignKey('chuyen_bay.ma_chuyen_bay'), nullable=False)
    so_ghe_hang_1 = Column(Integer, nullable=False)
    so_ghe_hang_2 = Column(Integer, nullable=False)
    chuyen_bay_rel = relationship("ChuyenBay", backref='lich_chuyen_bay', lazy=True)



class SanBayTrungGian(db.Model):
    __tablename__ = 'san_bay_trung_gian'
    stt = Column(Integer, primary_key=True, autoincrement=True)
    san_bay_trung_gian = Column(Integer, ForeignKey('san_bay.ma_san_bay'), nullable=False)
    ma_lich_chuyen_bay = Column(Integer, ForeignKey('lich_chuyen_bay.ma_lich_chuyen_bay'), nullable=False)
    thoi_gian_bay_gio_phut = Column(Time, nullable=False)
    ghi_chu = Column(Text, nullable=True)
    san_bay_rel = relationship("SanBay", backref='san_bay_trung_gian', lazy=True)
    lich_chuyen_bay_rel = relationship("LichChuyenBay", backref='san_bay_trung_gian', lazy=True)


class VeChuyenBay(db.Model):
    __tablename__ = 've_chuyen_bay'
    ma_ve = Column(Integer, primary_key=True, autoincrement=True)
    ma_chuyen_bay = Column(Integer, ForeignKey('chuyen_bay.ma_chuyen_bay'), nullable=False)
    hang_ve = Column(Enum(HangVe), nullable=False)
    gia = Column(Float, nullable=False)
    chuyen_bay_rel = relationship("ChuyenBay", backref='ve_chuyen_bay', lazy=True)



class DatVeChuyenBay(db.Model):
    __tablename__ = 'dat_ve_chuyen_bay'
    ma_dat_ve = Column(Integer, primary_key=True, autoincrement=True)
    ho_ten = Column(String(255), nullable=False)
    gioi_tinh = Column(Enum(GioiTinh), nullable=False)
    ngay_sinh = Column(DateTime, nullable=False)
    cmnd_ccd = Column(String(20), nullable=False)
    so_dien_thoai = Column(String(15), nullable=False)
    ma_ve = Column(Integer, ForeignKey('ve_chuyen_bay.ma_ve'), nullable=False)
    ma_lich_chuyen_bay = Column(Integer, ForeignKey('lich_chuyen_bay.ma_lich_chuyen_bay'), nullable=False)
    chon_cho = Column(Integer, nullable=False)  # Thêm cột này để lưu số ghế
    thoi_diem_dat_ve = Column(DateTime, default=datetime.now, nullable=False)
    ve_chuyen_bay_rel = relationship("VeChuyenBay", backref='dat_ve_chuyen_bay', lazy=True)
    lich_chuyen_bay_rel = relationship("LichChuyenBay", backref='dat_ve_chuyen_bay', lazy=True)



class ThanhToan(db.Model):
    __tablename__ = 'thanh_toan'
    ma_thanh_toan = Column(Integer, primary_key=True, autoincrement=True)
    ngay_thanh_toan = Column(DateTime, default=datetime.now, nullable=False)
    pttt = Column(Enum(PTTT), nullable=False)
    trang_thai = Column(Enum(TrangThaiThanhToan), nullable=False)
    so_tien = Column(Float, nullable=False)
    ma_dat_ve = Column(Integer, ForeignKey('dat_ve_chuyen_bay.ma_dat_ve'), nullable=False)
    dat_ve_rel = relationship("DatVeChuyenBay", backref='thanh_toan', lazy=True)



class QuyDinh(db.Model):
    __tablename__ = 'quy_dinh'
    ma_quy_dinh = Column(Integer, primary_key=True, autoincrement=True)
    so_luong_san_bay = Column(Integer, nullable=False)
    thoi_gian_bay_toi_thieu = Column(Time, nullable=False)
    so_san_bay_trung_gian_toi_da = Column(Integer, nullable=False)
    thoi_gian_dung_toi_thieu = Column(Time, nullable=False)
    thoi_gian_dung_toi_da = Column(Integer, nullable=False)
    so_gio_dat_ve_truoc = Column(Time, nullable=False)
    so_gio_ban_ve_truoc = Column(Time, nullable=False)



#Open file json
def read_json_file(json_file):
    with open(json_file, encoding='utf-8') as file:
        return json.load(file)

def load_user_to_db(json_file):
    data = read_json_file(json_file)
    for item in data:
        user = User(name=item['name'],
                    username=item['username'],
                    password=str(hashlib.md5(item['password'].encode('utf-8')).hexdigest()),
                    avatar=item['avatar'],
                    user_role=item['user_role'])
        db.session.add(user)
    db.session.commit()

def load_san_bay_to_db(json_file):
    data = read_json_file(json_file)
    for item in data:
        san_bay = SanBay(
            ten_san_bay=item['ten_san_bay'],
            tinh_thanh=item['tinh_thanh'],
            quoc_gia=item['quoc_gia']
        )
        db.session.add(san_bay)
    db.session.commit()

# Load dữ liệu vào bảng ChuyenBay
# def load_chuyen_bay_to_db(json_file):
#     data = read_json_file(json_file)
#     for item in data:
#         chuyen_bay = ChuyenBay(
#             san_bay_di=item['san_bay_di'],
#             san_bay_den=item['san_bay_den']
#         )
#         db.session.add(chuyen_bay)
#     db.session.commit()

# Load dữ liệu vào bảng ChuyenBay
def load_chuyen_bay_to_db(json_file):
    data = read_json_file(json_file)
    for item in data:
        chuyen_bay = ChuyenBay(
            ma_tuyen_bay=item['ma_tuyen_bay']
        )
        db.session.add(chuyen_bay)
    db.session.commit()

def load_tuyen_bay_to_db(json_file):
    data = read_json_file(json_file)
    for item in data:
        tuyen_bay = TuyenBay(
            san_bay_di=item['san_bay_di'],
            san_bay_den=item['san_bay_den']
        )
        db.session.add(tuyen_bay)
    db.session.commit()


# Load dữ liệu vào bảng LichChuyenBay
def load_lich_chuyen_bay_to_db(json_file):
    data = read_json_file(json_file)
    for item in data:
        lich_chuyen_bay = LichChuyenBay(
            ngay_gio_khoi_hanh=datetime.strptime(item['ngay_gio_khoi_hanh'], "%Y-%m-%d"),
            thoi_gian_bay_gio_phut=datetime.strptime(item['thoi_gian_bay_gio_phut'], "%H:%M:%S").time(),
            ma_chuyen_bay=item['ma_chuyen_bay'],
            so_ghe_hang_1=item['so_ghe_hang_1'],
            so_ghe_hang_2=item['so_ghe_hang_2']
        )
        db.session.add(lich_chuyen_bay)
    db.session.commit()

# Load dữ liệu vào bảng SanBayTrungGian
def load_san_bay_trung_gian_to_db(json_file):
    data = read_json_file(json_file)
    for item in data:
        san_bay_trung_gian = SanBayTrungGian(
            san_bay_trung_gian=item['san_bay_trung_gian'],
            ma_lich_chuyen_bay=item['ma_lich_chuyen_bay'],
            thoi_gian_bay_gio_phut=datetime.strptime(item['thoi_gian_bay_gio_phut'], "%H:%M:%S").time(),
            ghi_chu=item.get('ghi_chu', None)
        )
        db.session.add(san_bay_trung_gian)
    db.session.commit()

# Load dữ liệu vào bảng VeChuyenBay
def load_ve_chuyen_bay_to_db(json_file):
    data = read_json_file(json_file)
    for item in data:
        ve_chuyen_bay = VeChuyenBay(
            ma_chuyen_bay=item['ma_chuyen_bay'],
            hang_ve=item['hang_ve'],
            gia=item['gia']
        )
        db.session.add(ve_chuyen_bay)
    db.session.commit()

# Load dữ liệu vào bảng DatVeChuyenBay
def load_dat_ve_chuyen_bay_to_db(json_file):
    data = read_json_file(json_file)
    for item in data:
        dat_ve_chuyen_bay = DatVeChuyenBay(
            ho_ten=item['ho_ten'],
            gioi_tinh=item['gioi_tinh'],
            ngay_sinh=datetime.strptime(item['ngay_sinh'], "%Y-%m-%d"),
            cmnd_ccd=item['cmnd_ccd'],
            so_dien_thoai=item['so_dien_thoai'],
            ma_ve=item['ma_ve'],
            ma_lich_chuyen_bay=item['ma_lich_chuyen_bay'],
            thoi_diem_dat_ve=datetime.strptime(item['thoi_diem_dat_ve'], "%Y-%m-%d")
        )
        db.session.add(dat_ve_chuyen_bay)
    db.session.commit()

# Load dữ liệu vào bảng ThanhToan
def load_thanh_toan_to_db(json_file):
    data = read_json_file(json_file)
    for item in data:
        thanh_toan = ThanhToan(
            ngay_thanh_toan=datetime.strptime(item['ngay_thanh_toan'], "%Y-%m-%d"),
            pttt=item['pttt'],
            trang_thai=item['trang_thai'],
            so_tien=item['so_tien'],
            ma_dat_ve=item['ma_dat_ve']
        )
        db.session.add(thanh_toan)
    db.session.commit()

# Load dữ liệu vào bảng QuyDinh
def load_quy_dinh_to_db(json_file):
    data = read_json_file(json_file)
    for item in data:
        quy_dinh = QuyDinh(
            so_luong_san_bay=item['so_luong_san_bay'],
            thoi_gian_bay_toi_thieu=datetime.strptime(item['thoi_gian_bay_toi_thieu'], "%H:%M:%S").time(),
            so_san_bay_trung_gian_toi_da=item['so_san_bay_trung_gian_toi_da'],
            thoi_gian_dung_toi_thieu=datetime.strptime(item['thoi_gian_dung_toi_thieu'], "%H:%M:%S").time(),
            thoi_gian_dung_toi_da=item['thoi_gian_dung_toi_da'],
            so_gio_dat_ve_truoc=datetime.strptime(item['so_gio_dat_ve_truoc'], "%H:%M:%S").time(),
            so_gio_ban_ve_truoc=datetime.strptime(item['so_gio_ban_ve_truoc'], "%H:%M:%S").time()
        )
        db.session.add(quy_dinh)
    db.session.commit()


if __name__ == '__main__':
    with app.app_context():
        load_san_bay_to_db('data/Sanbay.json')
        load_tuyen_bay_to_db('data/tuyenbay.json')
        load_chuyen_bay_to_db('data/chuyenbay.json')
        load_lich_chuyen_bay_to_db('data/lichchuyenbay.json')
        db.create_all()

        # load_user_to_db('data/user.json')