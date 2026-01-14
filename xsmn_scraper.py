import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
import pytz

# CẤU HÌNH
FILE_JSON = 'data.json'
URL = 'https://www.minhngoc.net.vn/xo-so-mien-nam.html'

def lay_ket_qua():
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0'}
        response = requests.get(URL, headers=headers)
        
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, 'html.parser')
        box_kqxs = soup.find('div', class_='box_kqxs')
        if not box_kqxs: return None

        # 1. XỬ LÝ NGÀY: App yêu cầu định dạng YYYY-MM-DD (Ví dụ: 2026-01-14)
        tz_VN = pytz.timezone('Asia/Ho_Chi_Minh') 
        ngay_app_can = datetime.now(tz_VN).strftime('%Y-%m-%d') 

        # 2. XỬ LÝ KẾT QUẢ: App yêu cầu trường "result"
        # Vì App này có vẻ thiết kế cho XSMB (1 tỉnh), nhưng XSMN có 3-4 tỉnh.
        # Giải pháp: Ta sẽ gộp tất cả giải đặc biệt của các tỉnh vào một dict để App không bị lỗi.
        
        ket_qua_dict = {}
        
        right_table = box_kqxs.find('table', class_='rightcl')
        if right_table:
            # Lấy tên tỉnh và giải đặc biệt
            ds_tinh = [t.get_text(strip=True) for t in right_table.find_all('td', class_='tinh')]
            ds_giai_db = [d.get_text(strip=True) for d in right_table.find_all('td', class_='giaiDb')]

            for i in range(len(ds_tinh)):
                if i < len(ds_giai_db):
                    # Lưu tên tỉnh làm key, giải đặc biệt làm value
                    # Ví dụ: "Ben Tre": "123456"
                    tinh_khong_dau = ds_tinh[i].replace(" ", "_") # App thường thích không dấu
                    ket_qua_dict[tinh_khong_dau] = ds_giai_db[i]
                    
                    # Hack: Để App hiển thị ít nhất 1 số, ta tạo key "special" lấy giải của tỉnh đầu tiên
                    if i == 0:
                        ket_qua_dict["special"] = ds_giai_db[i]

        # 3. CẤU TRÚC JSON CHUẨN CHO APP CỦA BẠN
        du_lieu_chuan = {
            "date": ngay_app_can,   # Sửa từ "ngay" thành "date"
            "result": ket_qua_dict  # Sửa từ "cac_tinh" thành "result"
        }
        
        return du_lieu_chuan

    except Exception as e:
        print(f"Lỗi: {e}")
        return None

def cap_nhat_file(data_moi):
    if not data_moi or not data_moi['result']:
        print("Chưa có kết quả.")
        return

    du_lieu_cu = []
    if os.path.exists(FILE_JSON):
        try:
            with open(FILE_JSON, 'r', encoding='utf-8') as f:
                du_lieu_cu = json.load(f)
        except:
            du_lieu_cu = []

    # Kiểm tra trùng ngày (theo key "date")
    du_lieu_cu = [item for item in du_lieu_cu if item.get('date') != data_moi['date']]
    
    # Chèn dữ liệu mới lên đầu
    du_lieu_cu.insert(0, data_moi)

    # Ghi file
    with open(FILE_JSON, 'w', encoding='utf-8') as f:
        json.dump(du_lieu_cu, f, ensure_ascii=False, indent=4)
    print("Đã cập nhật format chuẩn cho App!")

if __name__ == "__main__":
    kq = lay_ket_qua()
    cap_nhat_file(kq)
