# Checklist Skripsi Edrones

Aplikasi web satu halaman untuk checklist dari persiapan terbang sampai sidang skripsi.

Terhubung ke project flight controller:
- Repo: https://github.com/SKRIPSI-FIXEDWING/flightcontroller-Edrones
- Folder lokal: `~/flightcontroller-Edrones` (bisa diubah di tab Ringkasan)
- Isi checklist terbang mengikuti `docs/checklist-terbang-november-2026.md` di project itu.
  Kalau checklist di project berubah, sesuaikan juga `GROUPS`, `PARAMS`, `FLIGHTS`, dan
  `flightSteps()` di `index.html`.
- Perintah analisis di tab Analisis memanggil skrip `tools/flight_analysis/*.py` di project itu.

Tab: Ringkasan (progres, hitung mundur sidang, link project, cadangan data), Persiapan
(firmware, parameter, misi), Hari terbang (checklist per hari + uji U1), Terbang
(18 terbang: prosedur + form catatan + status), Analisis, Skripsi, Sidang.

Data disimpan di `localStorage` browser, **hanya di perangkat itu**. Pakai
"Ekspor cadangan (JSON)" secara rutin; "Impor JSON" untuk memindah ke HP/laptop lain.

## Menjalankan

    cd ~/checklist-skripsi-edrones && python3 -m http.server 8000

Lalu buka http://localhost:8000.

Di HP (offline di lapangan): halaman perlu disajikan lewat **https** sekali supaya
service worker menyimpan cache, misalnya lewat GitHub Pages / Netlify Drop. Setelah
dibuka sekali, pilih "Tambahkan ke layar utama"; berikutnya bisa dibuka tanpa internet.

Setelah mengubah `index.html`, naikkan `VERSION` di `sw.js`.
