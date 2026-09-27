# Data Dictionary

## Raw layer (raw dataset)

Unfiltered landing tables, one per source, loaded via `load_to_bigquery.py`.

### `raw.raw_bps_kunjungan`

| Column | Type | Description |
|---|---|---|
| `provinsi` | STRING | Province name as it appears in the BPS source (inconsistent casing/spacing) |
| `tahun` | INT | Year |
| `bulan` | INT | Month (1–12) |
| `jumlah_wisman` | INT | Foreign tourist arrivals for the month |
| `jumlah_wisnus` | INT | Domestic tourist arrivals for the month |
| `tpk` | FLOAT | Hotel occupancy rate (%) |
| `rlm` | FLOAT | Average length of stay (nights) |

### `raw.raw_openmeteo_cuaca`

| Column | Type | Description |
|---|---|---|
| `tanggal` | DATE | Date of observation |
| `kota` | STRING | Representative city code for the province (`bali`, `yogyakarta`, `lombok`, `palembang`, `surabaya`) |
| `curah_hujan_mm` | FLOAT | Daily precipitation (mm) |
| `suhu_max_c` | FLOAT | Daily maximum temperature (°C) |
| `suhu_min_c` | FLOAT | Daily minimum temperature (°C) |

### `raw.raw_google_trends`

| Column | Type | Description |
|---|---|---|
| `tanggal` | DATE | Week start date |
| `wisata_bali` | INT | Search-interest score (0–100) for "wisata bali" |
| `wisata_yogyakarta` | INT | Search-interest score (0–100) for "wisata yogyakarta" |
| `wisata_lombok` | INT | Search-interest score (0–100) for "wisata lombok" |
| `wisata_palembang` | INT | Search-interest score (0–100) for "wisata palembang" |
| `wisata_surabaya` | INT | Search-interest score (0–100) for "wisata surabaya" |

## Warehouse layer (warehouse dataset)

### `fact_kunjungan_pariwisata`

Grain: one row per province per month.

| Column | Type | Description |
|---|---|---|
| `id_waktu` | INT | FK → `dim_waktu.id_waktu` |
| `id_provinsi` | INT | FK → `dim_provinsi.id_provinsi` |
| `id_kategori_cuaca` | INT | FK → `dim_kategori_cuaca.id_kategori` |
| `jumlah_wisman` | INT | Foreign tourist arrivals |
| `jumlah_wisnus` | INT | Domestic tourist arrivals |
| `tpk` | FLOAT | Hotel occupancy rate (%) |
| `rlm` | FLOAT | Average length of stay (nights) |
| `avg_suhu` | FLOAT | Average of max/min temperature (°C) |
| `total_curah_hujan` | FLOAT | Total monthly rainfall (mm) |
| `skor_trends` | FLOAT | Average Google Trends score for the month |

### `dim_waktu`

| Column | Type | Description |
|---|---|---|
| `id_waktu` | INT | Primary key |
| `tahun` | INT | Year |
| `bulan` | INT | Month (1–12) |
| `nama_bulan` | STRING | Month name in English (from `FORMAT_DATE('%B', ...)`) |
| `kuartal` | INT | Quarter (1–4) |
| `musim` | STRING | `Hujan` (Nov–Apr) or `Kemarau` (May–Oct) |

### `dim_provinsi`

| Column | Type | Description |
|---|---|---|
| `id_provinsi` | INT | Primary key |
| `nama_provinsi` | STRING | Province name, uppercase, standardized |
| `kota_cuaca` | STRING | Representative weather city, matches `raw_openmeteo_cuaca.kota` |
| `latitude` / `longitude` | FLOAT | Coordinates of the representative city |
| `pulau` | STRING | Island grouping (Bali, Jawa, Lombok, Sumatera) |

### `dim_kategori_cuaca`

| Column | Type | Description |
|---|---|---|
| `id_kategori` | INT | Primary key |
| `kategori` | STRING | `Kering`, `Normal`, `Basah`, `Sangat Basah` |
| `range_hujan` | STRING | Human-readable rainfall range |
| `min_mm` / `max_mm` | FLOAT | Bounds used to resolve `total_curah_hujan` into a category |
