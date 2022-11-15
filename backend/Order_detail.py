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

@app.route('/get_order_detail', methods=['GET'])
@jwt_required()
def get_order_detail():
	# Awal Query
	query = "SELECT * FROM order_detail WHERE 1=1"
	values = ()

	# Mengatur Parameter
	id_order_detail = request.args.get("id_order_detail")
	orderID = request.args.get("orderID")
	id_coffee = request.args.get("id_coffee")
	jumlah = request.args.get("jumlah")

	if id_order_detail:
		query += " AND id_order_detail=%s "
		values += (id_order_detail,)
	if orderID:
		query += " AND orderID LIKE %s "
		values += ("%"+orderID+"%", )
	if id_coffee:
		query += " AND id_coffee=%s "
		values += (id_coffee,)
	if jumlah:
		query += " AND jumlah=%s "
		values += (jumlah,)

	mycursor = mydb.cursor()
	mycursor.execute(query, values)
	row_headers = [x[0] for x in mycursor.description]
	data = mycursor.fetchall()
	json_data = []
	for result in data:
		json_data.append(dict(zip(row_headers, result)))
	return make_response(jsonify(json_data),200)

@app.route('/insert_order_detail', methods=['POST'])
@jwt_required()
def insert_order_detail():
	hasil = {"status": "gagal insert data order detail"}

	roleName = str(get_jwt()["roleName"])

	if roleName != ADMIN:
		return make_response(jsonify(deskripsi="Harap gunakan akun admin"), 401)

	try:
		data = request.json

		query = "INSERT INTO order_detail(id_order_detail, orderID, id_coffee, jumlah) VALUES(%s,%s,%s,%s)"
		values = (data["id_order_detail"], data["orderID"], data["id_coffee"], data["jumlah"])
		mycursor = mydb.cursor()
		mycursor.execute(query, values)
		mydb.commit()
		hasil = {"status": "berhasil insert data order detail"}

	except Exception as e:
		print("Error: " + str(e))
		hasil = {
			"status": "gagal insert data order detail",
			"error" : str(e)
		}

	return jsonify(hasil)

@app.route('/update_order_detail', methods=['PUT'])
@jwt_required()
def update_order_detail():
	hasil = {"status": "gagal update data order detail"}
	
	roleName = str(get_jwt()["roleName"])

	if roleName != ADMIN:
		return make_response(jsonify(deskripsi="Harap gunakan akun admin"), 401)
	
	try:
		data = request.json
		id_order_detail = data["id_order_detail"]

		query = "UPDATE order_detail SET id_order_detail = %s "
		values = (id_order_detail, )

		if "id_order_detail_ubah" in data:
			query += ", id_order_detail = %s"
			values += (data["id_order_detail_ubah"], )
		if "orderID_ubah" in data:
			query += ", orderID = %s"
			values += (data["orderID_ubah"], )
		if "id_coffee" in data:
			query += ", id_coffee = %s"
			values += (data["id_coffee"], )
		if "jumlah" in data:
			query += ", jumlah = %s"
			values += (data["jumlah"], )
        
			

		query += " WHERE id_order_detail = %s"
		values += (id_order_detail, )

		mycursor = mydb.cursor()
		mycursor.execute(query, values)
		mydb.commit()
		hasil = {"status": "berhasil update data order detail"}

	except Exception as e:
		print("Error: " + str(e))

	return jsonify(hasil)

@app.route('/delete_order_detail/<id_order_detail>', methods=['DELETE'])
@jwt_required()
def delete_order_detail(id_order_detail):
	hasil = {"status": "gagal hapus data order detail"}

	roleName = str(get_jwt()["roleName"])

	if roleName != ADMIN:
		return make_response(jsonify(deskripsi="Harap gunakan akun admin"), 401)

	try:
		query = "DELETE FROM order_detail WHERE id_order_detail=%s"
		values = (id_order_detail,)
		mycursor = mydb.cursor()
		mycursor.execute(query, values)
		mydb.commit()
		hasil = {"status": "berhasil hapus data order detail"}

	except Exception as e:
		print("Error: " + str(e))

	return jsonify(hasil)

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5010, debug=True)
