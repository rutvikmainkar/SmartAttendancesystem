// ---------------- DASHBOARD STATS ----------------
function loadDashboardStats(){
    fetch("/dashboard-stats")
    .then(res=>res.json())
    .then(data=>{
        let students=document.getElementById("studentsCount")
        let subjects=document.getElementById("subjectsCount")
        let sessions=document.getElementById("sessionsCount")

        if(students) students.textContent=data.students
        if(subjects) subjects.textContent=data.subjects
        if(sessions) sessions.textContent=data.sessions
    })
}

// ---------------- LOAD SUBJECTS ----------------
function loadSubjects(){
    fetch("/subjects")
    .then(res=>res.json())
    .then(data=>{
        let select=document.getElementById("subjectSelect")
        if(!select) return

        select.innerHTML=""
        data.forEach(subject=>{
            let option=document.createElement("option")
            option.value=subject.subject_id
            option.textContent=subject.subject_name
            select.appendChild(option)
        })
    })
}

// ---------------- START SESSION ----------------
function startSession(){
    let subject=document.getElementById("subjectSelect")

    if(!subject || subject.value === ""){
        alert("Select a valid subject first")
        return
    }

    let subject_id=subject.value
    fetch("/start-session",{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({subject_id:subject_id})
    })
    .then(res=>res.json())
    .then(data=>{
        alert(data.message)
        loadDashboardStats()
    })
}

// ---------------- END SESSION ----------------
function endSession(){
    fetch("/end-session",{method:"POST"})
    .then(res=>res.json())
    .then(data=>{
        alert(data.message)
        loadDashboardStats()
    })
}

// ---------------- GENERATE REPORT ----------------
function generateReport(){
    let subject=document.getElementById("subjectSelect")

    if(!subject || subject.value === ""){
        alert("Select a valid subject first")
        return
    }

    let subject_id=subject.value
    fetch("/generate-report",{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({subject_id:subject_id})
    })
    .then(res=>res.json())
    .then(data=>alert(data.message))
}

// ---------------- VIEW SWITCH ----------------
function switchView(view){
    let list=document.getElementById("listView")
    let grid=document.getElementById("gridView")

    if(view==="grid"){
        list.style.display="none"
        grid.style.display="grid"
    }

    if(view==="list"){
        list.style.display="block"
        grid.style.display="none"
    }
}

// ---------------- LOAD STUDENTS ----------------
function loadStudents(){
    fetch("/students")
    .then(res=>res.json())
    .then(data=>{
        let table=document.querySelector("#studentsTable tbody")
        let grid=document.getElementById("gridView")

        // Exit immediately if the user is not on the attendance page
        if(!table || !grid) return;

        table.innerHTML=""
        grid.innerHTML=""

        data.forEach(student=>{
            /* TABLE ROW */
            let row=document.createElement("tr")
            row.innerHTML=`
            <td>${student.roll_number}</td>
            <td>${student.full_name}</td>
            <td>
                <button onclick="mark(${student.student_id})">Present</button>
            </td>
            `
            table.appendChild(row)

            /* GRID CARD */
            let card=document.createElement("div")
            card.classList.add("student-card")
            card.innerHTML=`
            <div class="student-name">${student.full_name}</div>
            <div class="student-roll">Roll ${student.roll_number}</div>
            `
            card.onclick=function(){
                card.classList.toggle("present")
                mark(student.student_id)
            }
            grid.appendChild(card)
        })
    })
}

// ---------------- MARK ATTENDANCE ----------------
function mark(id){
    fetch("/mark-attendance",{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({student_id:id})
    })
    .then(res=>res.json())
    .then(data=>console.log(data.message)) // Changed to console.log to avoid spamming alerts in grid mode
}

// ---------------- PAGE LOAD ----------------
window.onload=function(){
    if(document.getElementById("studentsCount")){
        loadDashboardStats()
    }

    if(document.querySelector("#studentsTable")){
        loadStudents()
    }

    if(document.getElementById("subjectSelect")){
        loadSubjects()
    }
}

// ---------------- START SMART CAMERA ----------------
function startCamera(){
    alert("Starting Camera... Please look at the server window.");

    fetch("/start-camera", {
        method: "POST"
    })
    .then(res => res.json())
    .then(data => {
        alert(data.message);
        // Reload the grid/table to show the newly marked students!
        loadStudents();
    });
}