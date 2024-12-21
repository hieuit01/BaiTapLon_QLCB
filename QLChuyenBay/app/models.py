from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Enum, Time
from sqlalchemy.orm import relationship
from app import db, app
from enum import Enum as BaseEnum
from datetime import datetime
from flask_login import UserMixin


# Các Enums
class HangVe(BaseEnum):
    HANG_1 = "Hạng 1"
    HANG_2 = "Hạng 2"


class PTTT(BaseEnum):
    TIEN_MAT = "Tiền mặt"
    THE_TIN_DUNG = "Thẻ tín dụng"
    CHUYEN_KHOAN = "Chuyển khoản"


class TrangThaiThanhToan(BaseEnum):
    DA_THANH_TOAN = "Đã thanh toán"
    CHUA_THANH_TOAN = "Chưa thanh toán"


class UserRole(BaseEnum):
    ADMIN = "Admin"
    NHAN_VIEN = "Nhân viên"
    KHACH_HANG = "Khách hàng"


# Các Models
class User(db.Model, UserMixin):
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), nullable=False, unique=True)
    password = Column(String(100), nullable=False)
    avatar = Column(String(255), nullable=True)
    user_role = Column(Enum(BaseEnum))

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


class ChuyenBay(db.Model):
    __tablename__ = 'chuyen_bay'
    ma_chuyen_bay = Column(Integer, primary_key=True, autoincrement=True)
    san_bay_di = Column(Integer, ForeignKey('san_bay.ma_san_bay'), nullable=False)
    san_bay_den = Column(Integer, ForeignKey('san_bay.ma_san_bay'), nullable=False)
    san_bay_di_rel = relationship("SanBay", foreign_keys=[san_bay_di])
    san_bay_den_rel = relationship("SanBay", foreign_keys=[san_bay_den])


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
    cmnd_ccd = Column(String(20), nullable=False)
    so_dien_thoai = Column(String(15), nullable=False)
    ma_ve = Column(Integer, ForeignKey('ve_chuyen_bay.ma_ve'), nullable=False)
    ma_lich_chuyen_bay = Column(Integer, ForeignKey('lich_chuyen_bay.ma_lich_chuyen_bay'), nullable=False)
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


if __name__ == '__main__':
    with app.app_context():
        db.create_all()