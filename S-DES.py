__author__ = 'ALOUI Badre-Dine'

import numpy as np
from bitarray import bitarray


# Fonction pour encoder une chaine de caractères sur un nombre de bit précis (order)
def text_to_bits(text, order, encoding='utf-8', errors='surrogatepass'):
    bits = ''.join(format(ord(x), 'b') for x in text)
    return bits.zfill(order * ((len(bits) + 7) // order))


# Fonction pour décoder une chaines des caractères de 8 bits et retourner les caractères appropriés
def text_from_bits(bits, encoding='utf-8', errors='surrogatepass'):
    n = int(bits, 2)
    return n.to_bytes((n.bit_length() + 7) // 8, 'big').decode(encoding, errors) or '\0'


# Fonction qui calcule toutes les permutations utilisées dans l'algorithme
def permutation(key, order):
    assert (order in {"P10", "P8", "PI", "PI-1", "EP", "P4"}), "Erreur .. rassurez-vous de choisir la bonne permutation! "
    permut = ""
    list_index_P10 = [3, 5, 2, 7, 4, 10, 1, 9, 8, 6]
    list_index_P8 = [6, 3, 7, 4, 8, 5, 10, 9]
    list_index_IP = [2, 6, 3, 1, 4, 8, 5, 7]
    list_index_IP_inverse = [4, 1, 3, 5, 7, 2, 8, 6]
    list_index_EP = [4, 1, 2, 3, 2, 3, 4, 1]
    list_index_P4 = [2, 4, 3, 1]
    my_list = []

    if order == "P10":
        my_list = list_index_P10

    if order == "P8":
        my_list = list_index_P8

    if order == "PI":
        my_list = list_index_IP

    if order == "PI-1":
        my_list = list_index_IP_inverse

    if order == "EP":
        my_list = list_index_EP

    if order == "P4":
        my_list = list_index_P4

    for x in my_list:
        permut += key[x - 1]

    return permut


# Fonction pour effectuer une rotation à gauche
def left_spin(suite):
    output = ""
    for i in range(1, len(suite)):
        output += suite[i]
    output += suite[0]
    return output


# Fonctionne qui transforme un bitarray to str
def frombits(bits):
    assert (type(bits) == bitarray), "Le type d'entrée n'est pas valide "
    chars = ""
    for bl in bits:
        if bl:
            chars += "1"
        else:
            chars += "0"
    return chars


# Fonction pour transformer une chaine de caractères (binaire) en décimale
def char_to_dec(chaine):
    chaine = "".join(reversed(chaine))
    sum = 0
    for i in range(len(chaine)):
        sum += int(chaine[i]) * (2 ** i)
    return sum


# Fonction permettant de représenter une décimale sous sa forme binaire avec un nombre de bits donné
def decimal_to_binary(n, nb_bit):
    assert (n < 2 ** nb_bit), "Erreur .. Impossible de transformer en clés binaires !"
    rep = bin(n).replace("0b", "")
    while len(rep) < nb_bit:
        rep = '0' + rep
    return rep


# Préparation de la clé K1
def k1(key):
    assert(len(key) == 10), "Erreur .. rasssurez-vous que la longueur de clé est égale à 10!"
    key = permutation(key, "P10")
    length = len(key)
    left = key[:length//2]
    right = key[length//2:]
    rotate_left = left_spin(left)
    rotate_right = left_spin(right)
    rotate_final = rotate_left + rotate_right
    k1 = permutation(rotate_final, "P8")
    return k1

# Préparation de la clé K2
def k2(key):
    assert (len(key) == 10), "Erreur .. rasssurez-vous que la longueur de clé est égale à 10!"
    key = permutation(key, "P10")
    length = len(key)
    left = key[:length // 2]
    right = key[length // 2:]
    rotate_left_3 = left_spin(left_spin(left_spin(left)))
    rotate_right_3 = left_spin(left_spin(left_spin(right)))
    rotate_final = rotate_left_3 + rotate_right_3
    k2 = permutation(rotate_final, "P8")
    return k2


# K doit être dans un premier temps = K1(key) et dans un second temps = k2(key)
def F(input4bit, k):
    assert (len(input4bit) == 4 and len(k) == 8), "Erreur .. Veuillez vérifier la longueur des clés "
    S0 = [[1, 0, 3, 2], [3, 2, 1, 0], [0, 2, 1, 3], [3, 1, 3, 2]]
    S1 = [[0, 1, 2, 3], [2, 0, 1, 3], [3, 0, 1, 0], [2, 1, 0, 3]]
    EP = permutation(input4bit, "EP")

    EPbit = bitarray(EP)
    k = bitarray(k)

    # "ou-exclusif" entre EP et k1
    res_xor_bit = EPbit ^ k
    res_xor = frombits(res_xor_bit)
    input_S0 = res_xor[:len(res_xor)//2]
    input_S1 = res_xor[len(res_xor)//2:]

    row_S0 = input_S0[0]+input_S0[3]
    colon_S0 = input_S0[1]+input_S0[2]
    row_S1 = input_S1[0]+input_S1[3]
    colon_S1 = input_S1[1]+input_S1[2]

    # From string to decimal
    row_S0 = char_to_dec(row_S0)
    colon_S0 = char_to_dec(colon_S0)
    row_S1 = char_to_dec(row_S1)
    colon_S1 = char_to_dec(colon_S1)

    # On cherche les variables dans les matrices
    val1 = S0[row_S0][colon_S0]
    val2 = S1[row_S1][colon_S1]

    # Val to str_binanry pour concatener à la fin
    val1_bin = decimal_to_binary(val1, 2)
    val2_bin = decimal_to_binary(val2, 2)

    val_bin = val1_bin + val2_bin
    val = permutation(val_bin, "P4")
    return val


# XOR entre la sortie de F et les 4 bits qui restent
def fk(word, key):
    # On divise la chaine de 8 bits en deux chaines de 4 bits
    left_str = word[:4]
    right_str = word[4:]
    # La chaine de bit de droite est passée à la fonction F
    right_str = F(right_str, key)
    # On transforme les deux chaines de caractères en vrai tableau de bit (bitarray)
    left_bit = bitarray(left_str)
    right_bit = bitarray(right_str)
    # On calcule le 'ou exclusif' entre la chaine de gauche et la chaine de droit produite par F
    new_left_bit = left_bit ^ right_bit
    # On transforme le bitarray résultant en chaine de caractères
    new_left_str = frombits(new_left_bit)
    return new_left_str


# Fonction principale de cryptage et decryptage : S-DES
def SDES(to_cypher, key, action):

    global fk_left2, fk_left

    # Le 'cypher' subit une permutation de type PI
    IP_4bits = permutation(to_cypher, "PI")
    length = len(IP_4bits)

    # Calcul de K1 et K2 à partir la clé
    k_one = k1(key)
    k_two = k2(key)

    # Partie qui gère l'encryptage
    if action == "encrypt":
        # Calcul de fk avec K1
        fk_left = fk(IP_4bits, k_one)
        # Calcul de fk avec K2 tout en inverssant la partie droite avec la parties gauche (c'est bien le rôle joué par SW)
        fk_left2 = fk(IP_4bits[length // 2:] + fk_left, k_two)

    # Partie qui gère le décryptage : même structure que le cryptage mais on inversse les rôles de K1 et K2
    if action == "decrypt":
        # Calcul de fk avec K2
        fk_left = fk(IP_4bits, k_two)
        # Calcul de fk avec K1 tout en inverssant la partie droite avec la parties gauche (Rôle joué par SW)
        fk_left2 = fk(IP_4bits[length // 2:] + fk_left, k_one)

    # Calcul de IP-1 et le résultat est à clef chiffrée/déchiffré
    result = permutation(fk_left2 + fk_left, "PI-1")
    return result


# Fonction qui chiffre à partir d'un texte normale
def encode(text, key):
    assert len(key) == 10, 'Key length is 10!'
    encrypted_text = ""
    for x in text:
        # On transforme le texte en chaine de 0 et 1 (chaque caractère est codé sur 8bits) et en le chiffre avec S-DES
        word_bit = text_to_bits(x, 8)
        enc = SDES(word_bit, key, "encrypt")
        encrypted_text += enc
    return encrypted_text


# Fonction qui décrypte une chaine de 0 et 1
def decode(text_bit, key):
    assert is_zeros_and_ones(key) and is_zeros_and_ones(text_bit), 'Text_bit et la clé ne sont constitués que de zéros et de uns!'
    assert len(text_bit) % 8 == 0 and len(key) == 10, 'la longueur de Text_bit doit etre un multiple de 8 et la longueur de clé = 10!'
    decrypted_text = ''
    for i in range(0, len(text_bit), 8):
        # Parcours de la chaine chiffrée par un batch de 8 caractères
        word_bit = text_bit[i:i + 8]
        dec = SDES(word_bit, key, "decrypt")
        decrypted_text += dec
    return decrypted_text


# Fonction qui vérifie que la clé est composée que de 0 et de 1
def is_zeros_and_ones(key):
    res = True
    for x in key:
        if x != '0' and x != '1':
            res = False
            break
    return res


# Pour avoir la posibilité de sortir à chaque étape d'un input dans le main
def out(entree):
    if entree == "-1":
        return True
    return False


def main():
    print("\n****** Bienvenue dans l'algorithme S-DES  ******\n")

    choice = int(input("Veuillez taper '0' pour chiffrer, '1' pour déchiffrer. (Tapez toujours '-1' pour quitter):  "))

    while choice != -1:
        # Si l'utilisateur choisi l'encryptage
        if choice == 0:
            print("\n[+] Encryptage")
            text = input("Veuillez saisir votre texte : ")
            if out(text): break
            key = input("Veuillez saisir une clé -10bits- : ")
            if out(key): break
            # Si la clé comporte des caractères autres que 0 et 1 -> un warnings
            while len(key) != 10 or not is_zeros_and_ones(key):
                print("\n/!\ Attention .. Une clé est composée uniquement de zéros et de uns. La longueur de la clé doit être de 10!")
                key = input("Veuillez choisir à nouveau une clé -10bits-:  ")
            print("\nVotre clé (10 bits) est: ", key)
            print("Votre texte est " + '[' + text + ']')
            print("Son encodage sur (8 bits) est:  ", text_to_bits(text, 8))
            encrypted_text = encode(text, key)
            print("\n |-> L'encryptage de votre texte est:  ", encrypted_text)


        # Si l'utilisateur choisi le decryptage
        if choice == 1:
            print("\n[+] Decryptage")
            text_bit = input("Veuillez saisir votre texte binaire déjà crypté: ")
            if out(text_bit): break
            while len(text_bit) % 8 != 0 or not is_zeros_and_ones(text_bit):
                print("/!\ Attention .. La longueur du texte doit être multiple de 8 et composée uniquement de 0 et de 1! \n")
                text_bit = input("Veuillez saisir à nouveau votre texte binaire: ")
                if out(text_bit): break
            key = input("Veuillez saisir une clé -10bits-: ")
            if out(key): break
            while len(key) != 10 or not is_zeros_and_ones(key):
                print("/!\ Attention .. Une clé est composée uniquement de 0 et de 1. La longueur de la clé doit être de 10!\n")
                key = input("Veuillez choisir à nouveau une clé -10bits-: ")
                if out(key): break
            decrypted_text = decode(text_bit, key)
            print("\n -> Le décryptage de votre texte est: ", decrypted_text)
            print("/!\ L'algorithme S-DES a trouvé votre texte. C'est: " + '[' + text_from_bits(decrypted_text) + ']')

        choice = int(input("\nVeuillez taper '0' pour chiffrer, '1' pour déchiffrer. (Tapez toujours '-1' pour quitter): "))

    print("\nMerci à bientôt! ")


if __name__ == "__main__":
    main()
