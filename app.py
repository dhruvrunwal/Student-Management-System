
from flask import Flask, request, jsonify, render_template
import sqlite3
import csv
import os

app = Flask(__name__)

DATABASE = "students.db"
DATASET = "students_dataset.csv"


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            roll_no TEXT NOT NULL UNIQUE,
            class_name TEXT NOT NULL,
            marks REAL NOT NULL,
            contact TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def import_dataset():
    if not os.path.exists(DATASET):
        print("ERROR: students_dataset.csv not found!")
        print("Place the CSV file in the same folder as app.py.")
        return

    conn = get_db_connection()
    imported = 0

    try:
        with open(DATASET, mode="r", encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file)

            required_columns = {
                "name", "roll_no", "class_name", "marks", "contact"
            }

            if not reader.fieldnames or not required_columns.issubset(
                set(reader.fieldnames)
            ):
                print("ERROR: CSV column names are incorrect.")
                print("Required: name, roll_no, class_name, marks, contact")
                return

            for row in reader:
                try:
                    name = row["name"].strip()
                    roll_no = row["roll_no"].strip()
                    class_name = row["class_name"].strip()
                    marks = float(row["marks"])
                    contact = row["contact"].strip()

                    if not all([name, roll_no, class_name, contact]):
                        continue

                    cursor = conn.execute("""
                        INSERT OR IGNORE INTO students
                        (name, roll_no, class_name, marks, contact)
                        VALUES (?, ?, ?, ?, ?)
                    """, (name, roll_no, class_name, marks, contact))

                    if cursor.rowcount > 0:
                        imported += 1

                except (ValueError, TypeError, KeyError) as error:
                    print("Skipping invalid CSV row:", row, error)

            conn.commit()
            print(f"Dataset import complete. New records added: {imported}")

    except (OSError, csv.Error) as error:
        print("ERROR reading CSV dataset:", error)

    finally:
        conn.close()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/students", methods=["GET"])
def get_students():
    conn = get_db_connection()
    students = conn.execute(
        "SELECT * FROM students ORDER BY id DESC"
    ).fetchall()
    conn.close()

    return jsonify([dict(student) for student in students])


@app.route("/students/search", methods=["GET"])
def search_students():
    query = request.args.get("q", "").strip()

    conn = get_db_connection()
    students = conn.execute("""
        SELECT * FROM students
        WHERE name LIKE ?
           OR roll_no LIKE ?
           OR class_name LIKE ?
        ORDER BY id DESC
    """, (f"%{query}%", f"%{query}%", f"%{query}%")).fetchall()
    conn.close()

    return jsonify([dict(student) for student in students])


@app.route("/students", methods=["POST"])
def add_student():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No student data provided"}), 400

    try:
        name = data.get("name", "").strip()
        roll_no = data.get("roll_no", "").strip()
        class_name = data.get("class_name", "").strip()
        marks = float(data.get("marks"))
        contact = data.get("contact", "").strip()

        if not all([name, roll_no, class_name, contact]):
            return jsonify({"error": "All fields are required"}), 400

        conn = get_db_connection()
        conn.execute("""
            INSERT INTO students
            (name, roll_no, class_name, marks, contact)
            VALUES (?, ?, ?, ?, ?)
        """, (name, roll_no, class_name, marks, contact))
        conn.commit()
        conn.close()

        return jsonify({"message": "Student added successfully"}), 201

    except ValueError:
        return jsonify({"error": "Marks must be a valid number"}), 400

    except sqlite3.IntegrityError:
        return jsonify({"error": "Roll number already exists"}), 409


@app.route("/students/<int:student_id>", methods=["PUT"])
def update_student(student_id):
    data = request.get_json()

    if not data:
        return jsonify({"error": "No student data provided"}), 400

    try:
        name = data.get("name", "").strip()
        roll_no = data.get("roll_no", "").strip()
        class_name = data.get("class_name", "").strip()
        marks = float(data.get("marks"))
        contact = data.get("contact", "").strip()

        if not all([name, roll_no, class_name, contact]):
            return jsonify({"error": "All fields are required"}), 400

        conn = get_db_connection()

        cursor = conn.execute("""
            UPDATE students
            SET name = ?, roll_no = ?, class_name = ?,
                marks = ?, contact = ?
            WHERE id = ?
        """, (name, roll_no, class_name, marks, contact, student_id))

        conn.commit()
        updated = cursor.rowcount
        conn.close()

        if updated == 0:
            return jsonify({"error": "Student not found"}), 404

        return jsonify({"message": "Student updated successfully"})

    except ValueError:
        return jsonify({"error": "Marks must be a valid number"}), 400

    except sqlite3.IntegrityError:
        return jsonify({"error": "Roll number already exists"}), 409


@app.route("/students/<int:student_id>", methods=["DELETE"])
def delete_student(student_id):
    conn = get_db_connection()

    cursor = conn.execute(
        "DELETE FROM students WHERE id = ?", (student_id,)
    )

    conn.commit()
    deleted = cursor.rowcount
    conn.close()

    if deleted == 0:
        return jsonify({"error": "Student not found"}), 404

    return jsonify({"message": "Student deleted successfully"})


if __name__ == "__main__":
    init_db()
    import_dataset()
    app.run(debug=True)
