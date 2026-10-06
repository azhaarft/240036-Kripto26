# Nama : Azhaar Fathin Tsuraya
# NPM  : 140810240036
# Ket  : Tugas Steganography

import os
import math
import random
import struct

from PIL import Image


MAGIC = b"STG1"

# magic | m_bits | mode | tipe | panjang_nama | panjang_data
HEADER_FMT = ">4sBBBBI"
HEADER_BYTES = struct.calcsize(HEADER_FMT)
HEADER_BITS = HEADER_BYTES * 8

MODE_SEQ = 0
MODE_RANDOM = 1

TYPE_TEXT = 0
TYPE_FILE = 1


# ============================= Fungsi Bit =============================

def bytes_to_bits(data):
    return "".join(format(byte, "08b") for byte in data)


def bits_to_bytes(bits):
    jumlah_bit = len(bits) - (len(bits) % 8)
    bits = bits[:jumlah_bit]

    hasil = bytearray()

    for i in range(0, len(bits), 8):
        hasil.append(int(bits[i:i + 8], 2))

    return bytes(hasil)


# ============================= Fungsi Citra =============================

def load_image(path):
    image = Image.open(path).convert("RGB")
    pixel_data = bytearray(image.tobytes())

    return image, pixel_data


def save_image(image_size, pixel_data, path):
    image = Image.frombytes("RGB", image_size, bytes(pixel_data))
    image.save(path)


# ============================= Posisi Penyimpanan =============================

def slot_positions(total_bytes, jumlah_slot, mode, seed):
    ruang_tersedia = total_bytes - HEADER_BITS

    if jumlah_slot > ruang_tersedia:
        raise ValueError("Kapasitas citra tidak cukup.")

    if mode == MODE_SEQ:
        posisi = range(HEADER_BITS, HEADER_BITS + jumlah_slot)
        return list(posisi)

    random_generator = random.Random(seed)
    posisi_acak = random_generator.sample(range(ruang_tersedia), jumlah_slot)

    return [HEADER_BITS + posisi for posisi in posisi_acak]


def capacity_bytes(total_bytes, jumlah_bit):
    return ((total_bytes - HEADER_BITS) * jumlah_bit) // 8


# ============================= Encode =============================

def encode(cover_path, output_path, payload, file_name, data_type,
           jumlah_bit, mode, seed):

    image, pixel_data = load_image(cover_path)

    data_body = file_name + payload

    kapasitas = (len(pixel_data) - HEADER_BITS) * jumlah_bit

    if len(data_body) * 8 > kapasitas:
        raise ValueError(
            f"Pesan terlalu besar. Kapasitas maksimum: "
            f"{capacity_bytes(len(pixel_data), jumlah_bit)} byte "
            f"(pesan + nama file = {len(data_body)} byte)."
        )

    pixel_awal = bytes(pixel_data)

    # Menyimpan informasi utama pada 96 byte pertama
    header = struct.pack(
        HEADER_FMT,
        MAGIC,
        jumlah_bit,
        mode,
        data_type,
        len(file_name),
        len(payload)
    )

    header_bits = bytes_to_bits(header)

    for i, bit in enumerate(header_bits):
        pixel_data[i] = (pixel_data[i] & 0xFE) | int(bit)

    # Menyiapkan data yang akan disembunyikan
    data_bits = bytes_to_bits(data_body)

    sisa_bit = len(data_bits) % jumlah_bit
    if sisa_bit != 0:
        data_bits += "0" * (jumlah_bit - sisa_bit)

    jumlah_slot = len(data_bits) // jumlah_bit

    posisi_data = slot_positions(
        len(pixel_data),
        jumlah_slot,
        mode,
        seed
    )

    mask = 0xFF ^ ((1 << jumlah_bit) - 1)

    for i, posisi in enumerate(posisi_data):
        potongan_bit = data_bits[
            i * jumlah_bit:(i + 1) * jumlah_bit
        ]

        nilai_bit = int(potongan_bit, 2)

        pixel_data[posisi] = (
            (pixel_data[posisi] & mask) | nilai_bit
        )

    save_image(image.size, pixel_data, output_path)

    return psnr(pixel_awal, bytes(pixel_data))


# ============================= Decode =============================

def decode(stego_path, seed):

    image, pixel_data = load_image(stego_path)

    if len(pixel_data) < HEADER_BITS:
        raise ValueError("Citra terlalu kecil.")

    header_bits = ""

    for i in range(HEADER_BITS):
        header_bits += str(pixel_data[i] & 1)

    header_data = bits_to_bytes(header_bits)

    magic, jumlah_bit, mode, data_type, name_length, data_length = struct.unpack(
        HEADER_FMT,
        header_data
    )

    if (
        magic != MAGIC
        or not (1 <= jumlah_bit <= 8)
        or mode not in (MODE_SEQ, MODE_RANDOM)
    ):
        raise ValueError(
            "Tidak ditemukan pesan tersembunyi (header tidak valid)."
        )

    total_bit = (name_length + data_length) * 8
    jumlah_slot = math.ceil(total_bit / jumlah_bit)

    posisi_data = slot_positions(
        len(pixel_data),
        jumlah_slot,
        mode,
        seed
    )

    data_bits = ""

    for posisi in posisi_data:
        nilai = pixel_data[posisi] & ((1 << jumlah_bit) - 1)
        data_bits += format(nilai, f"0{jumlah_bit}b")

    data_bits = data_bits[:total_bit]

    data_body = bits_to_bytes(data_bits)

    file_name = data_body[:name_length]
    payload = data_body[name_length:]

    return data_type, file_name, payload, jumlah_bit, mode


# ============================= Steganalysis =============================

def enhanced_lsb_attack(input_path, output_path):
    """
    Menampilkan nilai LSB sebagai gambar hitam-putih.
    LSB 1 menjadi putih dan LSB 0 menjadi hitam.
    """

    image, pixel_data = load_image(input_path)

    hasil_analisis = bytearray(
        255 if byte & 1 else 0
        for byte in pixel_data
    )

    save_image(
        image.size,
        hasil_analisis,
        output_path
    )


# ============================= Perhitungan PSNR =============================

def psnr(data_awal, data_akhir):

    mse = sum(
        (nilai_awal - nilai_akhir) ** 2
        for nilai_awal, nilai_akhir in zip(data_awal, data_akhir)
    ) / len(data_awal)

    if mse == 0:
        return float("inf")

    return 10 * math.log10((255 ** 2) / mse)


# ============================= Input =============================

def ask(prompt, default=None):

    if default is not None:
        teks_input = input(
            prompt + f" [{default}]: "
        ).strip()
    else:
        teks_input = input(prompt + ": ").strip()

    if teks_input:
        return teks_input

    return default if default is not None else ""


def ask_existing_file(prompt):

    while True:
        file_path = ask(prompt).strip('"')

        if os.path.isfile(file_path):
            return file_path

        print("  ! File tidak ditemukan, coba lagi.")


def ask_int(prompt, minimum, maksimum, default):

    while True:
        nilai = ask(prompt, default)

        if str(nilai).isdigit():
            nilai = int(nilai)

            if minimum <= nilai <= maksimum:
                return nilai

        print(
            f"  ! Masukkan angka {minimum}-{maksimum}."
        )


def ask_mode_and_seed():

    mode = ask_int(
        "Mode (0 = sequential, 1 = acak)",
        0,
        1,
        0
    )

    seed = None

    if mode == MODE_RANDOM:
        seed = ask("Stego-key / seed (angka atau kata)")

    return mode, seed


# ============================= Menu Encode =============================

def menu_encode():

    print("\n=== ENCODE ===")

    cover_path = ask_existing_file(
        "Path citra cover (png/bmp/jpg)"
    )

    image, pixel_data = load_image(cover_path)

    print(
        f"  Ukuran citra: "
        f"{image.size[0]}x{image.size[1]} px"
    )

    data_type = ask_int(
        "Yang disembunyikan (0 = teks, 1 = file/gambar)",
        0,
        1,
        0
    )

    if data_type == TYPE_TEXT:

        payload = ask(
            "Ketik pesan rahasia"
        ).encode("utf-8")

        file_name = b""

    else:

        file_path = ask_existing_file(
            "Path file yang disembunyikan"
        )

        with open(file_path, "rb") as file:
            payload = file.read()

        file_name = os.path.basename(
            file_path
        ).encode("utf-8")[:255]

    jumlah_bit = ask_int(
        "Jumlah bit LSB per byte (1-8)",
        1,
        8,
        1
    )

    mode, seed = ask_mode_and_seed()

    output_path = ask(
        "Nama file stego-image output (.png)",
        "stego.png"
    )

    if not output_path.lower().endswith((".png", ".bmp")):
        output_path += ".png"

    try:

        nilai_psnr = encode(
            cover_path,
            output_path,
            payload,
            file_name,
            data_type,
            jumlah_bit,
            mode,
            seed
        )

    except ValueError as error:

        print("  ! Gagal:", error)
        return

    print(
        f"\n  Berhasil! Stego-image disimpan di: "
        f"{output_path}"
    )

    print(
        f"  Ukuran pesan : {len(payload)} byte "
        f"(kapasitas max "
        f"{capacity_bytes(len(pixel_data), jumlah_bit)} byte "
        f"dengan {jumlah_bit}-bit LSB)"
    )

    if nilai_psnr == float("inf"):
        nilai_psnr = "tak hingga"
    else:
        nilai_psnr = f"{nilai_psnr:.2f} dB"

    print(
        f"  PSNR         : {nilai_psnr} "
        "(>40 dB = perubahan sulit terlihat)"
    )


# ============================= Menu Decode =============================

def menu_decode():

    print("\n=== DECODE ===")

    stego_path = ask_existing_file(
        "Path stego-image"
    )

    seed = ask(
        "Stego-key / seed (kosongkan jika mode sequential)"
    ) or None

    try:

        data_type, file_name, payload, jumlah_bit, mode = decode(
            stego_path,
            seed
        )

    except ValueError as error:

        print("  ! Gagal:", error)
        return

    mode_text = "acak" if mode else "sequential"

    print(
        f"  Terdeteksi: {jumlah_bit}-bit LSB, "
        f"mode {mode_text}"
    )

    if data_type == TYPE_TEXT:

        try:
            print(
                "\n  Pesan tersembunyi:",
                payload.decode("utf-8")
            )

        except UnicodeDecodeError:

            print(
                "  ! Data tidak bisa di-decode sebagai teks "
                "(seed salah?)."
            )

    else:

        file_name_text = file_name.decode(
            "utf-8",
            errors="replace"
        ) or "hasil_ekstrak.bin"

        output_path = ask(
            "Simpan file hasil ekstrak sebagai",
            "extracted_" + os.path.basename(file_name_text)
        )

        with open(output_path, "wb") as file:
            file.write(payload)

        print(
            f"  File tersimpan di: "
            f"{output_path} ({len(payload)} byte)"
        )


# ============================= Menu Attack =============================

def menu_attack():

    print(
        "\n=== STEGANALYSIS: Enhanced LSB Attack ==="
    )

    input_path = ask_existing_file(
        "Path citra yang dianalisis"
    )

    output_path = ask(
        "Nama file hasil analisis",
        "enhanced_lsb.png"
    )

    enhanced_lsb_attack(
        input_path,
        output_path
    )

    print(
        f"  Selesai. Buka {output_path}: "
        "area noise acak menandakan kemungkinan ada "
        "pesan tersembunyi."
    )


# ============================= Program Utama =============================

def main():

    while True:

        print("\n===== LSB STEGANOGRAPHY =====")
        print("1. Encode (sembunyikan pesan/file)")
        print("2. Decode (ekstrak pesan/file)")
        print("3. Steganalysis - Enhanced LSB Attack")
        print("0. Keluar")

        pilihan = ask("Pilih menu")

        if pilihan == "1":
            menu_encode()

        elif pilihan == "2":
            menu_decode()

        elif pilihan == "3":
            menu_attack()

        elif pilihan == "0":
            print("Bye")
            break

        else:
            print("  ! Pilihan tidak valid.")


if __name__ == "__main__":
    main()