# Nama : Azhar Fathin Tsuraya
# NPM  : 140810240036
# Ket  : code hill chiper 

#Enkripsi : C = Mk * Mp 
#Dekripsi : P = Mk^-1 * Mc 

MOD = 26

def to_num(c) :
    return ord(c.upper()) - ord('A')

def to_char(n) : 
    return chr((n % MOD) + ord('A')) 

def prepare_text(text):
    text = ''.join(ch for ch in text.upper() if ch.isalpha())
    if len(text) % 2 != 0:
        text += 'X'
    return text

def determinant(K):
    return K[0][0] * K[1][1] - K[0][1] * K[1][0]

def mod_inverse(a, m=MOD):
    a = a % m
    for x in range(1,m):
        if (a * x) % m == 1:
            return x
    return None

def matrix_inverse(K):
    det = determinant(K) % MOD
    det_inv = mod_inverse(det)
    if det_inv is None:
        raise ValueError(
            f"Determinan matriks tidak koprima dg 26,"
            "kunci ini tidak valid untuk hill chiper."
        )
    a, b = K[0]
    c, d = K[1]
    adjugate = [[d, -b], [-c, a]]
    inverse = [[(det_inv * adjugate[i][j]) % MOD for j in range(2)] for i in range(2)]
    return inverse

def mat_mult_vec(K, v):
    r0 = (K[0][0] * v[0] + K[0][1] * v[1]) % MOD
    r1 = (K[1][0] * v[0] + K[1][1] * v[1]) % MOD
    return [r0, r1]

def mat_mult_mat(A,B):
    result = [[0,0], [0,0]]
    for i in range(2):
        for j in range(2):
            result[i][j] = sum(A[i][k] * B[k][j] for k in range(2)) % MOD
    return result

def hill_encrypt(plaintext, K):
    text = prepare_text(plaintext)
    ciphertext = ''
    for i in range (0, len(text), 2 ):
        pair = [to_num(text[i]), to_num(text[i + 1])]
        c = mat_mult_vec(K, pair)
        ciphertext += to_char(c[0]) + to_char(c[1])
    return ciphertext

def hill_decrypt(ciphertext, K):
    K_inv = matrix_inverse(K)
    text = prepare_text(ciphertext)
    plaintext =''
    for i in range(0, len(text), 2):
        pair = [to_num(text[i]), to_num(text[i + 1])]
        p = mat_mult_vec(K_inv, pair)
        plaintext += to_char(p[0]) + to_char(p[1])
    return plaintext

def find_key(plaintext, ciphertext):
    pt = prepare_text(plaintext)
    ct = prepare_text(ciphertext)
    if len(pt)< 4 or len(ct) < 4:
        raise ValueError("butuh mimal 4 huruf plain text ")

    P = [[to_num(pt[0]), to_num(pt[2])], [to_num(pt[1]), to_num(pt[3])]]
         
    C = [[to_num(ct[0]), to_num(ct[2])], [to_num(ct[1]), to_num(ct[3])]]
    
    P_inv = matrix_inverse(P)
    K = mat_mult_mat(C, P_inv)
    return K

def print_matrix(K, name="K"):
    print(f"{name} = [{K[0][0]:>3} {K[0][1]:>3}]")
    print(f"      [{K[1][0]:>3} {K[1][1]:>3}]")
    
    
if __name__ == "__main__":
    while True:
        print("\n=== HILL CIPHER ===")
        print("1. Enkripsi")
        print("2. Dekripsi")
        print("3. Cari Kunci")
        print("4. Keluar")

        pilihan = input("Pilih menu : ")

        if pilihan == "1":
            print("\n== ENKRIPSI ==")
            plaintext = input("Masukkan plaintext : ")

            print("Masukkan kunci matriks 2x2")
            a = int(input("K[0][0] : "))
            b = int(input("K[0][1] : "))
            c = int(input("K[1][0] : "))
            d = int(input("K[1][1] : "))

            K = [[a, b], [c, d]]

            try:
                ciphertext = hill_encrypt(plaintext, K)
                print_matrix(K)
                print("Plaintext  :", prepare_text(plaintext))
                print("Ciphertext :", ciphertext)
            except ValueError as e:
                print("Error :", e)

        elif pilihan == "2":
            print("\n== DEKRIPSI ==")
            ciphertext = input("Masukkan ciphertext : ")

            print("Masukkan kunci matriks 2x2")
            a = int(input("K[0][0] : "))
            b = int(input("K[0][1] : "))
            c = int(input("K[1][0] : "))
            d = int(input("K[1][1] : "))

            K = [[a, b], [c, d]]

            try:
                plaintext = hill_decrypt(ciphertext, K)
                print_matrix(K)
                print("Ciphertext :", prepare_text(ciphertext))
                print("Plaintext  :", plaintext)
            except ValueError as e:
                print("Error :", e)

        elif pilihan == "3":
            print("\n== CARI KUNCI ==")
            plaintext = input("Masukkan plaintext : ")
            ciphertext = input("Masukkan ciphertext : ")

            try:
                K = find_key(plaintext, ciphertext)
                print("Kunci ditemukan :")
                print_matrix(K)
            except ValueError as e:
                print("Error :", e)

        elif pilihan == "4":
            print("Program selesai.")
            break

        else:
            print("Pilihan tidak valid.")