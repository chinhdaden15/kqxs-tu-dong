import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
import pytz # Thư viện xử lý múi giờ

# CẤU HÌNH
FILE_JSON = 'data.json'
URL = 'https://www.minhngoc.net.vn/xo-so-mien-nam.html'

def lay_ket_qua():
    try:
        # Giả lập trình duyệt để web không chặn
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0'}
        response = requests.get(URL, headers=headers)
        
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, 'html.parser')
        box_kqxs = soup.find('div', class_='box_kqxs')
        if not box_kqxs: return None

        # Lấy ngày hiện tại (Giờ Việt Nam)
        tz_VN = pytz.timezone('Asia/Ho_Chi_Minh') 
        ngay_hom_nay = datetime.now(tz_VN).strftime('%d-%m-%Y')

        # Tạo cấu trúc dữ liệu
        du_lieu_moi = {
            "ngay": ngay_hom_nay,
            "cac_tinh": []
        }

        # Bóc tách dữ liệu từ bảng bên phải (Right Col)
        right_table = box_kqxs.find('table', class_='rightcl')
        if right_table:
            # Lấy tên các tỉnh
            ds_tinh = [t.get_text(strip=True) for t in right_table.find_all('td', class_='tinh')]
            # Lấy giải đặc biệt
            ds_giai_db = [d.get_text(strip=True) for d in right_table.find_all('td', class_='giaiDb')]

            # Ghép lại
            for i in range(len(ds_tinh)):
                if i < len(ds_giai_db):
                    tinh_info = {
                        "tinh": ds_tinh[i],
                        "giai_dac_biet": ds_giai_db[i]
                    }
                    du_lieu_moi["cac_tinh"].append(tinh_info)
        
        return du_lieu_moi

    except Exception as e:
        print(f"Lỗi: {e}")
        return None

def cap_nhat_file(data_moi):
    if not data_moi or not data_moi['cac_tinh']:
        print("Chưa có kết quả hoặc lỗi mạng.")
        return

    du_lieu_cu = []
    # Đọc file cũ nếu có
    if os.path.exists(FILE_JSON):
        try:
            with open(FILE_JSON, 'r', encoding='utf-8') as f:
                du_lieu_cu = json.load(f)
        except:
            du_lieu_cu = []

    # Kiểm tra xem ngày hôm nay đã lưu chưa
    # Lọc bỏ dữ liệu của ngày hôm nay (nếu đã có trước đó) để ghi đè cái mới nhất
    du_lieu_cu = [item for item in du_lieu_cu if item['ngay'] != data_moi['ngay']]
    
    # Chèn dữ liệu mới vào đầu danh sách
    du_lieu_cu.insert(0, data_moi)

    # Lưu lại file
    with open(FILE_JSON, 'w', encoding='utf-8') as f:
        json.dump(du_lieu_cu, f, ensure_ascii=False, indent=4)
    print("Đã cập nhật thành công!")

if __name__ == "__main__":
    kq = lay_ket_qua()
    cap_nhat_file(kq)
