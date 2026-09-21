# Program Vigenere Cipher: Enkripsi dan Dekripsi

# Enkripsi : C_i = (P_i + K_i) mod 26
# Dekripsi : P_i = (C_i - K_i + 26) mod 26

MOD = 26

def to_num(c):
    return ord(c.upper()) - ord('A')


def to_char(n):
    return chr((n % MOD) + ord('A'))


def clean_text(text):
    return ''.join(ch for ch in text.upper() if ch.isalpha())


def extend_key(text, key):
    text = clean_text(text)
    key = clean_text(key)
    
    if not key:
        raise ValueError("Kunci tidak boleh kosong!")
        
    repeated_key = ""
    for i in range(len(text)):
        repeated_key += key[i % len(key)]
        
    return repeated_key


def vigenere_encrypt(plaintext, key):
    pt = clean_text(plaintext)
    ext_key = extend_key(pt, key)
    ciphertext = ""
    
    for i in range(len(pt)):
        c_val = (to_num(pt[i]) + to_num(ext_key[i])) % MOD
        ciphertext += to_char(c_val)
        
    return ciphertext


def vigenere_decrypt(ciphertext, key):
    ct = clean_text(ciphertext)
    ext_key = extend_key(ct, key)
    plaintext = ""
    
    for i in range(len(ct)):
        p_val = (to_num(ct[i]) - to_num(ext_key[i]) + MOD) % MOD
        plaintext += to_char(p_val)
        
    return plaintext


if __name__ == "__main__":
    while True:
        print("\n=== PROGRAM VIGENERE CIPHER ===")
        print("1. Enkripsi")
        print("2. Dekripsi")
        print("3. Keluar")

        pilihan = input("Pilih menu: ")

        if pilihan == "1":
            plaintext = input("Masukkan plaintext: ")
            key = input("Masukkan kunci: ")

            try:
                ciphertext = vigenere_encrypt(plaintext, key)

                print("\n=== HASIL ENKRIPSI ===")
                print(f"Plaintext : {plaintext}")
                print(f"Key       : {clean_text(key)}")
                print(f"Key Extend: {extend_key(plaintext, key)}")
                print(f"Ciphertext: {ciphertext}")

            except ValueError as e:
                print(e)

        elif pilihan == "2":
            ciphertext = input("Masukkan ciphertext: ")
            key = input("Masukkan kunci: ")

            try:
                plaintext = vigenere_decrypt(ciphertext, key)

                print("\n=== HASIL DEKRIPSI ===")
                print(f"Ciphertext: {clean_text(ciphertext)}")
                print(f"Key       : {clean_text(key)}")
                print(f"Key Extend: {extend_key(ciphertext, key)}")
                print(f"Plaintext : {plaintext}")

            except ValueError as e:
                print(e)

        elif pilihan == "3":
            print("Program selesai.")
            break

        else:
            print("Pilihan tidak valid!")