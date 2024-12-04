// style part

let menu = document.querySelector('#menu-btn');
let navbar = document.querySelector('.navbar');


menu.onclick = () => {
    menu.classList.toggle('fa-times');
    navbar.classList.toggle('active');
}


window.onscroll = () => {
    menu.classList.remove('fa-times');
    navbar.classList.remove('active');
}








// // data part
// document.addEventListener('DOMContentLoaded', () => {
    
//     const fetchData = (url, elementId, templateFunction) => {
//         fetch(url)
//             .then(response => response.json())
//             .then(data => {
//                 const container = document.getElementById(elementId);
//                 container.innerHTML = '';
//                 data.forEach(item => container.innerHTML += templateFunction(item));
//             })
//             .catch(error => console.error('Error fetching data:', error));
//     };

//     // Template functions
//     const doctorTemplate = (doctor) => `
//         <div class="bg-white p-6 shadow rounded-lg">
//             <h3 class="text-lg font-bold">${doctor.user.full_name}</h3>
//             <p><strong>Specialty:</strong> ${doctor.specialty}</p>
//             <p><strong>Experience:</strong> ${doctor.experience_years} years</p>
//             <p><strong>Consultation Fee:</strong> $${doctor.consultation_fee}</p>
//         </div>
//     `;

//     const patientTemplate = (patient) => `
//         <div class="bg-white p-6 shadow rounded-lg">
//             <h3 class="text-lg font-bold">${patient.user.full_name}</h3>
//             <p><strong>Blood Type:</strong> ${patient.blood_type}</p>
//             <p><strong>Emergency Contact:</strong> ${patient.emergency_contact}</p>
//         </div>
//     `;

//     const appointmentTemplate = (appointment) => `
//         <div class="bg-white p-6 shadow rounded-lg">
//             <h3 class="text-lg font-bold">Appointment with Dr. ${appointment.doctor.user.full_name}</h3>
//             <p><strong>Patient:</strong> ${appointment.patient.user.full_name}</p>
//             <p><strong>Date:</strong> ${new Date(appointment.appointment_date).toLocaleString()}</p>
//             <p><strong>Status:</strong> ${appointment.status}</p>
//         </div>
//     `;

//     const treatmentTemplate = (treatment) => `
//         <div class="bg-white p-6 shadow rounded-lg">
//             <h3 class="text-lg font-bold">Treatment for ${treatment.patient.user.full_name}</h3>
//             <p><strong>Diagnosis:</strong> ${treatment.diagnosis}</p>
//             <p><strong>Date:</strong> ${treatment.treatment_date}</p>
//             <p><strong>Cost:</strong> $${treatment.cost}</p>
//         </div>
//     `;

//     // Fetch data and populate sections
//     fetchData('/api/doctors/', 'doctors-list', doctorTemplate);
//     fetchData('/api/patients/', 'patients-list', patientTemplate);
//     fetchData('/api/appointments/', 'appointments-list', appointmentTemplate);
//     fetchData('/api/treatments/', 'treatments-list', treatmentTemplate);
// });
