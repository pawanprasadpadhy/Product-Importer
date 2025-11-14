function openCreateModal() {
    document.getElementById('modalTitle').textContent = 'Add Product';
    document.getElementById('productForm').reset();
    document.getElementById('productId').value = '';
    document.getElementById('sku').disabled = false;
    document.getElementById('productModal').style.display = 'block';
}

async function openEditModal(productId) {
    try {
        const response = await fetch(`/products/${productId}/`);
        const product = await response.json();
        
        document.getElementById('modalTitle').textContent = 'Edit Product';
        document.getElementById('productId').value = product.id;
        document.getElementById('sku').value = product.sku;
        document.getElementById('sku').disabled = true; // SKU cannot be changed
        document.getElementById('name').value = product.name;
        document.getElementById('description').value = product.description;
        document.getElementById('is_active').checked = product.is_active;
        
        document.getElementById('productModal').style.display = 'block';
    } catch (error) {
        alert('Error loading product: ' + error.message);
    }
}

function closeModal() {
    document.getElementById('productModal').style.display = 'none';
}

document.getElementById('productForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const productId = document.getElementById('productId').value;
    const data = {
        sku: document.getElementById('sku').value,
        name: document.getElementById('name').value,
        description: document.getElementById('description').value,
        is_active: document.getElementById('is_active').checked
    };
    
    try {
        let response;
        if (productId) {
            // Update existing product
            response = await fetch(`/products/${productId}/`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
        } else {
            // Create new product
            response = await fetch('/products/create/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
        }
        
        if (response.ok) {
            alert('Product saved successfully!');
            closeModal();
            location.reload();
        } else {
            const error = await response.json();
            alert('Error: ' + (error.error || 'Failed to save product'));
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
});

async function deleteProduct(productId) {
    if (!confirm('Are you sure you want to delete this product?')) {
        return;
    }
    
    try {
        const response = await fetch(`/products/${productId}/`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            alert('Product deleted successfully!');
            location.reload();
        } else {
            alert('Error deleting product');
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('productModal');
    if (event.target == modal) {
        closeModal();
    }
}
