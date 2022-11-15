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

@app.route('/get_product', methods=['GET'])
@jwt_required()
def get_product():
	# Awal Query
	query = "SELECT * FROM product WHERE 1=1"
	values = ()

	# Mengatur Parameter
	id_coffee = request.args.get("id_coffee")
	CategoryID = request.args.get("CategoryID")
	nama_coffee = request.args.get("nama_coffee")
	deskripsi_coffee = request.args.get("deskripsi_coffee")
	stock = request.args.get("stock")
	harga_per_kg = request.args.get("harga_per_kg")
	file_gambar_coffee = request.args.get("file_gambar_coffee")

	if id_coffee:
		query += " AND id_coffee=%s "
		values += (id_coffee,)
	if CategoryID:
		query += " AND CategoryID=%s "
		values += (CategoryID,)
	if nama_coffee:
		query += " AND nama_coffee LIKE %s "
		values += ("%"+nama_coffee+"%", )
	if deskripsi_coffee:
		query += " AND deskripsi_coffee=%s "
		values += (deskripsi_coffee,)
	if stock:
		query += " AND stock=%s "
		values += (stock,)
	if harga_per_kg:
		query += " AND harga_per_kg=%s "
		values += (harga_per_kg,)
	if file_gambar_coffee:
		query += " AND file_gambar_coffee=%s "
		values += (file_gambar_coffee,)

	mycursor = mydb.cursor()
	mycursor.execute(query, values)
	row_headers = [x[0] for x in mycursor.description]
	data = mycursor.fetchall()
	json_data = []
	for result in data:
		json_data.append(dict(zip(row_headers, result)))
	return make_response(jsonify(json_data),200)

@app.route('/insert_product', methods=['POST'])
@jwt_required()
def insert_product():
	hasil = {"status": "gagal insert data coffee been"}

	roleName = str(get_jwt()["roleName"])

	if roleName != ADMIN:
		return make_response(jsonify(deskripsi="Harap gunakan akun admin"), 401)

	try:
		data = request.json

		query = "INSERT INTO product(id_coffee, CategoryID, nama_coffee, deskripsi_coffee, stock, harga_per_kg, file_gambar_coffee) VALUES(%s,%s,%s,%s,%s,%s,%s)"
		values = (data["id_coffee"], data["CategoryID"], data["nama_coffee"], 
        data["deskripsi_coffee"],data["stock"], data["harga_per_kg"], data["file_gambar_coffee"])
		mycursor = mydb.cursor()
		mycursor.execute(query, values)
		mydb.commit()
		hasil = {"status": "berhasil insert data coffee been"}

	except Exception as e:
		print("Error: " + str(e))
		hasil = {
			"status": "gagal insert data coffee been",
			"error" : str(e)
		}

	return jsonify(hasil)

@app.route('/update_product', methods=['PUT'])
@jwt_required()
def update_product():
	hasil = {"status": "gagal update data coffee been"}
	
	roleName = str(get_jwt()["roleName"])

	if roleName != ADMIN:
		return make_response(jsonify(deskripsi="Harap gunakan akun admin"), 401)
	
	try:
		data = request.json
		id_coffee = data["id_coffee"]

		query = "UPDATE product SET id_coffee = %s "
		values = (id_coffee, )

		if "id_coffee_ubah" in data:
			query += ", id_coffee = %s"
			values += (data["id_coffee_ubah"], )
		if "CategoryID_ubah" in data:
			query += ", CategoryID = %s"
			values += (data["CategoryID_ubah"], )
		if "nama_coffee" in data:
			query += ", nama_coffee = %s"
			values += (data["nama_coffee"], )
		if "deskripsi_coffee" in data:
			query += ", deskripsi_coffee = %s"
			values += (data["deskripsi_coffee"], )
		if "stock" in data:
			query += ", stock = %s"
			values += (data["stock"], )
		if "harga_per_kg" in data:
			query += ", harga_per_kg = %s"
			values += (data["harga_per_kg"], )
		if "file_gambar_coffee" in data:
			query += ", file_gambar_coffee = %s"
			values += (data["file_gambar_coffee"], )	

		query += " WHERE id_coffee = %s"
		values += (id_coffee, )

		mycursor = mydb.cursor()
		mycursor.execute(query, values)
		mydb.commit()
		hasil = {"status": "berhasil update data coffee been"}

	except Exception as e:
		print("Error: " + str(e))

	return jsonify(hasil)

@app.route('/delete_product/<id_coffee>', methods=['DELETE'])
@jwt_required()
def delete_product(id_coffee_been):
	hasil = {"status": "gagal hapus data coffee been"}

	roleName = str(get_jwt()["roleName"])

	if roleName != ADMIN:
		return make_response(jsonify(deskripsi="Harap gunakan akun admin"), 401)

	try:
		query = "DELETE FROM product WHERE id_coffee=%s"
		values = (id_coffee,)
		mycursor = mydb.cursor()
		mycursor.execute(query, values)
		mydb.commit()
		hasil = {"status": "berhasil hapus data coffee been"}

	except Exception as e:
		print("Error: " + str(e))

	return jsonify(hasil)

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5010, debug=True)
