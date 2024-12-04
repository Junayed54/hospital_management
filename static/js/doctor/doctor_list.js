document.addEventListener("DOMContentLoaded", function() {
    fetch('/doctors/')
        .then(response => response.json())
        .then(data => {
            console.log(data);
            const container = document.getElementById('doctor-list');
            data.forEach(doctor => {
                const doctorCard = `
                    <div class="bg-white shadow-lg rounded-lg p-6 mb-4">
                        <h2 class="text-2xl font-semibold text-center">${doctor.full_name}</h2>
                        <p class="text-gray-500 text-center">${doctor.specialty}</p>
                        
                        <p><strong>Experience:</strong> ${doctor.experience_years} years</p>
                        <p><strong>Education:</strong> ${doctor.education}</p>
                        <p><strong>Consultation Fee:</strong> $${doctor.consultation_fee}</p>
                        
                        
                        <a href="/appointment/${doctor.id}/" class="block text-center bg-blue-500 text-white py-2 rounded-lg mt-4 hover:bg-blue-600">
                            Book Appointment
                        </a>
                        <a href="/doctor_appointments/${doctor.id}/" class="block text-center bg-blue-500 text-white py-2 rounded-lg mt-4 hover:bg-blue-600">
                            All Appointments
                        </a>
                    </div>`;
                container.innerHTML += doctorCard;
            });
        })
        .catch(error => console.error('Error fetching doctors:', error));
});

