document.addEventListener('DOMContentLoaded', function () {
    const container = document.querySelector('.container[data-customer-id]');
    const customerId = container.getAttribute('data-customer-id');

    document.getElementById('editCustomerForm').addEventListener('submit', function (event) {
        event.preventDefault();

        const customerName = document.getElementById('customer_name').value;
        const awsRegion = document.getElementById('aws_region').value;
        const cxContacts = document.getElementById('cx_contacts').value.split(',').map(id => parseInt(id.trim()));

        const data = {
            customer_name: customerName,
            aws_region: awsRegion,
            cx_contact_ids: cxContacts
        };

        fetch(`/customers/${customerId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
            .then(response => {
                if (response.ok) {
                    window.location.href = '/customer-page';
                } else {
                    return response.json().then(data => {
                        alert(data.detail);
                    });
                }
            });
    });

    document.getElementById('saveContactsButton').addEventListener('click', function () {
        const selectedContacts = [];
        const selectedContactUsernames = [];
        document.querySelectorAll('#contactsForm .form-check-input:checked').forEach(function (checkbox) {
            selectedContacts.push(checkbox.value);
            selectedContactUsernames.push(checkbox.getAttribute('data-username'));
        });
        document.getElementById('cx_contacts').value = selectedContacts.join(', ');

        const selectedContactsList = document.getElementById('selectedContactsList');
        selectedContactsList.innerHTML = '';
        selectedContactUsernames.forEach(function (username) {
            const li = document.createElement('li');
            li.className = 'list-group-item';
            li.textContent = username;
            selectedContactsList.appendChild(li);
        });

        const modal = bootstrap.Modal.getInstance(document.getElementById('editContactsModal'));
        modal.hide();
    });
});
