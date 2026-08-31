from app import app
from orders import db, Admin
from werkzeug.security import generate_password_hash


with app.app_context():

    username = "admin"
    password = "admin123"

    password_hash = generate_password_hash(password)

    admin = Admin(
        username=username,
        password_hash=password_hash,
        role="admin"
    )

    db.session.add(admin)
    db.session.commit()

    print("Admin created successfully!")