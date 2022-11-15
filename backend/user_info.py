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
		roleName = data_user[0]

		if bcrypt.checkpw(password, pw) == False:
			return make_response(jsonify(deskripsi="Password Salah"), 401)

		session["username"] = username
		session["password"] = pw

		jwt_payload = {
			"roleName"	: roleName
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

@app.route('/about')
def about():
    if 'username' in session:
        return "Selamat Datang di About"
    else:
        return "Selamat Datang di Website Sencof"
@app.route('/contact')
def contact():
    if 'username' in session:
        return "Selamat Datang di Contact"
    else:
        return "Selamat Datang di Website Sencof"
@app.route('/logout')
def logout():
    session.clear()
    return "Selamat Datang di Website Sencof"

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

	roleName = str(get_jwt()["roleName"])

	if roleName != ADMIN:
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
	
	roleName = str(get_jwt()["roleName"])

	if roleName != ADMIN:
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

	roleName = str(get_jwt()["roleName"])

	if roleName != ADMIN:
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
