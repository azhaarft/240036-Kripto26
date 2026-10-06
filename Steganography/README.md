# Steganografi LSB pada Citra

Program Python untuk menyembunyikan teks atau file (termasuk gambar) ke dalam citra digital dengan metode Least Significant Bit (LSB), lalu mengekstraknya kembali. Dibuat untuk Tugas 4 Praktikum Kriptografi, Pertemuan 5.

## Fitur

- **Encode**: menyembunyikan teks yang diketik langsung, atau file apa pun, ke dalam citra cover.
- **Decode**: mengambil kembali pesan atau file dari stego-image.
- **Enhanced LSB Attack**: analisis visual untuk melihat apakah sebuah citra kemungkinan berisi pesan tersembunyi.
- Dua mode penyisipan: sequential dan acak (berbasis seed).
- Jumlah bit LSB yang dipakai dapat diatur dari 1 sampai 8 bit per byte.
- Setelah encode, program menampilkan kapasitas citra dan nilai PSNR sebagai ukuran perubahan kualitas.

## Kebutuhan

- Python 3.8 atau lebih baru
- Library Pillow

```
pip install pillow
```

## Cara Menjalankan

```
python LSB.py
```

Program akan menampilkan menu:

```
===== LSB STEGANOGRAPHY =====
1. Encode (sembunyikan pesan/file)
2. Decode (ekstrak pesan/file)
3. Steganalysis - Enhanced LSB Attack
0. Keluar
```

### Encode

Program akan meminta input berikut secara berurutan:

1. Path citra cover (png, bmp, atau jpg).
2. Jenis data yang disembunyikan: `0` untuk teks, `1` untuk file atau gambar.
3. Isi pesan (jika teks) atau path file (jika file).
4. Jumlah bit LSB per byte (1 sampai 8, default 1).
5. Mode penyisipan: `0` untuk sequential, `1` untuk acak. Jika memilih acak, program meminta stego-key (seed).
6. Nama file output (default `stego.png`).

### Decode

1. Masukkan path stego-image.
2. Masukkan stego-key. Kosongkan jika pesan disisipkan dengan mode sequential.

Jika isinya teks, pesan langsung ditampilkan. Jika isinya file, program menanyakan nama file untuk menyimpan hasil ekstrak (default `extracted_<nama asli>`).

### Enhanced LSB Attack

Masukkan path citra yang ingin dianalisis. Program menghasilkan citra baru (default `enhanced_lsb.png`) yang hanya menampilkan bit LSB. Pada citra asli, pola LSB cenderung mengikuti bentuk objek. Pada citra yang berisi pesan, akan tampak area noise acak.

## Cara Kerja

### Prinsip LSB

Setiap piksel citra 24-bit terdiri dari tiga byte (R, G, B). Bit paling kanan pada tiap byte (LSB) hanya berpengaruh sebesar 1 pada nilai warna, sehingga mengubahnya hampir tidak terlihat oleh mata. Bit-bit pesan ditulis ke posisi LSB tersebut.

Contoh: byte `10000010` (130) disisipi bit `1` menjadi `10000011` (131).

### Struktur Data yang Disisipkan

Citra dibaca sebagai deretan byte RGB. Data yang disisipkan terdiri dari dua bagian:

**1. Header (12 byte = 96 bit)**

Disimpan pada 96 byte pertama citra dengan 1-bit LSB, selalu secara sequential. Isinya:

| Field | Ukuran | Keterangan |
|---|---|---|
| Magic | 4 byte | Penanda `STG1` untuk memastikan citra memang berisi pesan |
| Jumlah bit | 1 byte | Jumlah bit LSB yang dipakai (m) |
| Mode | 1 byte | 0 = sequential, 1 = acak |
| Tipe | 1 byte | 0 = teks, 1 = file |
| Panjang nama | 1 byte | Panjang nama file dalam byte |
| Panjang data | 4 byte | Panjang isi pesan dalam byte |

Karena parameter ada di header, saat decode pengguna tidak perlu memasukkan jumlah bit maupun mode. Hanya seed yang perlu diberikan untuk mode acak.

**2. Body**

Berisi nama file (kosong untuk teks) diikuti isi pesan. Body diubah menjadi deretan bit, dipotong per m bit, lalu setiap potongan menggantikan m bit LSB pada satu byte citra. Penyisipan dimulai setelah 96 byte header.

### Mode Penyisipan

- **Sequential**: byte yang dipakai berurutan, mulai dari byte ke-97.
- **Acak**: posisi byte dipilih oleh `random.Random(seed).sample(...)`. Seed berfungsi sebagai stego-key. Saat decode, seed yang sama menghasilkan urutan posisi yang sama. Jika seed salah, data yang terbaca tidak bermakna.

### Jumlah Bit LSB (m-bit)

Semakin banyak bit LSB yang dipakai, semakin besar pesan yang dapat disimpan, tetapi perubahan pada citra juga semakin besar. Kapasitas maksimum dihitung dengan:

```
kapasitas (byte) = ((jumlah byte citra - 96) x m) / 8
```

### PSNR

PSNR dihitung antara citra asli dan stego-image. Nilai di atas sekitar 40 dB umumnya berarti perbedaannya sulit dilihat mata. Nilai ini turun seiring bertambahnya jumlah bit LSB dan ukuran pesan.

## Catatan

- Stego-image harus disimpan dalam format lossless (PNG atau BMP). Format JPEG memakai kompresi lossy yang mengubah nilai piksel sehingga bit LSB rusak dan pesan tidak dapat diekstrak. Karena itu program otomatis menambahkan ekstensi `.png` jika output bukan `.png` atau `.bmp`.
- Citra cover boleh berformat JPG karena hanya dibaca. Citra akan dikonversi ke RGB 24-bit.
- Jika ukuran pesan melebihi kapasitas, program menampilkan pesan kesalahan beserta kapasitas maksimumnya. Gunakan citra yang lebih besar atau naikkan jumlah bit LSB.
- Pesan tidak dienkripsi. Mode acak hanya mempersulit penentuan posisi bit, bukan menyembunyikan isinya. Untuk keamanan yang lebih baik, pesan sebaiknya dienkripsi terlebih dahulu.

## Struktur Folder

```
Steganography/
├── LSB.py
├── README.md
└── screenshot/
```

## Referensi

Materi Praktikum Kriptografi Pertemuan 5: Steganografi, LSB, Steganalysis, dan NoStega.
