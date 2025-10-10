import os
import io
import json
import base64
import bcrypt
from flask import request, jsonify
from PIL import Image
from datetime import datetime, date
import numpy as np
from database import Student

ADMIN_PATH = "data/admin.json"

# Ensure admin exist
if not os.path.exists(ADMIN_PATH):
    with open(ADMIN_PATH, "w") as f:
        hashed_pw = bcrypt.hashpw("admin123".encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        json.dump({"password": hashed_pw}, f)

def get_admin_password():
    with open(ADMIN_PATH, "r") as f:
        return json.load(f)["password"]

def set_admin_password(new_password):
    hashed_pw = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    with open(ADMIN_PATH, "w") as f:
        json.dump({"password": hashed_pw}, f)

def register_routes(app, db, Attendance, detector, embedder):

    def update_face(student, new_embedding):
        """Update existing student's face embedding in DB."""
        try:
            student.embedding = new_embedding
            db.session.commit()
            return True, f"Updated facial data for {student.name}"
        except Exception as e:
            db.session.rollback()
            return False, str(e)
        
    @app.route("/enroll", methods=["POST"])
    def enroll():
        try:
            data = request.json
            name = data["name"]
            mobile = data.get("mobile")
            email = data.get("email")
            image_data = data["image"].split(",")[1]
            image = Image.open(io.BytesIO(base64.b64decode(image_data)))

            faces = detector.detect_faces(np.array(image))

            if not faces:
                return jsonify({"error": "No face detected"}), 400

            if len(faces) > 1:
                return jsonify({
                    "error": "Multiple faces detected. Please provide an image with a single face."
                }), 400

            # Single face
            x, y, w, h = faces[0]["box"]
            face_crop = image.crop((x, y, x + w, y + h))
            embedding = embedder.embeddings([np.array(face_crop)])[0].tolist()

            # Check if student exists
            student = Student.query.filter_by(name=name).first()
            if student:
                # Instead of auto-update, prompt admin
                return jsonify({
                    "message": f"Student '{name}' already exists. Do you want to update facial data?",
                    "student_exists": True
                })

            # Create new student
            new_student = Student(
                name=name,
                mobile=mobile,
                email=email,
                embedding=embedding
            )
            db.session.add(new_student)
            db.session.commit()

            return jsonify({
                "message": f"User '{name}' enrolled successfully.",
                "faces_detected": 1,
                "updated": False
            })

        except Exception as e:
            return jsonify({"error": str(e)}), 500

        
    @app.route("/update-face", methods=["POST"])
    def update_face_route():
        try:
            data = request.json
            name = data["name"]
            image_data = data["image"].split(",")[1]
            image = Image.open(io.BytesIO(base64.b64decode(image_data)))

            faces = detector.detect_faces(np.array(image))
            if not faces:
                return jsonify({"error": "No face detected"}), 400

            if len(faces) > 1:
                return jsonify({
                    "error": "Multiple faces detected. Please provide an image with a single face."
                }), 400

            student = Student.query.filter_by(name=name).first()
            if not student:
                return jsonify({"error": f"Student '{name}' not found."}), 404

            # Single face crop
            x, y, w, h = faces[0]["box"]
            face_crop = image.crop((x, y, x + w, y + h))
            new_embedding = embedder.embeddings([np.array(face_crop)])[0].tolist()

            # Update embedding
            student.embedding = new_embedding
            db.session.commit()

            return jsonify({
                "message": f"Facial data for student '{name}' updated successfully.",
                "updated": True
            })

        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500


    @app.route("/recognize", methods=["POST"])
    def recognize():
        try:
            data = request.json
            image_data = data["image"].split(",")[1]
            image = Image.open(io.BytesIO(base64.b64decode(image_data)))

            faces = detector.detect_faces(np.array(image))
            if not faces:
                return jsonify({"error": "No face detected"}), 400
            
            students = Student.query.all()
            student_embeddings = {
                student.name: np.array(student.embedding) for student in students
            }
            results = []

            today = date.today().strftime("%Y-%m-%d")
            current_time = datetime.now().strftime("%H:%M:%S")

            for face in faces:
                x, y, w, h = face["box"]
                face_crop = image.crop((x, y, x + w, y + h))
                emb = embedder.embeddings([np.array(face_crop)])[0]

                match_name = "Unknown"
                min_dist = 1.0

                for name, stored_emb in student_embeddings.items():
                    dist = np.linalg.norm(emb - stored_emb)
                    if dist < min_dist:
                        min_dist = dist
                        match_name = name

                if match_name != "Unknown":
                    try:
                        existing_record = Attendance.query.filter_by(student=match_name, date=today).first()
                        if existing_record:
                            existing_record.outtime = current_time
                        else:
                            new_entry = Attendance(
                                student=match_name,
                                date=today,
                                intime=current_time,
                                outtime=current_time
                            )
                            db.session.add(new_entry)
                        db.session.commit()
                    except Exception as db_err:
                        db.session.rollback()
                        print("DB error:", db_err)

                results.append({
                    "name": match_name,
                    "bbox": [x, y, w, h],
                    "time": current_time
                })

            return jsonify({"faces": results})

        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    @app.route("/api/verify", methods=["POST"])
    def verify_password():
        data = request.json
        input_pw = data.get("password", "")
        stored_hashed_pw = get_admin_password().encode("utf-8")
        if bcrypt.checkpw(input_pw.encode("utf-8"), stored_hashed_pw):
            return jsonify({"success": True})
        else:
            return jsonify({"success": False}), 401

    @app.route("/api/update-password", methods=["POST"])
    def update_password():
        data = request.json
        old_pw = data.get("old_password", "")
        new_pw = data.get("new_password", "")
        stored_hashed_pw = get_admin_password().encode("utf-8")
        if bcrypt.checkpw(old_pw.encode("utf-8"), stored_hashed_pw):
            set_admin_password(new_pw)
            return jsonify({"message": "Password updated successfully!"})
        else:
            return jsonify({"error": "Old password is incorrect"}), 401
