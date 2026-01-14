# Analisis Alur (TikDownloader Capture)

Dokumen ini merangkum alur utama dari kode JavaScript yang tertangkap pada `main.min.js` serta contoh request/response yang tersedia di dump.

## Alur Utama pada JavaScript

1. **Inisialisasi UI & event**
   - Pada `$(document).ready(...)` ada listener untuk input, tombol convert, popup preview, dan query string. Ketika ada query param `q`, otomatis memanggil pencarian. Ini membuat halaman bisa memuat hasil tanpa klik manual.

2. **Validasi dan pencarian**
   - Fungsi `ksearchvideo()` mengambil nilai input `#s_input`, memvalidasi URL TikTok, lalu melakukan `POST` ke `k_url_search` dengan parameter `q` (URL TikTok) dan `lang` (bahasa). Jika sukses, HTML hasil dimasukkan ke `#search-result`.

3. **Render hasil**
   - Response `ajaxSearch` mengembalikan JSON `{status: "ok", data: "<html>..."}`. HTML inilah yang berisi info video, link unduhan, dan metadata tambahan seperti `k_exp`, `k_token`, serta `k_url_convert`.

4. **Konversi file (opsional)**
   - Fungsi `convertFile()` menyiapkan payload konversi (termasuk token dan expiration) lalu `POST` ke `k_url_convert`. Jika butuh proses asynchronous, `WSCheckStatus()` akan membuka WebSocket untuk menerima progres hingga selesai.

## Jejak Request/Response di Dump

- Request POST `ajaxSearch` direkam di `00012_POST_tikdownloader.io_api_ajaxSearch`.
- Body request berisi `q=<url_tiktok>&lang=id`.
- Response JSON berisi HTML hasil (download link, poster, token, dll.).

## Ringkas Alur Data

1. Input URL → validasi.
2. POST `/api/ajaxSearch` → JSON response.
3. HTML hasil berisi link unduh + token konversi.
4. (Opsional) POST `k_url_convert` → file siap download.

# Framework Pemanfaatan AI (Ringkas)

## Writing Assistance
- Ideasi terstruktur (outline → draft → refine), gunakan prompt eksplisit untuk gaya & audiens.
- Lakukan **iterasi**: minta versi lebih singkat/lebih formal, cek konsistensi istilah, dan periksa fakta.
- Gunakan checklist editorial: akurasi, koherensi, dan voice.

## Coding & Debugging
- Pecah tugas jadi unit kecil: "jelaskan fungsi", "sarankan perubahan", lalu "refactor".
- Minta AI membuat test case sebelum refactor untuk menjaga perilaku.
- Untuk debugging, berikan error log + input minimal reproduksi.

## Learning New Subjects
- Mulai dari peta konsep → lanjut ke contoh → latihan terarah.
- Gunakan sesi tanya jawab bertahap untuk memastikan pemahaman.
- Terapkan *spaced repetition* dan *retrieval practice*.

## Creative Brainstorming
- Minta variasi ide dalam beberapa kategori (ekstrem, realistis, murah).
- Gunakan teknik *SCAMPER*, *random stimulus*, atau analogi lintas domain.
- Lakukan evaluasi singkat (impact vs effort) untuk memilih ide.

## Daily Advice (Non-Medical/Legal)
- Jelaskan batasan: saran bukan pengganti profesional.
- Berikan opsi, bukan instruksi mutlak.
- Sertakan konteks risiko dan kapan harus mencari bantuan ahli.
