function openCreateModal() {
    document.getElementById('modalTitle').textContent = 'Add Webhook';
    document.getElementById('webhookForm').reset();
    document.getElementById('webhookId').value = '';
    document.getElementById('webhookModal').style.display = 'block';
}

async function openEditModal(webhookId) {
    try {
        const response = await fetch(`/webhooks/${webhookId}/`);
        const webhook = await response.json();
        
        document.getElementById('modalTitle').textContent = 'Edit Webhook';
        document.getElementById('webhookId').value = webhook.id;
        document.getElementById('url').value = webhook.url;
        document.getElementById('event_type').value = webhook.event_type;
        document.getElementById('is_active').checked = webhook.is_active;
        
        document.getElementById('webhookModal').style.display = 'block';
    } catch (error) {
        alert('Error loading webhook: ' + error.message);
    }
}

function closeModal() {
    document.getElementById('webhookModal').style.display = 'none';
}

document.getElementById('webhookForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const webhookId = document.getElementById('webhookId').value;
    const data = {
        url: document.getElementById('url').value,
        event_type: document.getElementById('event_type').value,
        is_active: document.getElementById('is_active').checked
    };
    
    try {
        let response;
        if (webhookId) {
            response = await fetch(`/webhooks/${webhookId}/`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
        } else {
            response = await fetch('/webhooks/create/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
        }
        
        if (response.ok) {
            alert('Webhook saved successfully!');
            closeModal();
            location.reload();
        } else {
            const error = await response.json();
            alert('Error: ' + (error.error || 'Failed to save webhook'));
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
});

async function deleteWebhook(webhookId) {
    if (!confirm('Are you sure you want to delete this webhook?')) {
        return;
    }
    
    try {
        const response = await fetch(`/webhooks/${webhookId}/`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            alert('Webhook deleted successfully!');
            location.reload();
        } else {
            alert('Error deleting webhook');
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

async function testWebhook(webhookId) {
    try {
        const response = await fetch(`/webhooks/${webhookId}/test/`, {
            method: 'POST'
        });
        
        if (response.ok) {
            alert('Test webhook sent! Check your endpoint logs.');
        } else {
            alert('Error sending test webhook');
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

window.onclick = function(event) {
    const modal = document.getElementById('webhookModal');
    if (event.target == modal) {
        closeModal();
    }
}
