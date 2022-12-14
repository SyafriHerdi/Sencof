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

	roleName = str(get_jwt()["roleName"])

	if roleName != ADMIN:
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
	
	roleName = str(get_jwt()["roleName"])

	if roleName != ADMIN:
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

	roleName = str(get_jwt()["roleName"])

	if roleName != ADMIN:
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
