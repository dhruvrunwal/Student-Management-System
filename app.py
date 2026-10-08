from flask import Flask, request, jsonify, render_template
import sqlite3

app = Flask(__name__)

DATABASE = "students.db"


# ---------------- DATABASE ----------------

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


# ---------------- FRONTEND ----------------

@app.route("/")
def home():
    return render_template("index.html")


# ---------------- GET ALL STUDENTS ----------------

@app.route("/students", methods=["GET"])
def get_students():

    conn = get_db_connection()

    students = conn.execute(
        "SELECT * FROM students ORDER BY id DESC"
    ).fetchall()

    conn.close()

    return jsonify([dict(student) for student in students])


# ---------------- SEARCH STUDENT ----------------

@app.route("/students/search", methods=["GET"])
def search_student():

    query = request.args.get("query", "")

    conn = get_db_connection()

    students = conn.execute("""
        SELECT * FROM students
        WHERE name LIKE ?
        OR roll_no LIKE ?
    """, (f"%{query}%", f"%{query}%")).fetchall()

    conn.close()

    return jsonify([dict(student) for student in students])


# ---------------- ADD STUDENT ----------------

@app.route("/students", methods=["POST"])
def add_student():

    data = request.get_json()

    name = data.get("name")
    roll_no = data.get("roll_no")
    class_name = data.get("class_name")
    marks = data.get("marks")
    contact = data.get("contact")

    # Validation
    if not name or not roll_no or not class_name or marks == "" or not contact:
        return jsonify({
            "error": "All fields are required"
        }), 400

    try:
        marks = float(marks)

        if marks < 0 or marks > 100:
            return jsonify({
                "error": "Marks must be between 0 and 100"
            }), 400

        conn = get_db_connection()

        conn.execute("""
            INSERT INTO students
            (name, roll_no, class_name, marks, contact)
            VALUES (?, ?, ?, ?, ?)
        """, (name, roll_no, class_name, marks, contact))

        conn.commit()
        conn.close()

        return jsonify({
            "message": "Student added successfully"
        }), 201

    except sqlite3.IntegrityError:

        return jsonify({
            "error": "Roll number already exists"
        }), 400


# ---------------- UPDATE STUDENT ----------------

@app.route("/students/<int:id>", methods=["PUT"])
def update_student(id):

    data = request.get_json()

    name = data.get("name")
    roll_no = data.get("roll_no")
    class_name = data.get("class_name")
    marks = data.get("marks")
    contact = data.get("contact")

    if not name or not roll_no or not class_name or marks == "" or not contact:
        return jsonify({
            "error": "All fields are required"
        }), 400

    try:

        marks = float(marks)

        if marks < 0 or marks > 100:
            return jsonify({
                "error": "Marks must be between 0 and 100"
            }), 400

        conn = get_db_connection()

        result = conn.execute("""
            UPDATE students
            SET name = ?,
                roll_no = ?,
                class_name = ?,
                marks = ?,
                contact = ?
            WHERE id = ?
        """, (
            name,
            roll_no,
            class_name,
            marks,
            contact,
            id
        ))

        conn.commit()

        if result.rowcount == 0:
            conn.close()

            return jsonify({
                "error": "Student not found"
            }), 404

        conn.close()

        return jsonify({
            "message": "Student updated successfully"
        })

    except sqlite3.IntegrityError:

        return jsonify({
            "error": "Roll number already exists"
        }), 400


# ---------------- DELETE STUDENT ----------------

@app.route("/students/<int:id>", methods=["DELETE"])
def delete_student(id):

    conn = get_db_connection()

    result = conn.execute(
        "DELETE FROM students WHERE id = ?",
        (id,)
    )

    conn.commit()
    conn.close()

    if result.rowcount == 0:
        return jsonify({
            "error": "Student not found"
        }), 404

    return jsonify({
        "message": "Student deleted successfully"
    })


# ---------------- RUN APPLICATION ----------------

if __name__ == "__main__":
    init_db()

    app.run(
        debug=True
    )