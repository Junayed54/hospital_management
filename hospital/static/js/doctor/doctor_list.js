// document.addEventListener("DOMContentLoaded", function() {
//     fetch('/doctors/')
//         .then(response => response.json())
//         .then(data => {
//             console.log(data);
//             const container = document.getElementById('doctor-list');
//             data.forEach(doctor => {
//                 const doctorCard = `
//                     <div class="bg-white shadow-lg rounded-lg p-6 mb-4">
//                         <h2 class="text-2xl font-semibold text-center">${doctor.full_name}</h2>
//                         <p class="text-gray-500 text-center">${doctor.specialty}</p>
                        
//                         <p><strong>Experience:</strong> ${doctor.experience_years} years</p>
//                         <p><strong>Education:</strong> ${doctor.education}</p>
//                         <p><strong>Consultation Fee:</strong> $${doctor.consultation_fee}</p>
                        
                        
//                         <a href="/appointment/${doctor.id}/" class="block text-center bg-blue-500 text-white py-2 rounded-lg mt-4 hover:bg-blue-600">
//                             Book Appointment
//                         </a>
//                         <a href="/doctor_appointments/${doctor.id}/" class="block text-center bg-blue-500 text-white py-2 rounded-lg mt-4 hover:bg-blue-600">
//                             All Appointments
//                         </a>
//                     </div>`;
//                 container.innerHTML += doctorCard;
//             });
//         })
//         .catch(error => console.error('Error fetching doctors:', error));
// });

document.addEventListener("DOMContentLoaded", function () {
    // Helper function to convert 24-hour time to 12-hour format
    function convertTo12HourFormat(time24) {
        const [hours, minutes] = time24.split(':').map(Number);
        const period = hours >= 12 ? 'PM' : 'AM';
        const hours12 = hours % 12 || 12; // Convert 0 to 12 for midnight
        return `${hours12}:${minutes.toString().padStart(2, '0')} ${period}`;
    }

    fetch('/doctors/')
        .then(response => response.json())
        .then(data => {
            console.log(data);
            const container = document.getElementById('doctor-list');
            data.forEach(doctor => {
                let availabilityHTML = '';

                // Loop through each availability for the doctor
                doctor.availability.forEach(avail => {
                    const formattedTime = convertTo12HourFormat(avail.start_time);
                    availabilityHTML += `
                        <div class="border p-2 my-2 rounded bg-gray-100">
                            <p><strong>Date:</strong> ${avail.date}</p>
                            <p><strong>Start Time:</strong> ${formattedTime}</p>
                            <p><strong>Max Patients:</strong> ${avail.max_patients}</p>
                            <p><strong>Booked Patients:</strong> ${avail.booked_patients}</p>
                            <a href="/appointment/${doctor.id}/${avail.id}/" class="block text-center bg-green-500 text-white py-2 rounded-lg mt-2 hover:bg-green-600">
                                Book Now
                            </a>
                        </div>`;
                });

                const doctorCard = `
                    <div class="bg-white shadow-lg rounded-lg p-6 mb-4">
                        <h2 class="text-2xl font-semibold text-center">${doctor.full_name}</h2>
                        <p class="text-gray-500 text-center">${doctor.specialty}</p>
                        
                        <p><strong>Experience:</strong> ${doctor.experience_years} years</p>
                        <p><strong>Education:</strong> ${doctor.education}</p>
                        <p><strong>Consultation Fee:</strong> $${doctor.consultation_fee}</p>
                        
                        <h3 class="mt-4 text-xl font-semibold">Availability</h3>
                        ${availabilityHTML}
                        
                        <a href="/doctor_appointments/${doctor.id}/" class="block text-center bg-blue-500 text-white py-2 rounded-lg mt-4 hover:bg-blue-600">
                            View All Appointments
                        </a>
                    </div>`;
                container.innerHTML += doctorCard;
            });
        })
        .catch(error => console.error('Error fetching doctors:', error));
});


