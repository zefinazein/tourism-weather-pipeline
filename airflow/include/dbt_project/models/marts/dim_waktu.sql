with bulan_seq as (
    select offset_bulan
    from unnest(generate_array(0,35)) as offset_bulan
),

tanggal_dasar as (
    select
        offset_bulan,
        date_add('2023-01-01', interval offset_bulan month) as tgl
    from bulan_seq
)

select
    row_number() over (order by offset_bulan) as id_waktu,
    extract(year from tgl) as tahun,
    extract(month from tgl) as bulan,
    format_date('%B', tgl) as nama_bulan,
    cast(ceil(extract(month from tgl) / 3.0) as int64) as kuartal,
    case
        when extract(month from tgl) in (11, 12, 1, 2, 3, 4) then 'Hujan'
        else 'Kemarau'
    end as musim
from tanggal_dasar