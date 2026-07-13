// ---------- helpers ----------
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}

function todayISO() {
    const d = new Date();
    const offset = d.getTimezoneOffset();
    const local = new Date(d.getTime() - offset * 60000);
    return local.toISOString().split('T')[0];
}

// converts "13:00" -> "1 PM", "10:00" -> "10 AM"
function to12Hour(hhmm) {
    const [hStr] = hhmm.split(':');
    let h = parseInt(hStr, 10);
    const period = h >= 12 ? 'PM' : 'AM';
    let displayHour = h % 12;
    if (displayHour === 0) displayHour = 12;
    return `${displayHour} ${period}`;
}

// ---------- Booking form (book.html) ----------
function initBookingForm() {
    const dateInput = document.getElementById('reservation_date');
    const slotSelect = document.getElementById('reservation_slot');
    const form = document.getElementById('booking-form');
    const message = document.getElementById('form-message');
    const panelTitle = document.getElementById('bookings-panel-title');
    const panelList = document.getElementById('bookings-panel-list');
    const panelEmpty = document.getElementById('bookings-panel-empty');

    // criterion 13: current date automatically selected
    if (!dateInput.value) {
        dateInput.value = todayISO();
    }

    // criteria 6, 7, 8, 9, 11: show current bookings for the selected date,
    // grey out slots that are already taken, refresh whenever the date changes
    function refreshBookingsForDate() {
        panelTitle.textContent = `Bookings For ${dateInput.value}`;

        fetch(`/bookings?date=${dateInput.value}`)
            .then(response => response.json())
            .then(existingBookings => {
                // update the side panel list
                panelList.innerHTML = '';
                if (existingBookings.length === 0) {
                    panelEmpty.style.display = 'block';
                } else {
                    panelEmpty.style.display = 'none';
                    existingBookings.forEach(b => {
                        const li = document.createElement('li');
                        li.textContent = `${b.first_name} - ${to12Hour(b.reservation_slot)}`;
                        panelList.appendChild(li);
                    });
                }

                // grey out already-taken slots in the select
                const takenSlots = existingBookings.map(b => b.reservation_slot);
                Array.from(slotSelect.options).forEach(option => {
                    option.disabled = takenSlots.includes(option.value);
                });
                if (slotSelect.selectedOptions[0] && slotSelect.selectedOptions[0].disabled) {
                    slotSelect.value = '';
                }
            })
            .catch(err => console.error('Could not load existing bookings:', err));
    }

    dateInput.addEventListener('change', refreshBookingsForDate); // criterion 8
    refreshBookingsForDate();

    form.addEventListener('submit', function (event) {
        event.preventDefault();
        message.textContent = '';
        message.className = '';

        const payload = {
            first_name: document.getElementById('first_name').value.trim(),
            reservation_date: dateInput.value,
            reservation_slot: slotSelect.value,
        };

        fetch('/bookings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify(payload),
        })
            .then(async response => {
                const data = await response.json();
                if (!response.ok) throw new Error(data.error || 'Could not create the booking.');
                return data;
            })
            .then(() => {
                message.textContent = 'Your table has been reserved!';
                message.className = 'success';
                form.reset();
                dateInput.value = todayISO();
                refreshBookingsForDate();
            })
            .catch(err => {
                message.textContent = err.message;
                message.className = 'error';
                refreshBookingsForDate(); // someone else may have just taken the slot
            });
    });
}

// ---------- Reservations page (reservations.html) ----------
function initReservationsPage() {
    const filterDate = document.getElementById('filter_date');
    const tbody = document.getElementById('reservations-body');
    const noBookingsMessage = document.getElementById('no-bookings-message');

    function loadReservations() {
        const url = filterDate.value ? `/bookings?date=${filterDate.value}` : '/bookings';
        fetch(url)
            .then(response => response.json())
            .then(data => {
                tbody.innerHTML = '';
                if (data.length === 0) {
                    noBookingsMessage.style.display = 'block'; // criterion 11
                } else {
                    noBookingsMessage.style.display = 'none';
                    data.forEach(b => {
                        const row = document.createElement('tr');
                        row.innerHTML = `<td>${b.first_name}</td><td>${b.reservation_date}</td><td>${to12Hour(b.reservation_slot)}</td>`;
                        tbody.appendChild(row);
                    });
                }
            })
            .catch(err => console.error('Could not load reservations:', err));
    }

    filterDate.addEventListener('change', loadReservations); // criterion 8
    loadReservations();
}
