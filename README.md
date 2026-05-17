# VAR Simulator — Grafika Komputer

Final Project mata kuliah Grafika Komputer 2025.
Simulator **Video Assistant Referee (VAR)** sepak bola berbasis Python 2D yang menerapkan algoritma dan konsep Grafika Komputer.

## 🎯 Konsep Grafika Komputer yang Diterapkan
1. **Transformasi Matriks (2D Scaling & Translation):** Digunakan pada fitur Zoom (Kaca Pembesar) VAR. Alih-alih meresize gambar biasa, sistem mengambil sub-region berpusat di titik target (`target_x, target_y`) dan mengalikannya dengan faktor skala (×1.6, ×2.4, dst) lalu merendernya ke ukuran monitor penuh.
2. **Algoritma Garis Bresenham:** Digunakan pada fitur "Draw Line" (Tarik Garis) untuk mendeteksi Offside. Algoritma ini menggambar garis piksel demi piksel menggunakan kalkulasi *integer* murni (tanpa angka desimal) sehingga sangat efisien dalam komputasi grafis dasar.
3. **Konversi Pixel ke Koordinat Normal:** Mengubah posisi klik mouse pada monitor (yang dipengaruhi zoom) menjadi titik koordinat relatif (0.0 – 1.0) di layar sebenarnya.

## 🎮 Fitur Utama
- **Video Player Integration:** Mampu memutar tayangan ulang video `.mp4` secara *frame-by-frame* menggunakan OpenCV (`cv2`).
- **Dynamic Category Loading:** Memilih dan memutar video secara *random* dari folder kategori pelanggaran (`assets/pelanggaran_keras`, `assets/handball`, `assets/offside`).
- **Video Control:** Pause, Play, Lewati frame (-5f / +5f), Rewind, dan Scrubbing menggunakan slider.
- **Decision Panel:** Tentukan keputusan akhir (Foul / Penalti / Kartu Merah / Tidak Foul) berdasarkan hasil analisis video.

## ⚙️ Persyaratan (Requirements)
Pastikan Python 3.x sudah terinstall di komputermu. Library yang dibutuhkan:
```bash
pip install pygame-ce numpy opencv-python
```

## 🚀 Cara Menjalankan
1. Clone repository ini.
2. Siapkan video contoh pelanggaran berformat `.mp4`.
3. Masukkan video tersebut ke dalam direktori assets sesuai kategorinya:
   - `assets/pelanggaran_keras/`
   - `assets/handball/`
   - `assets/offside/`
4. Jalankan script utama:
   ```bash
   python main.py
   ```
