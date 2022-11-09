from flask import Flask, request, jsonify, make_response
from flask_jwt_extended import create_access_token, get_jwt, jwt_required, JWTManager
import pymysql
import datetime
import hashlib

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

# Routing Index
@app.route('/')
@app.route('/index')
def index():
	return "Selamat Datang di Website Sencof"

@app.route("/login_user", methods=["POST"])
def login_user():
	data = request.json

	username = data["username"]
	password = data["password"]

	username = username.lower()
	password_enc = hashlib.md5(password.encode('utf-8')).hexdigest() # Convert password to md5

	# Cek kredensial didalam database
	query = " SELECT userID, password, roleID FROM user WHERE username = %s "
	values = (username, )

	mycursor = mydb.cursor()
	mycursor.execute(query, values)
	data_user = mycursor.fetchall()

	if len(data_user) == 0:
		return make_response(jsonify(deskripsi="Username tidak ditemukan"), 401)

	data_user	= data_user[0]

	db_userID = data_user[0]
	db_password = data_user[1]
	db_roleID		= data_user[2]
	
	if password_enc != db_password:
		return make_response(jsonify(deskripsi="Password salah"), 401)

	jwt_payload = {
		"userID" : db_userID,
		"roleID" : db_roleID
	}

	access_token = create_access_token(username, additional_claims=jwt_payload)

	return jsonify(access_token=access_token)

@app.route('/get_user_info', methods=['GET'])
@jwt_required()
def get_user_info():
	# Awal Query
	query = "SELECT * FROM user_info WHERE 1=1"
	values = ()

	# Mengatur Parameter
	infoID = request.args.get("infoID")
	userID = request.args.get("userID")
	fullname = request.args.get("fullname")
	phone = request.args.get("phone")
	address = request.args.get("address")
	city = request.args.get("city")
	zipcode = request.args.get("zipcode")

	if infoID:
		query += " AND infoID=%s "
		values += (infoID,)
	if userID:
		query += " AND userID LIKE %s "
		values += ("%"+userID+"%", )
	if fullname:
		query += " AND fullname=%s "
		values += (fullname,)
	if phone:
		query += " AND phone=%s "
		values += (phone,)
	if address:
		query += " AND address=%s "
		values += (address,)
	if city:
		query += " AND city LIKE %s "
		values += ("%"+city+"%", )
	if zipcode:
		query += " AND zipcode=%s "
		values += (zipcode,)

	mycursor = mydb.cursor()
	mycursor.execute(query, values)
	row_headers = [x[0] for x in mycursor.description]
	data = mycursor.fetchall()
	json_data = []
	for result in data:
		json_data.append(dict(zip(row_headers, result)))
	return make_response(jsonify(json_data),200)

@app.route('/insert_user_info', methods=['POST'])
@jwt_required()
def insert_user_info():
	hasil = {"status": "gagal insert data user info"}

	userID = str(get_jwt()["userID"])
	roleID 	= str(get_jwt()["roleID"])

	if roleID != "1":
		return make_response(jsonify(deskripsi="Harap gunakan akun admin"), 401)

	try:
		data = request.json

		query = "INSERT INTO user_info(infoID, userID, fullname, phone, address, city, zipcode) VALUES(%s,%s,%s,%s,%s,%s,%s)"
		values = (data["infoID"], data["userID"], data["fullname"], data["phone"], data["address"], data["city"], data["zipcode"])
		mycursor = mydb.cursor()
		mycursor.execute(query, values)
		mydb.commit()
		hasil = {"status": "berhasil insert data user info"}

	except Exception as e:
		print("Error: " + str(e))
		hasil = {
			"status": "gagal insert data user info",
			"error" : str(e)
		}

	return jsonify(hasil)

@app.route('/update_user_info', methods=['PUT'])
@jwt_required()
def update_user_info():
	hasil = {"status": "gagal update data user info"}
	
	userID = str(get_jwt()["userID"])
	roleID 	= str(get_jwt()["roleID"])

	if roleID != "1":
		return make_response(jsonify(deskripsi="Harap gunakan akun admin"), 401)
	
	try:
		data = request.json
		infoID = data["infoID"]

		query = "UPDATE user_info SET infoID = %s "
		values = (infoID, )

		if "infoID_ubah" in data:
			query += ", infoID = %s"
			values += (data["infoID_ubah"], )
		if "userID_ubah" in data:
			query += ", userID = %s"
			values += (data["userID_ubah"], )
		if "phone" in data:
			query += ", phone = %s"
			values += (data["phone"], )
		if "address" in data:
			query += ", address = %s"
			values += (data["address"], )
		if "city" in data:
			query += ", city = %s"
			values += (data["city"], )
		if "zipcode" in data:
			query += ", zipcode = %s"
			values += (data["zipcode"], )

			

		query += " WHERE infoID = %s"
		values += (infoID, )

		mycursor = mydb.cursor()
		mycursor.execute(query, values)
		mydb.commit()
		hasil = {"status": "berhasil update data user info"}

	except Exception as e:
		print("Error: " + str(e))

	return jsonify(hasil)

@app.route('/delete_user_info/<infoID>', methods=['DELETE'])
@jwt_required()
def delete_user_info(infoID):
	hasil = {"status": "gagal hapus data user info"}

	userID = str(get_jwt()["userID"])
	roleID 	= str(get_jwt()["roleID"])

	if roleID != "1":
		return make_response(jsonify(deskripsi="Harap gunakan akun admin"), 401)

	try:
		query = "DELETE FROM user_info WHERE infoID=%s"
		values = (infoID,)
		mycursor = mydb.cursor()
		mycursor.execute(query, values)
		mydb.commit()
		hasil = {"status": "berhasil hapus data user info"}

	except Exception as e:
		print("Error: " + str(e))

	return jsonify(hasil)

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5010, debug=True)
