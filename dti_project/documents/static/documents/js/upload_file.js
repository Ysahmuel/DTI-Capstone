document.addEventListener("DOMContentLoaded", function () {
    const openUploadFilesModalBtn = document.getElementById("upload-from-excel-btn");
    const uploadFilesModal = document.getElementById("upload-files-modal-container");
    const uploadFilesContainer = document.getElementById("upload-files-container");
    const closeUploadFilesModalBtn = uploadFilesModal ? uploadFilesModal.querySelector(".close-modal-btn") : null;

    const fileInput = document.getElementById("file-input");
    const uploadedFilesList = document.querySelector(".uploaded-files-list");
    const fileText = document.getElementById("file-text");
    const form = document.getElementById("excel-upload-form");
    const cancelBtn = document.getElementById("cancel-btn");

    let allFiles = [];
    let eventSource = null;
    let sessionId = null;

    if (openUploadFilesModalBtn && uploadFilesModal) {
        openUploadFilesModalBtn.addEventListener("click", function () {
            uploadFilesModal.style.display = "flex";
        });
    }

    if (closeUploadFilesModalBtn && uploadFilesModal) {
        closeUploadFilesModalBtn.addEventListener("click", function () {
            uploadFilesModal.style.display = "none";
            resetForm();
        });
    }

    if (cancelBtn && uploadFilesModal) {
        cancelBtn.addEventListener("click", function () {
            uploadFilesModal.style.display = "none";
            resetForm();
        });
    }

    if (uploadFilesContainer && fileInput) {
        uploadFilesContainer.addEventListener("click", () => {
            fileInput.click();
        });
    }

    if (fileInput && uploadedFilesList && fileText) {
        fileInput.addEventListener("change", (event) => {
            const newFiles = Array.from(event.target.files);
            if (newFiles.length === 0) return;

            allFiles = [...allFiles, ...newFiles];
            renderFileList();
            fileText.textContent = `(${allFiles.length}) files uploaded`;
        });
    }

    if (form) {
        form.addEventListener("submit", function (e) {
            e.preventDefault();

            if (allFiles.length === 0) {
                alert("Please select at least one file to upload.");
                return;
            }

            // Generate unique session ID
            sessionId = 'upload_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);

            // Create FormData
            const formData = new FormData();
            allFiles.forEach(file => {
                formData.append("files", file);
            });
            formData.append("session_id", sessionId);

            const csrfToken = form.querySelector('[name="csrfmiddlewaretoken"]').value;
            formData.append("csrfmiddlewaretoken", csrfToken);

            showProgressUI();
            uploadWithRealTimeProgress(formData);
        });
    }

    function renderFileList() {
        uploadedFilesList.innerHTML = "";
        
        if (allFiles.length === 0) {
            const li = document.createElement("li");
            li.className = "no-files";
            li.textContent = "No files yet";
            uploadedFilesList.appendChild(li);
            return;
        }

        allFiles.forEach((file, index) => {
            const li = document.createElement("li");
            li.innerHTML = `
                <i class="fa-solid fa-file"></i>
                <div class="details">
                    <strong>${file.name}</strong>
                    <p>${(file.size / 1024 / 1024).toFixed(2)} MB</p>
                </div>
                <i class="fa-solid fa-trash delete-file"></i>
            `;

            li.querySelector(".delete-file").addEventListener("click", () => {
                allFiles.splice(index, 1);
                renderFileList();
                fileText.textContent = allFiles.length > 0 ? `(${allFiles.length}) files uploaded` : "No file chosen yet.";
            });

            uploadedFilesList.appendChild(li);
        });
    }

    function showProgressUI() {
        uploadFilesContainer.style.display = "none";
        document.querySelector(".uploaded-files").style.display = "none";
        
        const actionsContainer = document.querySelector(".actions");
        if (actionsContainer) {
            actionsContainer.classList.add('uploading');
        }
        
        const progressContainer = document.createElement("div");
        progressContainer.className = "progress-container";
        progressContainer.innerHTML = `
            <div class="progress-header">
                <i class="fa-solid fa-file-arrow-up fa-bounce"></i>
                <h3>Processing Excel Files...</h3>
            </div>
            <div class="progress-stats">
                <span id="progress-percentage">0%</span>
                <span id="progress-eta" class="eta-text">Initializing...</span>
            </div>
            <div class="progress-bar-wrapper">
                <div class="progress-bar" id="progress-bar">
                    <div class="progress-bar-shine"></div>
                </div>
            </div>
            <p class="progress-info">
                <span id="progress-message">Starting upload...</span>
            </p>
            <p class="progress-details">
                Processing <strong><span id="current-row">0</span></strong> of <strong><span id="total-rows">...</span></strong> rows
                <br>
                File <strong><span id="current-file">0</span></strong> of <strong><span id="total-files">...</span></strong>
                <span id="current-filename" class="filename-badge"></span>
            </p>
        `;

        form.appendChild(progressContainer);
    }

    function uploadWithRealTimeProgress(formData) {
        const startTime = Date.now();

        console.log('Step 1: Uploading files to server...');
        
        // STEP 1: Upload files and get session ID
        fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            }
        })
        .then(response => response.json())
        .then(data => {
            console.log('Upload response:', data);
            
            if (data.status === 'error') {
                throw new Error(data.message);
            }
            
            if (data.status !== 'queued') {
                throw new Error('Unexpected response status');
            }

            // STEP 2: Start SSE connection to process uploaded files
            console.log('Step 2: Starting processing with SSE...');
            const processUrl = `/documents/process-upload/${data.session_id}/`;
            
            // Use POST for SSE (some servers handle this better)
            const eventSource = new EventSource(processUrl);
            
            eventSource.onopen = function() {
                console.log('SSE connection established');
            };
            
            eventSource.onmessage = function(event) {
                try {
                    const progressData = JSON.parse(event.data);
                    console.log('Progress update:', progressData);
                    
                    updateProgressFromServer(progressData, startTime);
                    
                    if (progressData.status === 'complete') {
                        console.log('Processing complete!');
                        eventSource.close();
                        showSuccess(progressData.redirect_url);
                    } else if (progressData.status === 'error') {
                        console.error('Processing error:', progressData.message);
                        eventSource.close();
                        showError(progressData.message || "Upload failed. Please try again.");
                    }
                } catch (e) {
                    console.error('Error parsing SSE data:', e, event.data);
                }
            };

            eventSource.onerror = function(error) {
                console.error('SSE connection error:', error);
                eventSource.close();
                showError("Connection lost. Please try again.");
            };
        })
        .catch(error => {
            console.error('Upload error:', error);
            showError(error.message || "Upload failed. Please try again.");
        });
    }

    function updateProgressFromServer(data, startTime) {
        const progressBar = document.getElementById("progress-bar");
        const progressPercentage = document.getElementById("progress-percentage");
        const progressEta = document.getElementById("progress-eta");
        const progressMessage = document.getElementById("progress-message");
        const currentRowSpan = document.getElementById("current-row");
        const totalRowsSpan = document.getElementById("total-rows");
        const currentFileSpan = document.getElementById("current-file");
        const totalFilesSpan = document.getElementById("total-files");
        const currentFilename = document.getElementById("current-filename");

        const percentage = data.percentage || 0;

        // Update progress bar with smooth transition
        if (progressBar) {
            progressBar.style.width = percentage + "%";
        }

        if (progressPercentage) {
            progressPercentage.textContent = percentage.toFixed(1) + "%";
        }

        // Update message
        if (progressMessage && data.message) {
            progressMessage.textContent = data.message;
        }

        // Update row counts
        if (currentRowSpan && data.current_row !== undefined) {
            currentRowSpan.textContent = data.current_row.toLocaleString();
        }
        if (totalRowsSpan && data.total_rows !== undefined) {
            totalRowsSpan.textContent = data.total_rows.toLocaleString();
        }

        // Update file counts
        if (currentFileSpan && data.current_file !== undefined) {
            currentFileSpan.textContent = data.current_file;
        }
        if (totalFilesSpan && data.total_files !== undefined) {
            totalFilesSpan.textContent = data.total_files;
        }

        // Update current filename
        if (currentFilename && data.current_filename) {
            currentFilename.textContent = data.current_filename;
            currentFilename.style.display = 'inline-block';
        }

        // Calculate real ETA based on actual progress
        if (progressEta && percentage > 2 && percentage < 100) {
            const elapsed = Date.now() - startTime;
            const rate = percentage / elapsed;
            const remainingProgress = 100 - percentage;
            const etaMs = remainingProgress / rate;

            if (etaMs > 0 && isFinite(etaMs)) {
                const etaSeconds = Math.ceil(etaMs / 1000);
                if (etaSeconds < 60) {
                    progressEta.textContent = `${etaSeconds}s remaining`;
                } else {
                    const minutes = Math.floor(etaSeconds / 60);
                    const seconds = etaSeconds % 60;
                    progressEta.textContent = `${minutes}m ${seconds}s remaining`;
                }
            } else {
                progressEta.textContent = "Almost done...";
            }
        } else if (progressEta && percentage >= 100) {
            progressEta.textContent = "Complete!";
        } else if (progressEta) {
            progressEta.textContent = "Calculating...";
        }
    }

    function showSuccess(redirectUrl) {
        const progressContainer = document.querySelector(".progress-container");
        if (progressContainer) {
            progressContainer.innerHTML = `
                <div class="progress-success">
                    <i class="fa-solid fa-check-circle"></i>
                    <h3>Upload Complete!</h3>
                    <p>Successfully processed all files. Redirecting...</p>
                </div>
            `;
        }
        
        setTimeout(() => {
            window.location.href = redirectUrl || '/all-documents';
        }, 1500);
    }

    function showError(message) {
        const progressContainer = document.querySelector(".progress-container");
        if (progressContainer) {
            progressContainer.innerHTML = `
                <div class="progress-error">
                    <i class="fa-solid fa-exclamation-circle"></i>
                    <h3>Upload Failed</h3>
                    <p>${message}</p>
                    <button type="button" id="retry-btn">Try Again</button>
                </div>
            `;

            document.getElementById("retry-btn").addEventListener("click", () => {
                resetForm();
            });
        }
    }

    function resetForm() {
        if (eventSource) {
            eventSource.close();
            eventSource = null;
        }
        
        sessionId = null;
        allFiles = [];
        fileInput.value = "";
        
        const progressContainer = document.querySelector(".progress-container");
        if (progressContainer) {
            progressContainer.remove();
        }

        uploadFilesContainer.style.display = "flex";
        document.querySelector(".uploaded-files").style.display = "block";
        
        const actionsContainer = document.querySelector(".actions");
        if (actionsContainer) {
            actionsContainer.classList.remove('uploading');
        }

        renderFileList();
        fileText.textContent = "Only .xlsx and .xls files are allowed.";
    }
});