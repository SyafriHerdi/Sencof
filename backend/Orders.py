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

@app.route('/get_order', methods=['GET'])
@jwt_required()
def get_order():
	# Awal Query
	query = "SELECT * FROM orders WHERE 1=1"
	values = ()

	# Mengatur Parameter
	orderID = request.args.get("orderID")
	UserID = request.args.get("UserID")
	statusID = request.args.get("statusID")
	total_harga = request.args.get("total_harga")
	waktu_order = request.args.get("waktu_order")

	if orderID:
		query += " AND orderID=%s "
		values += (orderID,)
	if UserID:
		query += " AND UserID=%s "
		values += (UserID,)
	if statusID:
		query += " AND statusID=%s "
		values += (statusID,)
	if total_harga:
		query += " AND total_harga LIKE %s "
		values += ("%"+total_harga+"%", )
	if waktu_order:
		query += " AND waktu_order=%s "
		values += (waktu_order,)

	mycursor = mydb.cursor()
	mycursor.execute(query, values)
	row_headers = [x[0] for x in mycursor.description]
	data = mycursor.fetchall()
	json_data = []
	for result in data:
		json_data.append(dict(zip(row_headers, result)))
	return make_response(jsonify(json_data),200)

@app.route('/insert_orders', methods=['POST'])
@jwt_required()
def insert_orders():
	hasil = {"status": "gagal insert data orders"}

	userID = str(get_jwt()["userID"])
	roleID 	= str(get_jwt()["roleID"])

	if roleID != "1":
		return make_response(jsonify(deskripsi="Harap gunakan akun admin"), 401)

	try:
		data = request.json

		query = "INSERT INTO orders(orderID, UserID, statusID, total_harga, waktu_order) VALUES(%s,%s,%s,%s,%s)"
		values = (data["orderID"], data["UserID"], data["statusID"], data["total_harga"], data["waktu_order"])
		mycursor = mydb.cursor()
		mycursor.execute(query, values)
		mydb.commit()
		hasil = {"status": "berhasil insert data orders"}

	except Exception as e:
		print("Error: " + str(e))
		hasil = {
			"status": "gagal insert data orders",
			"error" : str(e)
		}

	return jsonify(hasil)

@app.route('/update_orders', methods=['PUT'])
@jwt_required()
def update_orders():
	hasil = {"status": "gagal update data orders"}
	
	userID = str(get_jwt()["userID"])
	roleID 	= str(get_jwt()["roleID"])

	if roleID != "1":
		return make_response(jsonify(deskripsi="Harap gunakan akun admin"), 401)
	
	try:
		data = request.json
		orderID = data["orderID"]

		query = "UPDATE orders SET orderID = %s "
		values = (orderID, )

		if "orderID_ubah" in data:
			query += ", orderID = %s"
			values += (data["orderID_ubah"], )
		if "UserID" in data:
			query += ", UserID = %s"
			values += (data["UserID"], )
		if "statusID" in data:
			query += ", statusID = %s"
			values += (data["statusID"], )
		if "total_harga" in data:
			query += ", total_harga = %s"
			values += (data["total_harga"], )
		if "waktu_order" in data:
			query += ", waktu_order = %s"
			values += (data["waktu_order"], )		

		query += " WHERE orderID = %s"
		values += (orderID, )

		mycursor = mydb.cursor()
		mycursor.execute(query, values)
		mydb.commit()
		hasil = {"status": "berhasil update data orders"}

	except Exception as e:
		print("Error: " + str(e))

	return jsonify(hasil)

@app.route('/delete_orders/<orderID>', methods=['DELETE'])
@jwt_required()
def delete_orders(orderID):
	hasil = {"status": "gagal hapus data orders"}

	userID = str(get_jwt()["userID"])
	roleID 	= str(get_jwt()["roleID"])

	if roleID != "1":
		return make_response(jsonify(deskripsi="Harap gunakan akun admin"), 401)

	try:
		query = "DELETE FROM orders WHERE orderID=%s"
		values = (orderID,)
		mycursor = mydb.cursor()
		mycursor.execute(query, values)
		mydb.commit()
		hasil = {"status": "berhasil hapus data orders"}

	except Exception as e:
		print("Error: " + str(e))

	return jsonify(hasil)

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5010, debug=True)
