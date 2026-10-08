let editingStudentId = null;


// ---------------- LOAD STUDENTS ----------------

async function loadStudents() {

    const response = await fetch("/students");

    const students = await response.json();

    displayStudents(students);
}


// ---------------- DISPLAY STUDENTS ----------------

function displayStudents(students) {

    const tableBody = document.getElementById(
        "studentTableBody"
    );

    tableBody.innerHTML = "";

    if (students.length === 0) {

        tableBody.innerHTML = `
            <tr>
                <td colspan="7">
                    No students found
                </td>
            </tr>
        `;

        return;
    }


    students.forEach(student => {

        const row = document.createElement("tr");

        row.innerHTML = `

            <td>${student.id}</td>

            <td>${student.name}</td>

            <td>${student.roll_no}</td>

            <td>${student.class_name}</td>

            <td>${student.marks}</td>

            <td>${student.contact}</td>

            <td>

                <button
                    class="edit-btn"
                    onclick="editStudent(${student.id})"
                >
                    Edit
                </button>

                <button
                    class="delete-btn"
                    onclick="deleteStudent(${student.id})"
                >
                    Delete
                </button>

            </td>

        `;

        tableBody.appendChild(row);

    });
}


// ---------------- ADD / UPDATE STUDENT ----------------

document.getElementById("studentForm")
.addEventListener("submit", async function(event) {

    event.preventDefault();


    const student = {

        name: document.getElementById("name").value,

        roll_no: document.getElementById("roll_no").value,

        class_name: document.getElementById("class_name").value,

        marks: document.getElementById("marks").value,

        contact: document.getElementById("contact").value

    };


    let url = "/students";

    let method = "POST";


    // UPDATE

    if (editingStudentId !== null) {

        url = `/students/${editingStudentId}`;

        method = "PUT";

    }


    const response = await fetch(url, {

        method: method,

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify(student)

    });


    const result = await response.json();


    if (!response.ok) {

        alert(result.error);

        return;

    }


    alert(result.message);


    resetForm();

    loadStudents();

});


// ---------------- SEARCH ----------------

async function searchStudents() {

    const query = document.getElementById(
        "searchInput"
    ).value;


    if (query.trim() === "") {

        loadStudents();

        return;

    }


    const response = await fetch(
        `/students/search?query=${encodeURIComponent(query)}`
    );


    const students = await response.json();

    displayStudents(students);

}


// ---------------- EDIT ----------------

async function editStudent(id) {

    const response = await fetch("/students");

    const students = await response.json();


    const student = students.find(
        s => s.id === id
    );


    if (!student) {

        alert("Student not found");

        return;

    }


    document.getElementById("name").value =
        student.name;

    document.getElementById("roll_no").value =
        student.roll_no;

    document.getElementById("class_name").value =
        student.class_name;

    document.getElementById("marks").value =
        student.marks;

    document.getElementById("contact").value =
        student.contact;


    editingStudentId = id;


    document.getElementById("formTitle")
        .innerText = "Update Student";


    document.getElementById("submitButton")
        .innerText = "Update Student";


    document.getElementById("cancelButton")
        .style.display = "block";

}


// ---------------- DELETE ----------------

async function deleteStudent(id) {

    const confirmDelete = confirm(
        "Are you sure you want to delete this student?"
    );


    if (!confirmDelete) {

        return;

    }


    const response = await fetch(
        `/students/${id}`,
        {
            method: "DELETE"
        }
    );


    const result = await response.json();


    if (!response.ok) {

        alert(result.error);

        return;

    }


    alert(result.message);

    loadStudents();

}


// ---------------- RESET FORM ----------------

function resetForm() {

    document.getElementById("studentForm")
        .reset();

    editingStudentId = null;


    document.getElementById("formTitle")
        .innerText = "Add Student";


    document.getElementById("submitButton")
        .innerText = "Add Student";


    document.getElementById("cancelButton")
        .style.display = "none";

}


// ---------------- CANCEL EDIT ----------------

function cancelEdit() {

    resetForm();

}


// ---------------- INITIAL LOAD ----------------

loadStudents();
