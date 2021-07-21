from flask import Flask, render_template, request, flash, redirect, session
from werkzeug.utils import secure_filename
import os
from uuid import uuid4
import csv
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['SQLALCHEMY_DATABASE_URI']
app.config['UPLOAD_FOLDER'] = os.environ['UPLOAD_FOLDER']
db = SQLAlchemy(app)
app.secret_key = 'AVVCDF654#@'
ALLOWED_EXTENSIONS = {'txt'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def parse_file_and_insert_db(file_path, session_id):
    fields = ['Comprador', 'Descrição', 'Preço Unitário', 'Quantidade', 'Endereço', 'Fornecedor']
    with open(file_path, newline='\n') as csvfile:
        reader = csv.DictReader(csvfile, fieldnames=fields, dialect='excel-tab')
        for row in reader:
            if row['Comprador'] == 'Comprador':
                continue
            buyer = Buyer.query.filter_by(name=row['Comprador']).first()
            if buyer is None:
                buyer = Buyer(name=row['Comprador'])
                db.session.add(buyer)
            product = Product.query.filter_by(description=row['Descrição']).first()
            if product is None:
                product = Product(description=row['Descrição'], price=row['Preço Unitário'])
                db.session.add(product)
            supplier = Supplier.query.filter_by(name=row['Fornecedor']).first()
            if supplier is None:
                supplier = Supplier(name=row['Fornecedor'], address=row['Endereço'])
                db.session.add(supplier)
            db.session.commit()
            sale = Sale(
                session_id=session_id,
                buyer_id=buyer.id,
                supplier_id=supplier.id,
                product_id=product.id,
                quantity=row['Quantidade']
            )
            db.session.add(sale)
            db.session.commit()


def query_db(session_id):
    results = db.engine.execute("SELECT buyer.name, product.description, product.price,"
                                "quantity, supplier.address, supplier.name FROM "
                                "(SELECT session_id,buyer_id,supplier_id,product_id,"
                                "quantity FROM sale WHERE session_id='{}') AS a " 
                                "LEFT JOIN buyer ON buyer.id = a.buyer_id "
                                "LEFT JOIN product ON product.id = a.product_id "
                                "LEFT JOIN supplier ON supplier.id = a.supplier_id ".format(session_id))
    r_dict = []
    for r in results:
        r_dict.append(
            {
                'buyer_name': r[0],
                'description': r[1],
                'price': str(r[2]).replace('.',','),
                'quantity': r[3],
                'address': r[4],
                'supplier_name': r[5]
            }
        )

    results = db.engine.execute("SELECT SUM(product.price * a.quantity) FROM "
                              "(SELECT quantity, product_id FROM sale WHERE session_id='{}') AS a "
                              "LEFT JOIN product ON product.id = a.product_id".format(session_id))
    total = 0
    for r in results:
        total = str(r[0]).replace('.', ',')

    return r_dict, total


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
        return render_template("home.html")
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Sem arquivo!')
            return redirect(request.url)
        file = request.files['file']
        if file and allowed_file(file.filename):
            session['id'] = uuid4()
            filename = secure_filename(file.filename)
            fname_split = filename.split('.')
            fname_id = fname_split[0] + '-' + str(session['id']) + '.' + fname_split[1]
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], fname_id)
            file.save(save_path)
            parse_file_and_insert_db(save_path, str(session['id']))
            sales, total = query_db(str(session['id']))
            return render_template('file_data.html', data={'filename': fname_id, 'sales': sales, 'total': total})
        else:
            flash('Extensão de arquivo inválida!')
            return redirect(request.url)


class Buyer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True, nullable=False)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(300), unique=True, nullable=False)
    price = db.Column(db.Float, unique=False, nullable=False)


class Supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300), unique=True, nullable=False)
    address = db.Column(db.String(300), unique=False, nullable=False)


class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(36), unique=False, nullable=False)
    buyer_id = db.Column(db.Integer, db.ForeignKey('buyer.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)


if __name__ == '__main__':
    app.run()
