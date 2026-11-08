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
(18 terbang: prosedur + form catatan + status), Analisis, Skripsi, Bimbingan, Sidang.

Data disimpan di `localStorage` browser dan bisa disinkron ke server (lihat bawah).
"Ekspor cadangan (JSON)" tetap tersedia sebagai cadangan tambahan.

## Sinkron server (GitHub Gist)

Tab Ringkasan → kartu "Sinkron server". Data dikirim ke satu **gist privat**
(`checklist-skripsi.json`) di akun GitHub, sehingga:
- tidak hilang kalau HP rusak / cache browser terhapus,
- sama di HP dan laptop,
- punya riwayat versi (halaman gist → Revisions) untuk mengembalikan data lama.

Cara pasang:
1. Buat token klasik di https://github.com/settings/tokens/new?scopes=gist,public_repo dengan izin
   **gist** dan **public_repo** (untuk issue di repo FC); atur kedaluwarsa sampai setelah sidang.
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

## Tab Bimbingan

Satu entri per bimbingan: tanggal, dosen, topik, catatan bebas, tanggal bimbingan berikutnya,
dan daftar **poin masukan** (baris catatan yang diawali `-`, `*`, `•` atau nomor bisa diubah
jadi poin dengan satu tombol).

Setiap poin bisa:
- **dijadikan tugas** di grup tab lain (Skripsi, Analisis, Persiapan, Sidang). Tugas dan poin
  memakai centang yang sama, jadi mencentang di salah satu tempat menandai keduanya.
- **dijadikan issue** di repo flight controller (`SKRIPSI-FIXEDWING/flightcontroller-Edrones`).
  Dengan token ber-izin `public_repo` issue dibuat otomatis; tanpa itu, aplikasi membuka form
  issue yang sudah terisi lalu link issue ditempel kembali. Saat sinkron, issue yang sudah
  ditutup di GitHub otomatis mencentang poinnya.

Ringkasan menampilkan masukan yang belum selesai dan jadwal bimbingan berikutnya.
