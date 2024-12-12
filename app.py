from flask import Flask, request, jsonify, session
from flask_cors import CORS
from datetime import datetime
import os

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app, supports_credentials=True)
app.config['DEBUG'] = True
app.config['SESSION_TYPE'] = 'filesystem'


# Product model
class Product:
    def __init__(self, product_name, cost_price, quantity, sell_price):
        self.product_name = product_name
        self.cost_price = float(cost_price)
        self.quantity = int(quantity)
        self.sell_price = float(sell_price)
        self.quantity_left = int(quantity)

    def to_dict(self):
        return {
            'productName': self.product_name,
            'costPrice': self.cost_price,
            'quantity': self.quantity,
            'sellPrice': self.sell_price,
            'quantityLeft': self.quantity_left
        }

    @staticmethod
    def from_dict(data):
        product = Product(
            data['productName'],
            data['costPrice'],
            data['quantity'],
            data['sellPrice']
        )
        if 'quantityLeft' in data:
            product.quantity_left = data['quantityLeft']
        return product


# Initialize session
def init_session():
    if 'products' not in session:
        session['products'] = []


# Route handlers
@app.route('/api/products', methods=['GET', 'POST'])
def handle_products():
    init_session()

    if request.method == 'GET':
        return jsonify(session['products'])

    if request.method == 'POST':
        data = request.json
        if data.get('action') == 'add':
            product = Product.from_dict(data)
            session['products'].append(product.to_dict())
            session.modified = True
            return jsonify({'message': 'Product added successfully'})

        elif data.get('action') == 'edit':
            index = int(data['index'])
            product = Product.from_dict(data)
            product.quantity_left = session['products'][index]['quantityLeft']
            session['products'][index] = product.to_dict()
            session.modified = True
            return jsonify({'message': 'Product updated successfully'})

        elif data.get('action') == 'delete':
            index = int(data['index'])
            session['products'].pop(index)
            session.modified = True
            return jsonify({'message': 'Product deleted successfully'})


@app.route('/api/update-quantity', methods=['POST'])
def update_quantity():
    init_session()
    data = request.json
    changes_made = False

    for update in data['updates']:
        index = update['index']
        new_quantity = int(update['quantityLeft'])

        if new_quantity <= session['products'][index]['quantity']:
            if session['products'][index]['quantityLeft'] != new_quantity:
                session['products'][index]['quantityLeft'] = new_quantity
                changes_made = True

    if changes_made:
        session['last_submit_time'] = datetime.now().isoformat()
        session.modified = True
        return jsonify({'message': 'Quantities updated successfully'})

    return jsonify({'message': 'No changes made'})


@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    init_session()
    products = session['products']

    total_profit = 0
    total_quantity_sold = 0
    total_amount = 0

    for product in products:
        quantity_sold = product['quantity'] - product['quantityLeft']
        cost_price_each = product['costPrice'] / product['quantity']
        profit = (product['sellPrice'] * quantity_sold) - (cost_price_each * quantity_sold)

        total_profit += profit
        total_quantity_sold += quantity_sold
        total_amount += product['sellPrice'] * quantity_sold

    return jsonify({
        'totalProducts': len(products),
        'totalQuantitySold': total_quantity_sold,
        'totalAmount': total_amount,
        'totalProfit': total_profit
    })


@app.route('/')
def home():
    return 'Server is running!'

if __name__ == '__main__':
    app.run(debug=True)