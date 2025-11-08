// Admin Dashboard JavaScript

// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Toggle sidebar
    const sidebarToggle = document.getElementById('sidebarToggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function(e) {
            e.preventDefault();
            document.getElementById('wrapper').classList.toggle('toggled');
            
            // Save the sidebar state in localStorage
            const isToggled = document.getElementById('wrapper').classList.contains('toggled');
            localStorage.setItem('sidebarToggled', isToggled);
        });
        
        // Check for saved sidebar state
        if (localStorage.getItem('sidebarToggled') === 'true') {
            document.getElementById('wrapper').classList.add('toggled');
        }
    }
    
    // Enable tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Enable popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Handle file input preview
    const fileInputs = document.querySelectorAll('.custom-file-input');
    fileInputs.forEach(function(input) {
        input.addEventListener('change', function(e) {
            const fileName = e.target.files[0] ? e.target.files[0].name : 'Choose file';
            const label = this.nextElementSibling;
            if (label) {
                label.textContent = fileName;
            }
            
            // Preview image if it's an image file
            if (e.target.files && e.target.files[0] && e.target.files[0].type.match('image.*')) {
                const reader = new FileReader();
                const preview = document.getElementById('imagePreview');
                
                if (preview) {
                    reader.onload = function(e) {
                        preview.innerHTML = '<img src="' + e.target.result + '" class="img-fluid mt-2" style="max-height: 200px;">';
                    }
                    
                    reader.readAsDataURL(e.target.files[0]);
                }
            }
        });
    });
    
    // Initialize summernote for rich text editors
    if (typeof $ !== 'undefined' && $.fn.summernote) {
        $('.summernote').summernote({
            height: 300,
            minHeight: null,
            maxHeight: null,
            focus: true,
            toolbar: [
                ['style', ['style']],
                ['font', ['bold', 'italic', 'underline', 'clear']],
                ['fontname', ['fontname']],
                ['color', ['color']],
                ['para', ['ul', 'ol', 'paragraph']],
                ['table', ['table']],
                ['insert', ['link', 'picture', 'video']],
                ['view', ['fullscreen', 'codeview', 'help']]
            ]
        });
    }
    
    // Handle select all checkbox in tables
    const selectAllCheckbox = document.getElementById('selectAll');
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            const checkboxes = document.querySelectorAll('.row-checkbox');
            checkboxes.forEach(function(checkbox) {
                checkbox.checked = selectAllCheckbox.checked;
            });
        });
    }
    
    // Handle bulk actions
    const bulkActionForm = document.getElementById('bulkActionForm');
    const bulkActionSelect = document.getElementById('bulkAction');
    
    if (bulkActionForm && bulkActionSelect) {
        bulkActionSelect.addEventListener('change', function() {
            if (this.value) {
                if (confirm('Are you sure you want to perform this action on the selected items?')) {
                    bulkActionForm.submit();
                } else {
                    this.value = '';
                }
            }
        });
    }
    
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
    
    // Handle dark/light mode toggle
    const darkModeToggle = document.getElementById('darkModeToggle');
    if (darkModeToggle) {
        // Check for saved user preference, if any, on load
        if (localStorage.getItem('darkMode') === 'enabled') {
            document.documentElement.setAttribute('data-bs-theme', 'dark');
            darkModeToggle.checked = true;
        }
        
        darkModeToggle.addEventListener('change', function() {
            if (this.checked) {
                document.documentElement.setAttribute('data-bs-theme', 'dark');
                localStorage.setItem('darkMode', 'enabled');
            } else {
                document.documentElement.removeAttribute('data-bs-theme');
                localStorage.setItem('darkMode', 'disabled');
            }
        });
    }
    
    // Initialize DataTables if available
    if (typeof $ !== 'undefined' && $.fn.DataTable) {
        $('.datatable').DataTable({
            responsive: true,
            pageLength: 25,
            order: [[0, 'desc']],
            dom: '<"d-flex justify-content-between align-items-center mb-3"f<"d-flex align-items-center">>t<"d-flex justify-content-between align-items-center"<"d-flex align-items-center"li>p>',
            language: {
                search: "",
                searchPlaceholder: "Search...",
                lengthMenu: "Show _MENU_ entries",
                info: "Showing _START_ to _END_ of _TOTAL_ entries",
                infoEmpty: "No entries found",
                infoFiltered: "(filtered from _MAX_ total entries)",
                paginate: {
                    first: "First",
                    last: "Last",
                    next: "Next",
                    previous: "Previous"
                }
            }
        });
        
        // Add search icon to search input
        $('.dataTables_filter input').addClass('form-control form-control-sm');
        $('.dataTables_filter label').addClass('d-flex align-items-center');
        $('.dataTables_filter').prepend('<i class="fas fa-search me-2 text-muted"></i>');
    }
    
    // Handle form validation
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        }, false);
    });
    
    // Handle confirm on delete buttons
    const deleteButtons = document.querySelectorAll('.btn-delete');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });
    
    // Initialize flatpickr for date pickers
    if (typeof flatpickr !== 'undefined') {
        flatpickr(".datepicker", {
            dateFormat: "Y-m-d",
            allowInput: true
        });
        
        flatpickr(".datetimepicker", {
            enableTime: true,
            dateFormat: "Y-m-d H:i",
            allowInput: true
        });
    }
    
    // Handle password visibility toggle
    const togglePassword = document.querySelector('.toggle-password');
    if (togglePassword) {
        togglePassword.addEventListener('click', function() {
            const passwordInput = document.querySelector(this.getAttribute('toggle'));
            const icon = this.querySelector('i');
            
            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
            } else {
                passwordInput.type = 'password';
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
            }
        });
    }
});

// Helper function to format dates
function formatDate(dateString) {
    if (!dateString) return '';
    
    const options = { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    
    return new Date(dateString).toLocaleDateString(undefined, options);
}

// Helper function to handle AJAX form submissions
function submitForm(form, callback) {
    const formData = new FormData(form);
    const action = form.getAttribute('action');
    const method = form.getAttribute('method') || 'POST';
    
    fetch(action, {
        method: method,
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (typeof callback === 'function') {
            callback(data);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        if (typeof callback === 'function') {
            callback({ success: false, message: 'An error occurred. Please try again.' });
        }
    });
}

// Helper function to show toast notifications
function showToast(type, message, title = '') {
    const toastContainer = document.getElementById('toastContainer');
    
    if (!toastContainer) return;
    
    const toastId = 'toast-' + Date.now();
    const toast = document.createElement('div');
    toast.id = toastId;
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${title ? `<strong>${title}</strong><br>` : ''}
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    const bsToast = new bootstrap.Toast(toast, {
        autohide: true,
        delay: 5000
    });
    
    bsToast.show();
    
    // Remove toast from DOM after it's hidden
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
    
    return toastId;
}

// Initialize any tooltips that are dynamically added to the page
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Debounce function for performance optimization
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}
