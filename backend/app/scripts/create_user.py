from app import app, db
from app.models.user import User

def create_test_user():
    with app.app_context():
        user = User(
            email="admin@example.com",
            name="Admin User"
        )
        user.set_password("admin123")
        db.session.add(user)
        db.session.commit()
        print("Test user created successfully")

if __name__ == "__main__":
    create_test_user()