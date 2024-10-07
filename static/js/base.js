document.addEventListener('DOMContentLoaded', function () {
    const container = document.querySelector('.container[data-customer-id]');
    // if (!container) {
    //     console.error('Container element not found');
    //     return;
    // }
    const customerId = container.getAttribute('data-customer-id');
    console.log("Customer ID: " + customerId)

    document.getElementById('editCustomerForm').addEventListener('submit', function (event) {
        event.preventDefault();

        const customerName = document.getElementById('customer_name').value;
        const awsRegion = document.getElementById('aws_region').value;
        const cxContacts = document.getElementById('cx_contacts').value.split(',').map(id => id.trim()).filter(id => id !== '');

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
                    // window.location.href = `${customerId}`;
                    showAlert('Customer updated successfully!', 'success');
                } else {
                    return response.json().then(data => {
                        // alert(data.detail, 'danger');
                        showAlert(data.detail, 'danger');
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


    function showAlert(message, type) {
        const alertPlaceholder = document.getElementById('alertPlaceholder');
        if (!alertPlaceholder) {
            console.error('Alert placeholder not found');
            return;
        }
        const wrapper = document.createElement('div');
        wrapper.innerHTML = [
            `<div class="alert alert-${type} alert-dismissible" role="alert">`,
            `   <div>${message}</div>`,
            '   <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>',
            '</div>'
        ].join('');

        const alertElement = wrapper.firstChild;
        alertPlaceholder.append(alertElement);

        // Remove the alert after 3 seconds
        setTimeout(() => {
            alertElement.remove();
        }, 3000);
    }

});


// document.addEventListener('DOMContentLoaded', function () {
//     const container = document.querySelector('.container[data-customer-id]');
//     const customerId = container.getAttribute('data-customer-id');

//     const cxContacts1 = document.getElementById('cx_contacts').value.split(',').map(id => parseInt(id.trim()));
//     console.log("CX COntacts: " + cxContacts1)

//     document.getElementById('editCustomerForm').addEventListener('submit', function (event) {
//         event.preventDefault();

//         const customerName = document.getElementById('customer_name').value;
//         const awsRegion = document.getElementById('aws_region').value;
//         // const cxContacts = document.getElementById('cx_contacts').value.split(',').map(id => parseInt(id.trim()));
//         const cxContacts = document.getElementById('cx_contacts').value.split(',').map(id => id.trim()).filter(id => id !== '');

//         console.log("CX COntacts: " + cxContacts)
//         const data = {
//             customer_name: customerName,
//             aws_region: awsRegion,
//             cx_contact_ids: cxContacts
//             // cx_contact_ids: cxContacts.join(',')
//         };

//         fetch(`/customers/${customerId}`, {
//             method: 'PUT',
//             headers: {
//                 'Content-Type': 'application/json'
//             },
//             body: JSON.stringify(data)
//         })
//             .then(response => {
//                 if (response.ok) {
//                     window.location.href = '/customer-page';
//                 } else {
//                     return response.json().then(data => {
//                         alert(data.detail);
//                     });
//                 }
//             });
//     });
// });