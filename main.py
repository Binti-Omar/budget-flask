from flask import Flask,jsonify,request
from flask_jwt_extended import JWTManager,jwt_required,create_access_token
from flask_bcrypt import Bcrypt
from sqlalchemy import create_engine,select
from sqlalchemy.orm import sessionmaker
from database import Budget,Base,User
from flask_cors import CORS
from datetime import datetime


app = Flask(__name__)
app.config["JWT_SECRET_KEY"]="adrgijj765"

CORS(app)

jwt=JWTManager(app)

bcrypt=Bcrypt(app)

DATABASE_URL = "postgresql+psycopg2://postgres:C0717824020@localhost:5432/budget"

engine = create_engine(DATABASE_URL,echo=False)

session = sessionmaker(bind=engine)
mysession = session()

Base.metadata.create_all(engine)

allowed_methods = ["GET","POST","DELETE","PATCH"]

@app.route('/',methods=allowed_methods)
def home():
    method = request.method.lower()
    if method == "get":
        return jsonify({"Flask API Version":"1.0"}),200
    else:
        return jsonify({"msg":"Method not allowed"}),405

@app.route("/register",methods=allowed_methods)
def register():
    try:
        method = request.method.lower()

        if method == "post":
            data = request.get_json()

            if data["name"] == "" or data["email"] == "" or data["password"] == "":
                return jsonify({"error": "name, email and password cannot be empty"}), 400
            
            existing_user = mysession.query(User).filter_by(email=data["email"]).first()
            if existing_user:
                return jsonify({"error": "Email already registered"}), 409
            
            hashed_pw = bcrypt.generate_password_hash(data['password']).decode('utf-8')
            
            new_user = User(
                name=data['name'],
                email=data['email'],
                hashed_pw=hashed_pw,
                created_at=datetime.utcnow()
            )

            mysession.add(new_user)
            mysession.commit()

            token=create_access_token(identity=data["email"])

            return jsonify({"message": "User registered successfully","token":f"{token}"}), 201
            
        else:
            return jsonify({"msg": "Method not allowed"}), 405
    except Exception as e:
            return jsonify({"error": str(e)}), 500

@app.route('/login',methods=allowed_methods)
def login():
        try:
            method = request.method.lower()

            if method == "post":
                data = request.get_json()

                email = data.get("email")
                password = data.get("password")

                if not email or not password:
                    return jsonify({"error": "Email and password required"}),400
                
                query = select(User).where(User.email==email)
                existing_user = mysession.scalars(query).first()

                if not existing_user:
                    return {"error": "Invalid email"}, 401
                
                if not bcrypt.check_password_hash(existing_user.hashed_pw, password):
                    return {"error": "Invalid password"}, 401
    
                token=create_access_token(identity=data["email"])
                
                return jsonify({
                    "message": "Login successful",
                    "user": {
                        "id": existing_user.id,
                        "name": existing_user.name,
                        "email": existing_user.email},
                        "token":f"{token}"
                    }),200
            
            else:
                return jsonify({"msg": "Method not allowed"}), 405
        except Exception as e:
                return jsonify({"error":str(e)})
        
@app.route("/budget", methods=allowed_methods)
@jwt_required()
def budget():
    try:
        method = request.method.lower()

        if method == "get":
            query = select(Budget)
            budgets = mysession.scalars(query).all()

            budget_list = []
            for b in budgets:
                budget_list.append({
                    "id": b.id,
                    "title": b.title,
                    "amount": b.amount,
                    "date": b.date
                })

            return jsonify(budget_list), 200

        elif method == "post":
            data = request.get_json()

            title = data.get("title")
            amount = data.get("amount")
            date = data.get("date")

            # validation
            if not title or not amount :
                return jsonify({"error": "All fields are required"}), 400

            new_budget = Budget(
                title=title,
                amount=float(amount),
                date=datetime.fromisoformat(date)
            )

            mysession.add(new_budget)
            mysession.commit()

            return jsonify({"message": "Budget created"}), 201

        else:
            return jsonify({"error": "Method not allowed"}), 405

    except Exception as e:
        return jsonify({"error": str(e)}), 500
   
    
          
app.run(debug=True)