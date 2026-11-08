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

Data disimpan di `localStorage` browser dan bisa disinkron ke server (lihat bawah).
"Ekspor cadangan (JSON)" tetap tersedia sebagai cadangan tambahan.

## Sinkron server (GitHub Gist)

Tab Ringkasan → kartu "Sinkron server". Data dikirim ke satu **gist privat**
(`checklist-skripsi.json`) di akun GitHub, sehingga:
- tidak hilang kalau HP rusak / cache browser terhapus,
- sama di HP dan laptop,
- punya riwayat versi (halaman gist → Revisions) untuk mengembalikan data lama.

Cara pasang:
1. Buat token klasik di https://github.com/settings/tokens/new?scopes=gist dengan izin
   **gist saja**; atur kedaluwarsa sampai setelah sidang.
2. Perangkat pertama: tempel token, Gist ID dikosongkan → gist dibuat otomatis.
3. Perangkat lain: tempel token yang sama + Gist ID (atau URL gist) dari perangkat pertama.

Cara kerja: tetap offline-first. Setiap perubahan dicatat waktu ubahnya per item
(`S.ts`). Saat sinkron (2,5 s setelah perubahan, saat aplikasi dibuka, saat internet
kembali), aplikasi mengambil gist, menggabungkan per item (yang paling baru diubah
menang), lalu mengirim balik bila ada yang lebih baru di perangkat. Token disimpan
terpisah di perangkat (`edrones-sync-v1`), tidak ikut file ekspor maupun gist.

## Menjalankan

    cd ~/checklist-skripsi-edrones && python3 -m http.server 8000

Lalu buka http://localhost:8000.

Di HP (offline di lapangan): halaman perlu disajikan lewat **https** sekali supaya
service worker menyimpan cache, misalnya lewat GitHub Pages / Netlify Drop. Setelah
dibuka sekali, pilih "Tambahkan ke layar utama"; berikutnya bisa dibuka tanpa internet.

Setelah mengubah `index.html`, naikkan `VERSION` di `sw.js`.
