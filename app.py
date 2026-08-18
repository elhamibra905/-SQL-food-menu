from flask import Flask, redirect, render_template, jsonify, request
from orders import db, Order

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///orders.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/cart.html")
def cart():
    return render_template("cart.html")

@app.route("/admin/orders")
def admin_orders():
    orders = Order.query.all()
    return render_template("admin_orders.html", orders=orders)

@app.route("/admin/orders/<int:order_id>/cancel", methods=["POST"])
def cancel_order(order_id):
    order = Order.query.get_or_404(order_id)

    order.status = "cancelled"

    db.session.commit()

    return redirect("/admin/orders")

@app.route("/admin/orders/<int:order_id>/delete", methods=["POST"])
def delete_order(order_id):
    order = Order.query.get_or_404(order_id)

    db.session.delete(order)
    db.session.commit()

    return redirect("/admin/orders")

@app.route("/admin/add", methods=["GET", "POST"])
def admin_add():
    if request.method == "POST":
        customer = request.form.get("customer")
        items = request.form.get("items")
        quantity = request.form.get("quantity")
        total_price = request.form.get("total_price")

        if not customer or not items or not quantity or not total_price:
            return "All fields are required", 400

        order = Order(
            customer=customer,
            items=items,
            quantity=int(quantity),
            total_price=float(total_price)
        )

        db.session.add(order)
        db.session.commit()

        return redirect("/admin/orders")

    return render_template("admin_add.html")

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

@app.route("/api/orders", methods=["GET"])
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

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("Database tables:")
        print(db.metadata.tables.keys())

    app.run(debug=True)