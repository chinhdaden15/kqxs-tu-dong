import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime, timedelta
import pytz
import re

# CẤU HÌNH
FILE_JSON = 'data.json'
DAYS_TO_BACKFILL = 35 # Lấy dư ra 35 ngày cho chắc
BASE_URL = 'https://www.minhngoc.net.vn/xo-so-mien-nam/{}.html'

def get_data_for_date(date_obj):
    date_str_url = date_obj.strftime('%d-%m-%Y') # Định dạng cho URL Minh Ngọc
    date_str_app = date_obj.strftime('%Y-%m-%d') # Định dạng cho App
    url = BASE_URL.format(date_str_url)
    
    print(f"Đang lấy dữ liệu ngày: {date_str_url}...")
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, 'html.parser')
        box_kqxs = soup.find('div', class_='box_kqxs')
        if not box_kqxs: return None

        ket_qua_dict = {}
        all_numbers = []
        special_prizes = []
        
        right_table = box_kqxs.find('table', class_='rightcl')
        if right_table:
            rows = right_table.find_all('tr')
            for row in rows:
                cells = row.find_all('td')
                for cell in cells:
                    if 'tinh' in cell.get('class', []): continue
                    
                    text_val = cell.get_text(strip=True)
                    if not text_val: continue
                    
                    numbers_in_cell = re.findall(r'\d+', text_val)
                    for num in numbers_in_cell:
                        all_numbers.append(num)
                        if 'giaiDb' in cell.get('class', []):
                            special_prizes.append(num)

        if not all_numbers: return None

        # Mapping dữ liệu
        if special_prizes:
            ket_qua_dict["special"] = special_prizes[0]
        else:
            ket_qua_dict["special"] = all_numbers[0] if all_numbers else "000000"

        ket_qua_dict["tat_ca_cac_so"] = all_numbers

        return {
            "date": date_str_app,
            "result": ket_qua_dict
        }

    except Exception as e:
        print(f"Lỗi ngày {date_str_url}: {e}")
        return None

def run_backfill():
    tz_VN = pytz.timezone('Asia/Ho_Chi_Minh')
    today = datetime.now(tz_VN)
    
    full_data = []
    
    for i in range(DAYS_TO_BACKFILL):
        target_date = today - timedelta(days=i)
        data = get_data_for_date(target_date)
        
        if data:
            full_data.append(data)
        
        # Nghỉ 1 xíu để không bị web chặn
        time.sleep(1)

    # Ghi đè vào file data.json
    # Sắp xếp theo ngày tăng dần để đẹp
    full_data.sort(key=lambda x: x['date'])
    
    with open(FILE_JSON, 'w', encoding='utf-8') as f:
        json.dump(full_data, f, ensure_ascii=False, indent=4)
    
    print(f"✅ Đã cập nhật thành công {len(full_data)} ngày vào file {FILE_JSON}")

if __name__ == "__main__":
    run_backfill()
