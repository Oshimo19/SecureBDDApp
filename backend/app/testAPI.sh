#!/bin/bash

# URL du backend Django
BASE_URL="http://127.0.0.1:${DJANGO_PORT:-8085}/api"

echo "=== Test API Sécurisée ==="

# Vérification que le serveur est en ligne
echo -n "[*] Vérification du serveur Django à $BASE_URL ... "
if ! curl -s --head "$BASE_URL/home/" | grep "200 OK" > /dev/null; then
    echo "ÉCHEC"
    echo "[-] Le serveur Django n'est pas accessible sur $BASE_URL"
    exit 1
fi
echo "OK"

# 1. Inscription
echo -e "\n[1] Inscription de alice@example.com"
REGISTER_RESPONSE=$(curl -s -X POST "$BASE_URL/register/" \
    -H "Content-Type: application/json" \
    -d '{
    "email": "alice@example.com",
    "password": "StrongPwd123!",
    "firstName": "Alice",
    "lastName": "Liddell"
}')
echo "$REGISTER_RESPONSE" | jq .

# Vérification si déjà inscrit
if echo "$REGISTER_RESPONSE" | grep -q "Email déjà utilisé"; then
    echo "[!] Utilisateur déjà inscrit, on continue"
fi

# 2. Connexion avec bon mot de passe
echo -e "\n[2] Connexion de alice@example.com"
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/login/" \
    -H "Content-Type: application/json" \
    -d '{
    "email": "alice@example.com",
    "password": "StrongPwd123!"
}')
echo "$LOGIN_RESPONSE" | jq .

TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r .token)

if [ -z "$TOKEN" ] || [ "$TOKEN" = "null" ]; then
    echo "[-] Erreur : token non reçu"
    exit 1
fi
echo "[+] Token JWT obtenu"

# 3. Accès au profil utilisateur
echo -e "\n[3] Accès au profil (/user/me/)"
curl -s -X GET "$BASE_URL/user/me/" \
    -H "Authorization: Bearer $TOKEN" | jq .

# 4. Accès refusé à la route admin en tant qu'utilisateur
echo -e "\n[4] Accès route admin (interdit)"
curl -s -X GET "$BASE_URL/admin/users/" \
    -H "Authorization: Bearer $TOKEN" | jq .

# 5. Connexion admin
echo -e "\n[5] Connexion admin"
ADMIN_RESPONSE=$(curl -s -X POST "$BASE_URL/login/" \
    -H "Content-Type: application/json" \
    -d '{
    "email": "admin@test.com",
    "password": "5!h+US5.hy9W0S"
}')
echo "$ADMIN_RESPONSE" | jq .

ADMIN_TOKEN=$(echo "$ADMIN_RESPONSE" | jq -r .token)

if [ -z "$ADMIN_TOKEN" ] || [ "$ADMIN_TOKEN" = "null" ]; then
    echo "[-] Erreur : token admin non reçu"
    exit 1
fi
echo "[+] Token admin reçu"

# 6. Accès autorisé route admin
echo -e "\n[6] Accès admin OK"
curl -s -X GET "$BASE_URL/admin/users/" \
    -H "Authorization: Bearer $ADMIN_TOKEN" | jq .

# 7. Route inconnue
echo -e "\n[7] Route inconnue (/route/inexistante)"
curl -s -X GET "$BASE_URL/route/inexistante" | jq .

# 8. Bruteforce (6 tentatives échouées)
echo -e "\n[8] Test bruteforce (email: alice@example.com)"
for i in {1..6}; do
    echo "Tentative $i (mauvais mot de passe)"
    curl -s -X POST "$BASE_URL/login/" \
        -H "Content-Type: application/json" \
        -d '{
        "email": "alice@example.com",
        "password": "wrongPassword"
    }' | jq .
done

echo -e "\n[✓] Tous les tests CURL terminés"
