from flask import Flask, request, jsonify, make_response
from flask_jwt_extended import create_access_token, get_jwt, jwt_required, JWTManager
import pymysql
import datetime
import bcrypt

# Membuat server Flask
app = Flask(__name__)

# Flask JWT Extended Configuration
app.config['SECRET_KEY'] 							= "INI_SECRET_KEY"
app.config['JWT_HEADER_TYPE']						= "JWT"
app.config['JWT_ACCESS_TOKEN_EXPIRES'] 				= datetime.timedelta(days=1) #1 hari token JWT expired
jwt = JWTManager(app)

# Koneksi ke database MySQL
mydb = pymysql.connect(
	host="localhost",
	user="root",
	passwd="",
	database="sencof_database"
)
# declare constants 
ADMIN = "admin"
CUSTOMER = "customer"

# Routing Index
@app.route('/')
@app.route('/home')
def home():
	return "Selamat Datang di Website Sencof"

@app.route("/login_user", methods=["POST"])
def login_user():
		username = request.json["username"]
		password = request.json["password"].encode('utf-8')
		

		# Cek kredensial didalam database
		query = " SELECT username,password FROM user WHERE username = %s "
		values = (username, )

		mycursor = mydb.cursor()
		mycursor.execute(query, values)
		data_user = mycursor.fetchone()
		mydb.commit()
		mycursor.close()
		print(data_user)
		
		if len(data_user) == 0:
			return make_response(jsonify(deskripsi="Username tidak ditemukan"), 401)

		username = data_user[0]
		pw = data_user[1].encode()

		if bcrypt.checkpw(password, pw) == False:
			return make_response(jsonify(deskripsi="Password Salah"), 401)

		session["username"] = username
		session["password"] = pw

		jwt_payload = {
			"username"	: username
	}
		access_token = create_access_token(username, additional_claims=jwt_payload)
		return jsonify(access_token=access_token)

@app.route("/register", methods=["POST"])
def register():
	hasil = {"status": "gagal insert registrasi akun"}

	try:
		username = request.json["username"]
		password = request.json["password"].encode('utf-8')
		hash_password = bcrypt.hashpw(password, bcrypt.gensalt())
		roleName = CUSTOMER

		# Cek kredensial didalam database
		mycursor = mydb.cursor()
		mycursor.execute("INSERT INTO user (username,password,roleName) VALUES (%s,%s,%s)" , (username,hash_password,CUSTOMER))
		mydb.commit()
		hasil = {"status": "berhasil insert registrasi akun"}
	except Exception as e:
		print("Error: " + str(e))
		hasil = {
			"status": "gagal insert registrasi akun",
			"error" : str(e)
		}

	return jsonify(hasil)

@app.route('/get_category_coffee', methods=['GET'])
@jwt_required()
def get_category_coffee():
	# Awal Query
	query = "SELECT * FROM category_coffee WHERE 1=1"
	values = ()

	# Mengatur Parameter
	CategoryID = request.args.get("CategoryID")
	nama_category = request.args.get("nama_category")
	deskripsi_category = request.args.get("deskripsi_category")

	if CategoryID:
		query += " AND CategoryID=%s "
		values += (CategoryID,)
	if nama_category:
		query += " AND nama_category LIKE %s "
		values += ("%"+nama_category+"%", )
	if deskripsi_category:
		query += " AND deskripsi_category=%s "
		values += (deskripsi_category,)

	mycursor = mydb.cursor()
	mycursor.execute(query, values)
	row_headers = [x[0] for x in mycursor.description]
	data = mycursor.fetchall()
	json_data = []
	for result in data:
		json_data.append(dict(zip(row_headers, result)))
	return make_response(jsonify(json_data),200)

@app.route('/insert_category_coffee', methods=['POST'])
@jwt_required()
def insert_category_coffee():
	hasil = {"status": "gagal insert data category coffee"}

	user_id = str(get_jwt()["user_id"])
	roleID 	= str(get_jwt()["roleID"])

	if roleID != "1":
		return make_response(jsonify(deskripsi="Harap gunakan akun admin"), 401)

	try:
		data = request.json

		query = "INSERT INTO category_coffee(CategoryID, nama_category, deskripsi_category) VALUES(%s,%s,%s)"
		values = (data["CategoryID"], data["nama_category"], data["deskripsi_category"])
		mycursor = mydb.cursor()
		mycursor.execute(query, values)
		mydb.commit()
		hasil = {"status": "berhasil insert data category coffee"}

	except Exception as e:
		print("Error: " + str(e))
		hasil = {
			"status": "gagal insert data category coffee",
			"error" : str(e)
		}

	return jsonify(hasil)

@app.route('/update_category_coffee', methods=['PUT'])
@jwt_required()
def update_category_coffee():
	hasil = {"status": "gagal update data category coffee"}
	
	user_id = str(get_jwt()["user_id"])
	roleID 	= str(get_jwt()["roleID"])

	if roleID != "1":
		return make_response(jsonify(deskripsi="Harap gunakan akun admin"), 401)
	
	try:
		data = request.json
		CategoryID = data["CategoryID"]

		query = "UPDATE category_coffee SET CategoryID = %s "
		values = (CategoryID, )

		if "CategoryID_ubah" in data:
			query += ", CategoryID = %s"
			values += (data["CategoryID_ubah"], )
		if "nama_category" in data:
			query += ", nama_category = %s"
			values += (data["nama_category"], )
		if "deskripsi_category" in data:
			query += ", deskripsi_category = %s"
			values += (data["deskripsi_category"], )
			

		query += " WHERE CategoryID = %s"
		values += (CategoryID, )

		mycursor = mydb.cursor()
		mycursor.execute(query, values)
		mydb.commit()
		hasil = {"status": "berhasil update data category coffee"}

	except Exception as e:
		print("Error: " + str(e))

	return jsonify(hasil)

@app.route('/delete_category_coffee/<CategoryID>', methods=['DELETE'])
@jwt_required()
def delete_category_coffee(CategoryID):
	hasil = {"status": "gagal hapus data category coffee"}

	user_id = str(get_jwt()["user_id"])
	roleID 	= str(get_jwt()["roleID"])

	if roleID != "1":
		return make_response(jsonify(deskripsi="Harap gunakan akun admin"), 401)

	try:
		query = "DELETE FROM category_coffee WHERE CategoryID=%s"
		values = (CategoryID,)
		mycursor = mydb.cursor()
		mycursor.execute(query, values)
		mydb.commit()
		hasil = {"status": "berhasil hapus data category coffee"}

	except Exception as e:
		print("Error: " + str(e))

	return jsonify(hasil)

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5010, debug=True)
