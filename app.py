import os
from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector, decimal
import jwt
import bcrypt
from datetime import datetime, timedelta
from functools import wraps
import mysql.connector.pooling

SECRET_KEY =

app = Flask(__name__)
CORS(app, supports_credentials=True, resources={
    r"/*": {
        "origins": ["http://localhost:3000"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

app.config['SECRET_KEY'] = SECRET_KEY

# Database configuration
DB_CONFIG = {

}

connection_pool = None

def init_db_pool():
    global connection_pool
    try:
        connection_pool = mysql.connector.pooling.MySQLConnectionPool(**DB_CONFIG)
        print("Connection pool created successfully")
    except Exception as e:
        print(f"Error creating connection pool: {e}")
        raise

def get_db_connection():
    try:
        if connection_pool is None:
            init_db_pool()
        return connection_pool.get_connection()
    except Exception as e:
        print(f"Error getting connection from pool: {e}")
        raise

# Add more detailed logging to the verify_token function
def verify_token():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        print("No Authorization header found")
        return None
    if not auth_header.startswith('Bearer '):
        print("Invalid Authorization header format")
        return None

    token = auth_header.split(' ')[1]
    try:
        decoded = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        print(f"Successfully decoded token for user: {decoded.get('username')}")
        return decoded
    except jwt.ExpiredSignatureError:
        print("Token has expired")
        return None
    except jwt.InvalidTokenError as e:
        print(f"Invalid token: {str(e)}")
        return None
    except Exception as e:
        print(f"Unexpected error decoding token: {str(e)}")
        return None

# def get_db_connection():
#     try:
#         connection = mysql.connector.connect(**DB_CONFIG)
#         return connection
#     except mysql.connector.Error as e:
#         print(f"Error connecting to database: {e}")
#         raise e

# Password hashing functions
def hash_password(plain_password):
    bytes = plain_password.encode('utf-8')
    salt = bcrypt.gensalt()
    hash = bcrypt.hashpw(bytes, salt)
    return hash.decode('utf-8')

def check_password(plain_password, hashed_password):
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )

# Login route
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    connection = None

    try:
        print("Attempting to get database connection...")
        connection = get_db_connection()
        print("Connection successful")

        cursor = connection.cursor(dictionary=True)
        print(f"Executing query for user: {username}")

        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        print(f"Query results: {user is not None}")

        if user and check_password(password, user['password']):
            token = jwt.encode(
                {
                    'user_id': user['id'],
                    'username': user['username'],
                    'exp': datetime.utcnow() + timedelta(days=1)
                },
                app.config['SECRET_KEY'],
                algorithm='HS256'
            )
            return jsonify({'token': token, 'message': 'Login successful'})

        return jsonify({'message': 'Invalid credentials'}), 401

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'message': 'Server error'}), 500

    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


# def verify_token():
#     auth_header = request.headers.get('Authorization')
#     if not auth_header or not auth_header.startswith('Bearer '):
#         return None
#
#     token = auth_header.split(' ')[1]
#     try:
#         return jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
#     except:
#         return None


# Add this middleware to protected routes
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token_data = verify_token()
        if not token_data:
            return jsonify({'message': 'Unauthorized'}), 401
        return f(*args, **kwargs)

    return decorated_function

# Products routes
@app.route('/api/products', methods=['GET', 'POST'])
@login_required
def handle_products():
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        if request.method == 'GET':
            cursor.execute("""
                SELECT id, product_name, cost_price, sell_price, 
                       quantity, quantity_left, created_at, user_id, average_cost_price
                FROM products 
                ORDER BY created_at DESC
            """)
            products = cursor.fetchall()

            # Convert Decimal and datetime objects for JSON serialization
            formatted_products = []
            for product in products:
                formatted_product = {}
                for key, value in product.items():
                    if isinstance(value, decimal.Decimal):
                        formatted_product[key] = float(value)
                    elif isinstance(value, datetime):
                        formatted_product[key] = value.isoformat()
                    else:
                        formatted_product[key] = value
                formatted_products.append(formatted_product)

            return jsonify(formatted_products)

        elif request.method == 'POST':
            # Your existing POST handling code stays the same
            data = request.json
            if data.get('action') == 'add':
                if isinstance(data.get('products'), list):
                    # Handle bulk product creation
                    for product_data in data['products']:
                        cursor.execute("""
                            INSERT INTO products 
                            (product_name, cost_price, quantity, quantity_left, sell_price, 
                             user_id, created_at) 
                            VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, %s)
                            """,
                                       (product_data['productName'],
                                        float(product_data['costPrice']),
                                        int(product_data['quantity']),
                                        int(product_data['quantity']),
                                        float(product_data['sellPrice']),
                                        1,  # Replace with actual user_id from token
                                        product_data.get('originalProductId'))
                                       )
                else:
                    # Handle single product creation
                    cursor.execute("""
                        INSERT INTO products 
                        (product_name, cost_price, quantity, quantity_left, sell_price, 
                         user_id, created_at) 
                        VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                        """,
                                   (data['productName'],
                                    float(data['costPrice']),
                                    int(data['quantity']),
                                    int(data['quantity']),
                                    float(data['sellPrice']),
                                    1)  # Replace with actual user_id from token
                                   )
                connection.commit()
                return jsonify({'message': 'Product(s) added successfully'})

    except Exception as e:
        print(f"Error in handle_products: {str(e)}")
        return jsonify({'message': f'Server error: {str(e)}'}), 500
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

# Statistics route
@app.route('/api/statistics', methods=['GET'])
@login_required
def get_statistics():
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT * FROM products")
        products = cursor.fetchall()

        total_quantity_sold = sum(p['quantity'] - p['quantity_left'] for p in products)
        total_amount = sum(p['sell_price'] * (p['quantity'] - p['quantity_left']) for p in products)
        total_profit = sum(
            (p['sell_price'] * (p['quantity'] - p['quantity_left'])) -
            ((p['cost_price'] / p['quantity']) * (p['quantity'] - p['quantity_left']))
            for p in products
        )

        return jsonify({
            'totalProducts': len(products),
            'totalQuantitySold': total_quantity_sold,
            'totalAmount': total_amount,
            'totalProfit': total_profit
        })

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'message': 'Server error'}), 500
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

# Update quantity route
@app.route('/api/update-quantity', methods=['POST'])
@login_required
def update_quantity():
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        data = request.json
        updates = data.get('updates', [])

        for update in updates:
            product_id = update['productId']
            quantity_added = int(update.get('quantity', 0))
            new_cost_price = update.get('costPrice')
            new_sell_price = update.get('sellPrice')
            has_price_change = update.get('hasPriceChange', False)

            # Get current product state
            cursor.execute("""
                SELECT product_name, quantity_left, cost_price, sell_price, 
                       average_cost_price, quantity, quantity_sold 
                FROM products WHERE id = %s
            """, (product_id,))
            current_product = cursor.fetchone()

            if not current_product:
                raise Exception(f"Product with ID {product_id} not found")

            # Convert None values to 0 and ensure proper decimal handling
            current_avg_cost = float(current_product['average_cost_price'] or current_product['cost_price'] or 0)
            current_quantity_left = int(current_product['quantity_left'] or 0)
            current_quantity = int(current_product['quantity'] or 0)
            current_quantity_sold = int(current_product['quantity_sold'] or 0)

            # Handle quantity addition
            if quantity_added > 0:
                # Calculate new total cost and average cost per unit
                current_total_cost = current_avg_cost * current_quantity
                new_total_cost = float(new_cost_price or current_total_cost)
                total_new_quantity = current_quantity_left + quantity_added
                new_avg_cost = new_total_cost / total_new_quantity

                # Add to price history if adding new quantity and prices changed
                if has_price_change:
                    cursor.execute("""
                        INSERT INTO product_price_history 
                        (product_id, product_name, cost_price, sell_price, average_cost_price,
                         total_profit, quantity, quantity_sold, quantity_left, new_quantity_added)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        product_id,
                        current_product['product_name'],
                        float(new_total_cost),
                        float(new_sell_price) if new_sell_price is not None else float(current_product['sell_price'] or 0),
                        new_avg_cost,
                        0,  # No profit calculation needed for additions
                        total_new_quantity,
                        current_quantity_sold,
                        current_quantity_left + quantity_added,
                        quantity_added
                    ))

                # Update product with new values
                cursor.execute("""
                    UPDATE products 
                    SET quantity_left = %s,
                        quantity = %s,
                        cost_price = %s,
                        average_cost_price = %s,
                        sell_price = CASE WHEN %s AND %s IS NOT NULL THEN %s ELSE sell_price END,
                        quantity_sold = 0
                    WHERE id = %s
                """, (
                    current_quantity_left + quantity_added,
                    total_new_quantity,
                    new_total_cost,
                    new_avg_cost,
                    has_price_change,
                    new_sell_price,
                    float(new_sell_price) if new_sell_price is not None else float(current_product['sell_price'] or 0),
                    product_id
                ))

            else:
                # This is just a quantity update or sale - only update quantities
                quantity_change = int(update.get('quantity_sold', 0))
                new_quantity_left = current_quantity_left - quantity_change

                if new_quantity_left < 0:
                    raise Exception("Not enough quantity available")

                # Update product quantities without recording in history
                cursor.execute("""
                    UPDATE products 
                    SET quantity_left = %s,
                        quantity_sold = quantity_sold + %s
                    WHERE id = %s
                """, (new_quantity_left, quantity_change, product_id))

        connection.commit()
        return jsonify({'message': 'Products updated successfully'})

    except Exception as e:
        if connection:
            connection.rollback()
        print(f"Error: {str(e)}")
        return jsonify({'message': f'Server error: {str(e)}'}), 500
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/api/update-product-quantity', methods=['POST'])
@login_required
def update_product_quantity():
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        data = request.json
        updates = data.get('updates', [])

        for update in updates:
            product_id = update['productId']
            quantity_added = update['quantity']
            new_quantity_total = update['newQuantityTotal']
            cost_price = update['costPrice']
            sell_price = update['sellPrice']
            has_price_change = update['hasPriceChange']

            # Add to price history
            cursor.execute("""
                INSERT INTO product_price_history 
                (product_id, cost_price, sell_price, quantity_added)
                VALUES (%s, %s, %s, %s)
            """, (product_id, cost_price, sell_price, quantity_added))

            # Calculate new average cost price
            cursor.execute("""
                SELECT quantity_left, average_cost_price, cost_price 
                FROM products WHERE id = %s
            """, (product_id,))
            current_product = cursor.fetchone()

            current_avg_cost = current_product['average_cost_price'] or current_product['cost_price']
            current_quantity = current_product['quantity_left']

            # Calculate weighted average cost
            new_avg_cost = (
                    (current_avg_cost * current_quantity + cost_price * quantity_added) /
                    (current_quantity + quantity_added)
            )

            # Update product
            cursor.execute("""
                UPDATE products 
                SET quantity_left = %s,
                    average_cost_price = %s,
                    sell_price = %s
                WHERE id = %s
            """, (new_quantity_total, new_avg_cost, sell_price if has_price_change else sell_price, product_id))

        connection.commit()
        return jsonify({'message': 'Products updated successfully'})

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'message': f'Server error: {str(e)}'}), 500
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


@app.route('/api/price-history/<int:product_id>', methods=['GET'])
@login_required
def get_price_history(product_id):
    connection = None
    try:
        print(f"Fetching price history for product ID {product_id}")
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT cost_price, sell_price, new_quantity_added as quantity_added, timestamp as date
            FROM product_price_history
            WHERE product_id = %s
            ORDER BY timestamp DESC
        """, (product_id,))

        history = cursor.fetchall()

        # Format decimal values
        formatted_history = []
        for record in history:
            formatted_record = {}
            for key, value in record.items():
                if isinstance(value, decimal.Decimal):
                    formatted_record[key] = float(value)
                elif isinstance(value, datetime):
                    formatted_record[key] = value.isoformat()
                else:
                    formatted_record[key] = value
            formatted_history.append(formatted_record)

        return jsonify(formatted_history)

    except Exception as e:
        print(f"Error in get_price_history: {str(e)}")
        return jsonify({'message': 'Server error', 'error': str(e)}), 500
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()



@app.route('/api/validate-token', methods=['GET'])
def validate_token():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'valid': False}), 401

    token = auth_header.split(' ')[1]
    try:
        # Verify the token
        jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return jsonify({'valid': True})
    except jwt.ExpiredSignatureError:
        return jsonify({'valid': False, 'message': 'Token expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'valid': False, 'message': 'Invalid token'}), 401

@app.route('/api/add-quantity', methods=['POST'])
@login_required
def add_quantity():
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        data = request.json
        updates = data.get('updates', [])

        for update in updates:
            product_id = update['productId']
            added_quantity = update['addedQuantity']
            new_total_quantity = update['newTotalQuantity']
            new_cost_price = update['newCostPrice']
            new_sell_price = update['newSellPrice']
            has_price_change = update['hasPriceChange']

            # If prices changed, add to price history
            if has_price_change:
                cursor.execute("""
                    INSERT INTO product_price_history 
                    (product_id, cost_price, sell_price, quantity_added, date_added)
                    VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
                """, (product_id, new_cost_price, new_sell_price, added_quantity))

            # Update product quantities and prices
            cursor.execute("""
                UPDATE products 
                SET quantity_left = %s,
                    cost_price = %s,
                    sell_price = %s
                WHERE id = %s
            """, (new_total_quantity, new_cost_price, new_sell_price, product_id))

        connection.commit()
        return jsonify({'message': 'Quantities and prices updated successfully'})

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'message': f'Server error: {str(e)}'}), 500
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


# Add this route to your app.py
# @app.route('/api/products', methods=['GET'])
# @login_required
# def get_products():
#     connection = None
#     try:
#         connection = get_db_connection()
#         cursor = connection.cursor(dictionary=True)
#
#         cursor.execute("SELECT * FROM products ORDER BY created_at DESC")
#         products = cursor.fetchall()
#
#         # Convert Decimal objects to float for JSON serialization
#         formatted_products = []
#         for product in products:
#             formatted_product = {}
#             for key, value in product.items():
#                 if isinstance(value, decimal.Decimal):
#                     formatted_product[key] = float(value)
#                 else:
#                     formatted_product[key] = value
#             formatted_products.append(formatted_product)
#
#         return jsonify(formatted_products)
#
#     except Exception as e:
#         print(f"Error fetching products: {str(e)}")
#         return jsonify({'message': 'Server error'}), 500
#     finally:
#         if connection and connection.is_connected():
#             cursor.close()
#             connection.close()


# Add or update these routes in your app.py

@app.route('/api/products/<int:product_id>', methods=['PUT', 'DELETE'])
@login_required
def manage_product(product_id):
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        if request.method == 'DELETE':
            # First check if product exists
            cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
            product = cursor.fetchone()
            if not product:
                return jsonify({'message': 'Product not found'}), 404

            # Check if product has sales history
            if product['quantity'] != product['quantity_left']:
                return jsonify({'message': 'Cannot delete product with sales history'}), 400

            # Delete product
            cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
            connection.commit()
            return jsonify({'message': 'Product deleted successfully'})

        elif request.method == 'PUT':
            data = request.json
            print("Received update data:", data)  # Debug print

            # Validate required fields
            if not all(key in data for key in ['productName', 'costPrice', 'sellPrice']):
                return jsonify({'message': 'Missing required fields'}), 400

            # First check if product exists
            cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
            product = cursor.fetchone()
            if not product:
                return jsonify({'message': 'Product not found'}), 404

            # Convert prices to float and validate
            try:
                cost_price = float(data['costPrice'])
                sell_price = float(data['sellPrice'])
                if cost_price < 0 or sell_price < 0:
                    return jsonify({'message': 'Prices cannot be negative'}), 400
            except ValueError:
                return jsonify({'message': 'Invalid price values'}), 400

            # Check if prices changed
            if (cost_price != float(product['cost_price']) or
                    sell_price != float(product['sell_price'])):
                # Add to price history first
                cursor.execute("""
                    INSERT INTO product_price_history 
                    (product_id, cost_price, sell_price, quantity_added, date_added)
                    VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
                """, (product_id, cost_price, sell_price, 0))

            # Update the product
            cursor.execute("""
                UPDATE products 
                SET product_name = %s,
                    cost_price = %s,
                    sell_price = %s,
                    average_cost_price = %s
                WHERE id = %s
            """, (
                data['productName'],
                cost_price,
                sell_price,
                cost_price,  # Update average_cost_price when cost_price changes
                product_id
            ))

            print("Update query executed")  # Debug print
            connection.commit()
            print("Changes committed")  # Debug print

            # Fetch and return updated product
            cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
            updated_product = cursor.fetchone()

            # Convert Decimal to float for JSON serialization
            updated_product = {
                k: float(v) if isinstance(v, decimal.Decimal) else v
                for k, v in updated_product.items()
            }

            return jsonify({
                'message': 'Product updated successfully',
                'product': updated_product
            })

    except mysql.connector.Error as e:
        print(f"Database error: {str(e)}")  # Debug print
        return jsonify({'message': f'Database error: {str(e)}'}), 500
    except Exception as e:
        print(f"Unexpected error: {str(e)}")  # Debug print
        return jsonify({'message': f'Server error: {str(e)}'}), 500
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("Database connection closed")  # Debug print

if __name__ == '__main__':
    init_db_pool()
    app.run(debug=True)