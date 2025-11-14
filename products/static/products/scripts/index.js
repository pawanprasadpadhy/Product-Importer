let currentJobId = null;
let progressInterval = null;

document.getElementById('uploadForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData();
    const fileInput = document.getElementById('csvFile');
    formData.append('file', fileInput.files[0]);
    
    document.getElementById('uploadProgress').style.display = 'block';
    document.getElementById('progressText').textContent = 'Starting upload...';
    
    try {
        const response = await fetch('/upload/', {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            currentJobId = data.job_id;
            startProgressTracking(data.job_id);
        } else {
            showError(data.error);
        }
    } catch (error) {
        showError('Upload failed: ' + error.message);
    }
});

function startProgressTracking(jobId) {
    progressInterval = setInterval(async () => {
        try {
            const response = await fetch(`/upload/${jobId}/progress/`);
            const data = await response.json();
            
            const progress = data.progress;
            document.getElementById('progressFill').style.width = progress + '%';
            document.getElementById('progressFill').textContent = progress + '%';
            
            document.getElementById('progressText').textContent = 
                `Processing: ${data.processed_rows} / ${data.total_rows} rows`;
            
            if (data.status === 'completed') {
                clearInterval(progressInterval);
                document.getElementById('progressText').textContent = 
                    `✓ Upload completed! ${data.total_rows} products processed.`;
                document.getElementById('uploadResult').innerHTML = 
                    '<div class="alert alert-success">Upload completed successfully!</div>';
            } else if (data.status === 'failed') {
                clearInterval(progressInterval);
                showError(data.error_message);
            }
        } catch (error) {
            console.error('Error fetching progress:', error);
        }
    }, 1000);
}

function showError(message) {
    document.getElementById('uploadResult').innerHTML = 
        `<div class="alert alert-error">Error: ${message}</div>`;
    document.getElementById('uploadProgress').style.display = 'none';
    if (progressInterval) {
        clearInterval(progressInterval);
    }
}

async function confirmBulkDelete() {
    if (!confirm('Are you sure you want to delete ALL products? This action cannot be undone!')) {
        return;
    }
    
    try {
        const response = await fetch('/products/bulk-delete/', {
            method: 'POST'
        });
        
        if (response.ok) {
            alert('All products are being deleted in the background.');
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}
