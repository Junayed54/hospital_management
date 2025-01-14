const apiUrl = '/doctor/availability/'; // Adjust to match your API URL
const token = localStorage.getItem('access_token'); // Retrieve the JWT token from localStorage

const headers = {
  'Content-Type': 'application/json',
  Authorization: `Bearer ${token}`,
};

// Fetch and display availability slots
async function fetchAvailability() {
  try {
    const response = await fetch(apiUrl, { headers });
    if (!response.ok) {
      throw new Error('Failed to fetch availability slots');
    }
    const data = await response.json();

    const availabilityList = document.getElementById('availability-slots');
    availabilityList.innerHTML = ''; // Clear existing slots

    data.forEach(slot => {
      const li = document.createElement('li');
      li.innerHTML = `
        <div class="flex justify-between items-center">
          <span>
            <strong>Date:</strong> ${slot.date} | 
            <strong>Start Time:</strong> ${slot.start_time} | 
            <strong>Duration:</strong> ${slot.session_duration} mins | 
            <strong>Max Patients:</strong> ${slot.max_patients}
          </span>
          <div>
            <button class="text-blue-500 ml-4" onclick="editSlot(${slot.id}, '${slot.date}', '${slot.start_time}', ${slot.session_duration}, ${slot.max_patients})">Edit</button>
            <button class="text-red-500 ml-4" onclick="deleteSlot(${slot.id})">Delete</button>
          </div>
        </div>
      `;
      availabilityList.appendChild(li);
    });
  } catch (error) {
    console.error('Error fetching slots:', error);
    alert('Error fetching availability slots. Please try again.');
  }
}

// Submit form (Create or Update)
document.getElementById('availability-form').addEventListener('submit', async (e) => {
  e.preventDefault();

  const id = document.getElementById('availability-id').value;
  const date = document.getElementById('date').value;
  const startTime = document.getElementById('start-time').value;
  const sessionDuration = document.getElementById('session-duration').value;
  const maxPatients = document.getElementById('max-patients').value;

  const method = id ? 'PUT' : 'POST';
  const url = id ? `${apiUrl}${id}/` : apiUrl;

  try {
    const response = await fetch(url, {
      method,
      headers,
      body: JSON.stringify({
        date,
        start_time: startTime,
        session_duration: sessionDuration,
        max_patients: maxPatients,
      }),
    });

    if (!response.ok) {
      throw new Error(`Failed to ${id ? 'update' : 'create'} slot`);
    }

    fetchAvailability();
    document.getElementById('availability-form').reset();
    document.getElementById('availability-id').value = '';
  } catch (error) {
    console.error('Error saving slot:', error);
    alert('Error saving slot. Please check the inputs and try again.');
  }
});

// Edit a slot
function editSlot(id, date, startTime, sessionDuration, maxPatients) {
  document.getElementById('availability-id').value = id;
  document.getElementById('date').value = date;
  document.getElementById('start-time').value = startTime;
  document.getElementById('session-duration').value = sessionDuration;
  document.getElementById('max-patients').value = maxPatients;
}

// Delete a slot
async function deleteSlot(id) {
  if (!confirm('Are you sure you want to delete this slot?')) return;

  try {
    const response = await fetch(`${apiUrl}${id}/`, {
      method: 'DELETE',
      headers,
    });

    if (!response.ok) {
      throw new Error('Failed to delete slot');
    }

    fetchAvailability();
  } catch (error) {
    console.error('Error deleting slot:', error);
    alert('Error deleting slot. Please try again.');
  }
}

// Initialize
fetchAvailability();
