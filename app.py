from flask import Flask, redirect, render_template, jsonify, request
from orders import db, Order,Admin
from werkzeug.security import check_password_hash
from functools import wraps
import jwt
from datetime import datetime, timedelta

app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = "abcdefg"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///orders.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

def admin_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):

        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return jsonify({
                "error": "Authorization token is required"
            }), 401

        try:
            token = auth_header.split(" ")[1]

            payload = jwt.decode(
                token,
                app.config["JWT_SECRET_KEY"],
                algorithms=["HS256"]
            )

        except jwt.ExpiredSignatureError:
            return jsonify({
                "error": "Token has expired"
            }), 401

        except jwt.InvalidTokenError:
            return jsonify({
                "error": "Invalid token"
            }), 401

        if payload.get("role") != "admin":
            return jsonify({
                "error": "Admin permission required"
            }), 403

        return f(*args, **kwargs)

    return decorated_function

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/admin/login")
def admin_login_page():
    return render_template("admin_login.html")
@app.route("/admin/dashboard")
def admin_dashboard():
    return render_template("admin_dashboard.html")
@app.route("/cart.html")
def cart():
    return render_template("cart.html")

@app.route("/order-status")
def order_status():
    return render_template("order-status.html")

@app.route("/api/admin/orders/<int:order_id>/status", methods=["PATCH"])
@admin_required
def update_order_status(order_id):
    order = db.session.get(Order, order_id)

    if not order:
        return jsonify({
            "error": "Order not found"
        }), 404

    data = request.get_json()

    status = data.get("status")

    allowed_statuses = [
        "pending",
        "preparing",
        "completed",
        "cancelled"
    ]

    if status not in allowed_statuses:
        return jsonify({
            "error": "Invalid order status"
        }), 400

    order.status = status

    db.session.commit()

    return jsonify({
        "message": "Order status updated successfully",
        "order": {
            "id": order.id,
            "status": order.status
        }
    }), 200


@app.route("/api/admin/orders/<int:order_id>", methods=["DELETE"])
@admin_required
def delete_order(order_id):
    order = db.session.get(Order, order_id)

    if order is None:
        return jsonify({
            "error": f"No order found with ID {order_id}"
        }), 404

    db.session.delete(order)
    db.session.commit()

    return jsonify({
        "message": "Order deleted successfully"
    }), 200

@app.route("/api/orders/<int:order_id>", methods=["GET"])
def get_order(order_id):

    order = db.session.get(Order, order_id)

    if order is None:
        return jsonify({
            "error": "Order not found"
        }), 404

    return jsonify({
        "id": order.id,
        "customer": order.customer,
        "items": order.items,
        "quantity": order.quantity,
        "total_price": order.total_price,
        "created_at": order.created_at.isoformat(),
        "status": order.status
    })

@app.route("/admin/add")
def admin_add_page():
    return render_template("admin_add.html")

@app.route("/api/admin/orders", methods=["POST"])
@admin_required
def admin_create_order():
    data = request.get_json()

    customer = data.get("customer")
    items = data.get("items")
    quantity = data.get("quantity")
    total_price = data.get("total_price")

    if not customer or not items or not quantity or total_price is None:
        return jsonify({
            "error": "Missing required order information"
        }), 400

    try:
        quantity = int(quantity)
        total_price = float(total_price)
    except (ValueError, TypeError):
        return jsonify({
            "error": "Quantity and total price must be valid numbers"
        }), 400

    order = Order(
        customer=customer,
        items=items,
        quantity=quantity,
        total_price=total_price
    )

    db.session.add(order)
    db.session.commit()

    return jsonify({
        "message": "Order created successfully",
        "order": {
            "id": order.id,
            "customer": order.customer,
            "items": order.items,
            "quantity": order.quantity,
            "total_price": order.total_price,
            "status": order.status
        }
    }), 201

@app.route("/api/orders", methods=["POST"])
def create_order():
    data = request.get_json()

    customer = data.get("customer")
    items = data.get("items")
    quantity = data.get("quantity")
    total_price = data.get("total_price")

    if not customer or not items or not quantity or total_price is None:
        return jsonify({
            "error": "Missing required order information"
        }), 400

    order = Order(
        customer=customer,
        items=items,
        quantity=quantity,
        total_price=total_price
    )

    db.session.add(order)
    db.session.commit()

    return jsonify({
        "message": "Order created successfully",
        "order": {
            "id": order.id,
            "customer": order.customer,
            "items": order.items,
            "quantity": order.quantity,
            "total_price": order.total_price,
            "status": order.status
        }
    }), 201


@app.route("/api/admin/orders", methods=["GET"])
@admin_required
def get_orders():
    orders = Order.query.all()

    return jsonify([
        {
            "id": order.id,
            "customer": order.customer,
            "items": order.items,
            "quantity": order.quantity,
            "total_price": order.total_price,
            "created_at": order.created_at.isoformat(),
            "status": order.status
        }
        for order in orders
    ])

@app.route("/api/menu")
def get_menu():
    return jsonify([
        {
            "id": "bruschetta",
            "name": "Classic Bruschetta",
            "desc": "Toasted sourdough topped with vine tomatoes, fresh basil, and a drizzle of extra-virgin olive oil.",
            "price": 8.5,
            "img": "img/image1.png",
            "category": "starters"
        },
        {
            "id": "mushroom-soup",
            "name": "Cream of Mushroom Soup",
            "desc": "Rich, velvety mushroom soup with a swirl of cream and fresh thyme garnish.",
            "price": 7.0,
            "img": "img/image2.png",
            "category": "starters"
        },
        {
            "id": "shrimp-cocktail",
            "name": "Shrimp Cocktail",
            "desc": "Chilled jumbo shrimp served with house-made cocktail sauce and lemon wedges.",
            "price": 13.0,
            "img": "img/image3.png",
            "category": "starters"
        },
        {
            "id": "ribeye-steak",
            "name": "Grilled Ribeye Steak",
            "desc": "12 oz prime ribeye, seasoned and flame-grilled, served with roasted potatoes and seasonal vegetables.",
            "price": 38.0,
            "img": "img/image4.png",
            "category": "main-course"
        },
        {
            "id": "pan-seared-salmon",
            "name": "Pan-Seared Salmon",
            "desc": "Atlantic salmon fillet with lemon-dill butter sauce, served over wild rice and steamed asparagus.",
            "price": 29.0,
            "img": "img/image5.png",
            "category": "main-course"
        },
        {
            "id": "truffle-pasta",
            "name": "Truffle Pasta",
            "desc": "House-made tagliatelle tossed in a black truffle cream sauce with parmesan and fresh parsley.",
            "price": 24.0,
            "img": "img/image5.png",
            "category": "main-course"
        },
        {
            "id": "roast-chicken",
            "name": "Herb Roast Chicken",
            "desc": "Half chicken slow-roasted with rosemary, garlic, and lemon, served with mashed potatoes and gravy.",
            "price": 22.0,
            "img": "img/image6.png",
            "category": "desserts"
        },
        {
            "id": "lava-cake",
            "name": "Chocolate Lava Cake",
            "desc": "Warm dark chocolate fondant with a molten centre, served with vanilla bean ice cream.",
            "price": 11.0,
            "img": "img/image7.png",
            "category": "desserts"
        },
        {
            "id": "creme-brulee",
            "name": "Crème Brûlée",
            "desc": "Classic French custard with a crisp caramelised sugar crust, topped with fresh berries.",
            "price": 10.0,
            "img": "img/image8.png",
            "category": "desserts"
        },
        {
            "id": "cheesecake",
            "name": "New York Cheesecake",
            "desc": "Dense and creamy cheesecake on a buttery graham cracker base with a fresh strawberry compote.",
            "price": 9.5,
            "img": "img/image9.png",
            "category": "desserts"
        }
    ])

@app.route("/api/auth/admin/login", methods=["POST"])
def admin_login():
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({
            "error": "Username and password are required"
        }), 400

    admin = Admin.query.filter_by(username=username).first()

    if not admin:
        return jsonify({
            "error": "Invalid username or password"
        }), 401

    if not check_password_hash(admin.password_hash, password):
        return jsonify({
            "error": "Invalid username or password"
        }), 401

    token = jwt.encode(
    {
        "admin_id": admin.id,
        "role": admin.role,
        "exp": datetime.utcnow() + timedelta(hours=1)
    },
    app.config["JWT_SECRET_KEY"],
    algorithm="HS256"
)

    return jsonify({
    "message": "Login successful",
    "token": token
     }), 200



if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("Database tables:")
        print(db.metadata.tables.keys())

    app.run(debug=True)