#!/bin/bash

# URL du backend Django
BASE_URL="http://127.0.0.1:${DJANGO_PORT:-8085}/api"

echo "=== Test API Securisee (etendue) ==="

# 1. Connexion admin
echo -e "\n[1] Connexion admin"
ADMIN_RESPONSE=$(curl -s -X POST "$BASE_URL/login/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@test.com",
    "password": "5!h+US5.hy9W0S"
  }'
)
echo "$ADMIN_RESPONSE" | jq .
ADMIN_TOKEN=$(echo "$ADMIN_RESPONSE" | jq -r .token)

if [ "$ADMIN_TOKEN" = "null" ] || [ -z "$ADMIN_TOKEN" ]; then
  echo "[-] Erreur : token admin non recu"
  exit 1
fi

echo "[+] Token admin recu"

# 2. Création utilisateur avec injection
echo -e "\n[2] Creation user injection"
INJECT_USER="xssinjection@test.com"
CREATE_RESP=$(curl -s -X POST "$BASE_URL/register/" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"${INJECT_USER}\",
    \"password\": \"StrongPwd123!\",
    \"firstName\": \"<script>alert('xss')</script>\",
    \"lastName\": \"Robert'); DROP TABLE users;--\"
  }"
)
echo "$CREATE_RESP" | jq .
CREATE_OK=$(echo "$CREATE_RESP" | jq -r .user_id)

# 3. Connexion avec utilisateur injecté (ou fallback)
echo -e "\n[3] Connexion utilisateur"

if [ "$CREATE_OK" = "null" ] || [ -z "$CREATE_OK" ]; then
  echo "[*] Injection bloquee. Utilisation d un utilisateur normal pour continuer."
  SAFE_USER="testuser@test.com"
  curl -s -X POST "$BASE_URL/register/" \
    -H "Content-Type: application/json" \
    -d "{
      \"email\": \"$SAFE_USER\",
      \"password\": \"StrongPwd123!\",
      \"firstName\": \"Jean\",
      \"lastName\": \"Dupont\"
    }" | jq .

  TARGET_USER="$SAFE_USER"
else
  TARGET_USER="$INJECT_USER"
fi

# Connexion avec l utilisateur cible
TOKEN=$(curl -s -X POST "$BASE_URL/login/" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"${TARGET_USER}\",
    \"password\": \"StrongPwd123!\"
  }" | jq -r .token)

if [ "$TOKEN" = "null" ] || [ -z "$TOKEN" ]; then
  echo "[-] Erreur : token utilisateur non recu"
  exit 1
fi

echo "[+] Token utilisateur recu"

# 4. Tentative d acces admin
echo -e "\n[4] Acces route admin en tant qu utilisateur"
curl -s -X GET "$BASE_URL/admin/users/" \
  -H "Authorization: Bearer $TOKEN" | jq .

# 5. Tentative suppression admin
echo -e "\n[5] Tentative suppression admin"
curl -s -X POST "$BASE_URL/admin/users/delete/1" \
  -H "Authorization: Bearer $TOKEN" | jq .

# 6. Suppression de l utilisateur par admin
echo -e "\n[6] Suppression de l utilisateur par admin"
USER_ID=$(curl -s -X GET "$BASE_URL/admin/users/" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq ".users[] | select(.email==\"$TARGET_USER\") | .id")

if [ -z "$USER_ID" ]; then
  echo "[-] Utilisateur $TARGET_USER non trouve"
else
  curl -s -X POST "$BASE_URL/admin/users/delete/$USER_ID" \
    -H "Authorization: Bearer $ADMIN_TOKEN" | jq .

  # 7. Reconnexion post-suppression
  echo -e "\n[7] Reconnexion avec utilisateur supprime"
  curl -s -X POST "$BASE_URL/login/" \
    -H "Content-Type: application/json" \
    -d "{
      \"email\": \"${TARGET_USER}\",
      \"password\": \"StrongPwd123!\"
    }" | jq .
fi

# 8. Simuler logout
echo -e "\n[8] Simulation logout"
TOKEN=""

# 9. Acces au profil sans token
echo -e "\n[9] Acces au profil sans token"
curl -s -X GET "$BASE_URL/user/me/" | jq .

echo -e "\n[✓] Tous les tests API2 termines"
