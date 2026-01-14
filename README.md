# Export Req/Res (Readable)
Berisi folder per-request, dengan urutan sesuai waktu capture.
- 00-meta.txt : ringkasan metadata
- 01-request-headers.txt
- 02-request-body.(txt/json)
- 03-response-headers.txt
- 04-response-body.(json/html/txt/bin)

## Script lokal
- `tikdownloader_local.py` menjalankan alur otomatis tanpa argumen (menggunakan payload dari dump jika tersedia).
- Ringkasan alur dan framework AI tersedia di `ANALYSIS.md`.
