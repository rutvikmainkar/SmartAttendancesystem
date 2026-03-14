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

if(!subject){
alert("Select subject first")
return
}

let subject_id=subject.value

fetch("/start-session",{
method:"POST",
headers:{
"Content-Type":"application/json"
},
body:JSON.stringify({
subject_id:subject_id
})
})
.then(res=>res.json())
.then(data=>{
alert(data.message)
loadDashboardStats()
})

}


// ---------------- END SESSION ----------------

function endSession(){

fetch("/end-session",{
method:"POST"
})
.then(res=>res.json())
.then(data=>{
alert(data.message)
loadDashboardStats()
})

}


// ---------------- GENERATE REPORT ----------------

function generateReport(){

let subject=document.getElementById("subjectSelect")

if(!subject){
alert("Select subject first")
return
}

let subject_id=subject.value

fetch("/generate-report",{
method:"POST",
headers:{
"Content-Type":"application/json"
},
body:JSON.stringify({
subject_id:subject_id
})
})
.then(res=>res.json())
.then(data=>alert(data.message))

}


// ---------------- LOAD STUDENTS ----------------

function loadStudents(){

fetch("/students")
.then(res=>res.json())
.then(data=>{

let table=document.querySelector("#studentsTable tbody")

data.forEach(student=>{

let row=document.createElement("tr")

row.innerHTML=`
<td>${student.roll_number}</td>
<td>${student.full_name}</td>
<td>
<button onclick="mark(${student.student_id})">
Present
</button>
</td>
`

table.appendChild(row)

})

})

}


// ---------------- MARK ATTENDANCE ----------------

function mark(id){

fetch("/mark-attendance",{
method:"POST",
headers:{
"Content-Type":"application/json"
},
body:JSON.stringify({
student_id:id
})
})
.then(res=>res.json())
.then(data=>alert(data.message))

}


// ---------------- PAGE LOAD ----------------

window.onload=function(){

loadDashboardStats()

if(document.querySelector("#studentsTable")){
loadStudents()
}

if(document.getElementById("subjectSelect")){
loadSubjects()
}

}