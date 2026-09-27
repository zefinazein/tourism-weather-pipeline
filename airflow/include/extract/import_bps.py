"""
BPS Data Merger — Final Version
Menggabungkan data wisman, wisnus, TPK, RLM dari berbagai file BPS
menjadi satu tabel bersih: 5 provinsi x 36 bulan (2023-2025)

Dua tipe struktur file BPS yang di-handle:
  Tipe A: row0=tahun (ada angka 2023/2024/2025), row1=bulan, row2+=data
  Tipe B: row0=bulan saja (tanpa tahun eksplisit), row1+=data
"""

import pandas as pd
import numpy as np
import os, gc

DATA   = "../data/raw/bps_dynamic_tables"
OUTPUT = "../data/raw/bps/output_bps.xlsx"

BULAN = {
    "Januari":1,"Februari":2,"Maret":3,"April":4,
    "Mei":5,"Juni":6,"Juli":7,"Agustus":8,
    "September":9,"Oktober":10,"November":11,"Desember":12
}
TAHUN    = [2023, 2024, 2025]
PROVINSI = ["BALI","DI YOGYAKARTA","JAWA TIMUR",
            "NUSA TENGGARA BARAT","SUMATERA SELATAN"]

PINTU_MAP = {
    "Ngurah Rai":           "BALI",
    "Adi Sucipto":          "DI YOGYAKARTA",
    "Bandara Int. Lombok":  "NUSA TENGGARA BARAT",
    "Sultan Badaruddin II": "SUMATERA SELATAN",
    "Juanda":               "JAWA TIMUR",
}


def clean_val(s):
    s = str(s).strip().replace(",", ".").replace("-", "").replace("–", "")
    try:
        return float(s) if s and s != "nan" else np.nan
    except ValueError:
        return np.nan


# ── PARSER TIPE A ───────────────────────────────────────────
# row0=tahun eksplisit, row1=bulan, row2+=data

def parse_tipe_a(filepath):
    raw = pd.read_csv(filepath, header=None, skiprows=1,
                      encoding="utf-8-sig", dtype=str).dropna(how="all").reset_index(drop=True)

    tahun_row = raw.iloc[0, 1:].tolist()
    bulan_row = raw.iloc[1, 1:].tolist()

    cur = None
    tahun_ff = []
    for t in tahun_row:
        t = str(t).strip()
        if t.isdigit() and int(t) in TAHUN:
            cur = int(t)
        tahun_ff.append(cur)

    col_keys = []
    for t, b in zip(tahun_ff, bulan_row):
        b = str(b).strip()
        col_keys.append((t, BULAN[b]) if (b in BULAN and t) else None)

    result = {}
    for _, row in raw.iloc[2:].iterrows():
        entitas = str(row.iloc[0]).strip()
        if not entitas or entitas == "nan" or entitas.lower().startswith("catatan"):
            continue
        for ci, ck in enumerate(col_keys):
            if ck is None:
                continue
            result.setdefault(ck, {})[entitas] = clean_val(row.iloc[ci + 1])
    return result


# ── PARSER TIPE B ───────────────────────────────────────────
# row0=bulan (berulang untuk setiap tahun, tanpa angka tahun), row1+=data

def parse_tipe_b(filepath, tahun_list):
    """
    Tipe B: tidak ada baris tahun eksplisit.
    Deteksi pergantian tahun dengan menghitung grup 12 bulan.
    Kolom 'Tahunan' di-skip (bukan nama bulan).
    """
    raw = pd.read_csv(filepath, header=None, skiprows=2,
                      encoding="utf-8-sig", dtype=str).dropna(how="all").reset_index(drop=True)

    bulan_row = raw.iloc[0, 1:].tolist()

    # Hitung posisi kolom Januari untuk deteksi pergantian tahun
    col_keys = []
    tidx = 0
    jan_count = 0  # berapa kali Januari sudah muncul di tahun ini
    bulan_in_group = 0  # berapa bulan sudah diproses dalam tahun ini

    for b in bulan_row:
        b = str(b).strip()
        if b not in BULAN:
            col_keys.append(None)  # Tahunan atau kosong, skip
            continue

        bnum = BULAN[b]

        # Jika Januari muncul lagi dan sudah ada bulan sebelumnya → tahun baru
        if bnum == 1 and bulan_in_group > 0:
            tidx += 1
            bulan_in_group = 0

        t = tahun_list[tidx] if tidx < len(tahun_list) else None
        col_keys.append((t, bnum) if t else None)
        bulan_in_group += 1

    result = {}
    for _, row in raw.iloc[1:].iterrows():
        entitas = str(row.iloc[0]).strip()
        if not entitas or entitas == "nan" or entitas.lower().startswith("catatan"):
            continue
        for ci, ck in enumerate(col_keys):
            if ck is None:
                continue
            result.setdefault(ck, {})[entitas] = clean_val(row.iloc[ci + 1])
    return result


# ── AGGREGATOR HELPERS ──────────────────────────────────────

def agg_mean(data_dict, provinsi, col, exclude_kw=None):
    rows = []
    for (tahun, bulan), ents in data_dict.items():
        vals = [v for k, v in ents.items()
                if not np.isnan(v)
                and (not exclude_kw or not any(x.lower() in k.lower() for x in exclude_kw))]
        rows.append({"provinsi": provinsi, "tahun": tahun, "bulan": bulan,
                     col: np.mean(vals) if vals else np.nan})
    return pd.DataFrame(rows)


def agg_sum(data_dict, provinsi, col, exclude_kw=None):
    rows = []
    for (tahun, bulan), ents in data_dict.items():
        vals = [v for k, v in ents.items()
                if not np.isnan(v)
                and (not exclude_kw or not any(x.lower() in k.lower() for x in exclude_kw))]
        rows.append({"provinsi": provinsi, "tahun": tahun, "bulan": bulan,
                     col: sum(vals) if vals else np.nan})
    return pd.DataFrame(rows)


def get_single(data_dict, provinsi, col, key_substr):
    rows = []
    for (tahun, bulan), ents in data_dict.items():
        val = next((v for k, v in ents.items() if key_substr.lower() in k.lower()), np.nan)
        rows.append({"provinsi": provinsi, "tahun": tahun, "bulan": bulan, col: val})
    return pd.DataFrame(rows)


# ── LOADERS ─────────────────────────────────────────────────

def load_wisman():
    print("  [wisman]", end=" ", flush=True)
    data = parse_tipe_a(os.path.join(DATA, "wisman_2023_2025.csv"))
    rows = []
    for (tahun, bulan), ents in data.items():
        for pintu, provinsi in PINTU_MAP.items():
            val = next((v for k, v in ents.items() if pintu.lower() in k.lower()), np.nan)
            rows.append({"provinsi": provinsi, "tahun": tahun,
                         "bulan": bulan, "jumlah_wisman": val})
    df = pd.DataFrame(rows).groupby(["provinsi","tahun","bulan"], as_index=False)["jumlah_wisman"].first()
    print(f"{len(df)} baris ✓")
    return df


def load_wisnus():
    print("  [wisnus]", end=" ", flush=True)
    dfs = []

    # Yogyakarta — tipe B, sudah level provinsi
    d = parse_tipe_b(os.path.join(DATA, "wisnus_yogyakarta_2023_2025.csv"), TAHUN)
    dfs.append(get_single(d, "DI YOGYAKARTA", "jumlah_wisnus", "DI Yogyakarta"))

    # Sumsel — tipe A, pakai baris total "Sumatera Selatan"
    d = parse_tipe_a(os.path.join(DATA, "wisnus_sumsel_2023_2025.csv"))
    dfs.append(get_single(d, "SUMATERA SELATAN", "jumlah_wisnus", "Sumatera Selatan"))

    # Bali & NTB — tipe B (kab/kota), jumlahkan semua
    for fname, provinsi in [("wisnus_bali_2023_2025.csv", "BALI"),
                             ("wisnus_ntb_2023_2025.csv",  "NUSA TENGGARA BARAT")]:
        d = parse_tipe_b(os.path.join(DATA, fname), TAHUN)
        dfs.append(agg_sum(d, provinsi, "jumlah_wisnus"))

    # Jatim — tipe A, pakai baris total "Jawa Timur" (sudah tersedia di file)
    d = parse_tipe_a(os.path.join(DATA, "winus_jatim_2023_2025.csv"))
    dfs.append(get_single(d, "JAWA TIMUR", "jumlah_wisnus", "Jawa Timur"))

    df = pd.concat(dfs, ignore_index=True)
    print(f"{len(df)} baris ✓")
    del dfs; gc.collect()
    return df


def load_tpk():
    print("  [tpk]   ", end=" ", flush=True)
    dfs = []

    # Bali — tipe B, rata-rata semua kelas bintang
    d = parse_tipe_b(os.path.join(DATA, "tpk_bintang_bali_2023_2025.csv"), TAHUN)
    dfs.append(agg_mean(d, "BALI", "tpk"))

    # NTB — tipe A, rata-rata semua kelas bintang
    d = parse_tipe_a(os.path.join(DATA, "tpk_bintang_ntb_2023_2025.csv"))
    dfs.append(agg_mean(d, "NUSA TENGGARA BARAT", "tpk"))

    # Jatim — tipe A, ambil baris "Hotel Bintang" saja
    d = parse_tipe_a(os.path.join(DATA, "tpk_bintang_jatim_2023_2025.csv"))
    dfs.append(get_single(d, "JAWA TIMUR", "tpk", "Hotel Bintang"))

    # Yogyakarta — tipe B, ambil "DI Yogyakarta"
    d = parse_tipe_b(os.path.join(DATA, "tpk_bintang_yogyakarta_2023_2025.csv"), TAHUN)
    dfs.append(get_single(d, "DI YOGYAKARTA", "tpk", "DI Yogyakarta"))

    # Sumsel — tipe A, ambil "Hotel Berbintang"
    d = parse_tipe_a(os.path.join(DATA, "tpk_bintang_sumsel_2023_2025.csv"))
    dfs.append(get_single(d, "SUMATERA SELATAN", "tpk", "Hotel Berbintang"))

    df = pd.concat(dfs, ignore_index=True)
    print(f"{len(df)} baris ✓")
    del dfs; gc.collect()
    return df


def load_rlm():
    print("  [rlm]   ", end=" ", flush=True)
    dfs = []

    # Bali — tipe B, rata-rata semua kelas (gabungan asing+domestik)
    d = parse_tipe_b(os.path.join(DATA, "rlm_bintang_bali_2023_2025.csv"), TAHUN)
    dfs.append(agg_mean(d, "BALI", "rlm"))

    # NTB — tipe A, rata-rata semua kelas
    d = parse_tipe_a(os.path.join(DATA, "rlm_bintang_ntb_2023_2025.csv"))
    dfs.append(agg_mean(d, "NUSA TENGGARA BARAT", "rlm"))

    # Jatim — tipe A, ambil "Jumlah" (sudah gabungan)
    d = parse_tipe_a(os.path.join(DATA, "rlm_bintang_jatim_2023_2025.csv"))
    dfs.append(get_single(d, "JAWA TIMUR", "rlm", "Jumlah"))

    # Yogyakarta — tipe B, ambil "D.I Yogyakarta"
    d = parse_tipe_b(os.path.join(DATA, "rlm_bintang_yogyakarta_2023_2025.csv"), TAHUN)
    dfs.append(get_single(d, "DI YOGYAKARTA", "rlm", "D.I Yogyakarta"))

    # Sumsel — tipe A, rata-rata Tamu Asing dan Domestik
    d = parse_tipe_a(os.path.join(DATA, "rlm_bintang_sumsel_2023_2025.csv"))
    dfs.append(agg_mean(d, "SUMATERA SELATAN", "rlm"))

    df = pd.concat(dfs, ignore_index=True)
    print(f"{len(df)} baris ✓")
    del dfs; gc.collect()
    return df


# ── MAIN ────────────────────────────────────────────────────

def main():
    print("=" * 55)
    print("BPS Data Merger")
    print("=" * 55)

    skeleton = pd.DataFrame([
        {"provinsi": p, "tahun": t, "bulan": b}
        for p in PROVINSI for t in TAHUN for b in range(1, 13)
    ])
    print(f"\nSkeleton: {len(skeleton)} baris\n")
    print("Memuat data:")

    df_wisman = load_wisman()
    df_wisnus = load_wisnus()
    df_tpk    = load_tpk()
    df_rlm    = load_rlm()

    print("\nMenggabungkan...")
    key = ["provinsi", "tahun", "bulan"]
    df  = skeleton.copy()
    for src, label in [(df_wisman,"wisman"),(df_wisnus,"wisnus"),
                       (df_tpk,"tpk"),(df_rlm,"rlm")]:
        df = df.merge(src, on=key, how="left")
        del src; gc.collect()
        print(f"  + {label} ✓")

    # Bulatkan & konversi tipe
    df["tpk"] = df["tpk"].round(2)
    df["rlm"] = df["rlm"].round(2)
    df["jumlah_wisman"] = df["jumlah_wisman"].round(0).astype("Int64")
    df["jumlah_wisnus"] = df["jumlah_wisnus"].round(0).astype("Int64")

    df = df.sort_values(["provinsi","tahun","bulan"]).reset_index(drop=True)
    df.to_csv(OUTPUT, index=False)

    print(f"\n{'='*55}")
    print(f"SELESAI — {len(df)} baris → {OUTPUT}")
    print(f"{'='*55}\n")

    print("NULL per kolom:")
    for col in ["jumlah_wisman","jumlah_wisnus","tpk","rlm"]:
        n = df[col].isna().sum()
        print(f"  {col:25s}: {n:3d} NULL ({n/len(df)*100:.1f}%)")

    print("\nPreview Januari 2023:")
    print(df[(df["bulan"]==1) & (df["tahun"]==2023)].to_string(index=False))
    print("\nPreview November-Desember 2025 (cek NULL):")
    print(df[(df["bulan"]>=11) & (df["tahun"]==2025)].to_string(index=False))

    return df


if __name__ == "__main__":
    main()