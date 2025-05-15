import os
import django

# Initialise Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "secureBDDApp.settings")
django.setup()

from accounts.models import User
from django.db import connection

def check_users_table():
	print("[*] Verification de la table 'accounts_user'...")
	users = User.objects.all()
	if not users: 
		print("[-] Aucun utilisateur trouve en base.")

	for user in users:
		print(f"\nUtilisateur : {user.email}")
		
		# 1. Algo de hachage
		if "argon2id" in user.password:
			print("[+] Algorithme : Argon2id OK")
		else:
			print("[-] Algorithme : NON conforme (attendu: Argon2id)")
			   
    	# 2. Donnee en clair ?
		if "password" in user.password or len(user.password) < 30:
			print("[-] Mot de passe potentiellement en clair !")
		else:
			print("[+] Mot de passe non lisible (OK)")
		
	# 3. Jetons JWT en base ?
	columns = [field.name for field in User._meta.get_fields()]
	if "token" in columns:
		print("[-] Champ 'token' present dans la table User !")
	else:
		print("[+] Aucun champ 'token' stocke en base (OK)")
		
	# 4. SELECT *
	print("\n[*] Contenu brut de accounts_user :")
	with connection.cursor() as cursor:
		cursor.execute("SELECT * FROM accounts_user;")
		rows = cursor.fetchall()
		for row in rows:
			print(row)

check_users_table()
