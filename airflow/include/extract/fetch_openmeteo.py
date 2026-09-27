import requests
import pandas as pd
import os
import time

output_dir = os.path.join('data', 'raw', 'openmeteo')
os.makedirs(output_dir, exist_ok=True)

kota = {
    'bali':       (-8.67,  115.21),
    'yogyakarta': (-7.80,  110.36),
    'lombok':     (-8.58,  116.10),
    'palembang':  (-2.99,  104.76),
    'surabaya':   (-7.25,  112.75)
}

all_data = []

for nama, (lat, lon) in kota.items():
    url = 'https://archive-api.open-meteo.com/v1/archive'
    params = {
        'latitude':   lat,
        'longitude':  lon,
        'start_date': '2023-01-01',
        'end_date':   '2025-12-31',
        'daily': 'precipitation_sum,temperature_2m_max,temperature_2m_min',
        'timezone': 'Asia/Bangkok'
    }
    
    print(f'Fetching data untuk {nama}...')
    
    for attempt in range(3):
        try:
            r = requests.get(url, params=params, timeout=20)
            r.raise_for_status()
            data = r.json()

            df = pd.DataFrame(data['daily'])
            df['kota'] = nama
            df.rename(columns={
                'time':                'tanggal',
                'precipitation_sum':    'curah_hujan_mm',
                'temperature_2m_max':   'suhu_max_c',
                'temperature_2m_min':   'suhu_min_c'
            }, inplace=True)
            all_data.append(df)
            print(f'  -> {len(df)} baris berhasil diambil')
            break
            
        except Exception as e:
            if attempt < 2:
                print(f'  -> Percobaan {attempt+1} gagal, mencoba lagi...')
                time.sleep(2)
            else:
                print(f'  -> Gagal total mengambil data {nama}: {e}')

if all_data:
    df_all = pd.concat(all_data, ignore_index=True)
    file_path = os.path.join(output_dir, 'raw_cuaca.csv')
    df_all.to_csv(file_path, index=False)
    print(f'\nSelesai! Total {len(df_all)} baris disimpan ke: {file_path}')
else:
    print('Tidak ada data yang berhasil diambil.')