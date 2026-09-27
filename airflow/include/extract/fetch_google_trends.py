
# %%
from pytrends.request import TrendReq
import pandas as pd
import time
import os

# %%
# koneksi pytrends
pytrends = TrendReq(
    hl='id',
    tz=420
)

keywords = [
    'wisata bali',
    'wisata yogyakarta',
    'wisata lombok',
    'wisata palembang',
    'wisata surabaya'
]

# request data
pytrends.build_payload(
    keywords,
    timeframe='2023-01-01 2025-12-31',
    geo='ID'
)

# delay biar ga kena rate limit
time.sleep(5)

# ambil data
df = pytrends.interest_over_time()

# hapus kolom isPartial
if 'isPartial' in df.columns:
    df = df.drop(columns=['isPartial'])

# reset index
df = df.reset_index()

# rename kolom tanggal
df.rename(columns={'date':'tanggal'}, inplace=True)
df.rename(columns={'wisata bali':'wisata_bali'}, inplace=True)
df.rename(columns={'wisata yogyakarta':'wisata_yogyakarta'}, inplace=True)
df.rename(columns={'wisata lombok':'wisata_lombok'}, inplace=True)
df.rename(columns={'wisata palembang':'wisata_palembang'}, inplace=True)
df.rename(columns={'wisata surabaya':'wisata_surabaya'}, inplace=True)
df.head()

output_dir = os.path.join('data', 'raw', 'google_trends')
os.makedirs(output_dir, exist_ok=True)

# save csv
df.to_csv(os.path.join(output_dir, 'raw_google_trends.csv'), index=False)

