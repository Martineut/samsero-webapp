// Wait for DOM to be fully loaded before attaching event listeners
document.addEventListener('DOMContentLoaded', function() {
    const contactForm = document.getElementById('contact-form');
    
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Show loading state
            const submitButton = this.querySelector('button[type="submit"]');
            const originalButtonText = submitButton.textContent;
            submitButton.textContent = 'Sending...';
            submitButton.disabled = true;
            
            // Collect form data
            const formData = {
                name: document.getElementById("name").value.trim(),
                email: document.getElementById("email").value.trim(),
                subject: document.getElementById("subject").value,
                deadline: document.getElementById("deadline").value,
                message: document.getElementById("message").value.trim()
            };
            
            // Validate form data
            const emptyFields = Object.entries(formData)
                .filter(([_, value]) => !value)
                .map(([key, _]) => key);
                
            if (emptyFields.length > 0) {
                alert(`Please fill in all the fields. Missing: ${emptyFields.join(', ')}`);
                submitButton.textContent = originalButtonText;
                submitButton.disabled = false;
                return;
            }
            
            // Validate email format
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(formData.email)) {
                alert("Please enter a valid email address.");
                submitButton.textContent = originalButtonText;
                submitButton.disabled = false;
                return;
            }
            
            // Send form data
            fetch('/contact', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData),
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log("Server response:", data);
                if (data.success && data.redirect) {
                    window.location.href = data.redirect;
                } else {
                    alert(data.message || "Unknown error occurred.");
                    submitButton.textContent = originalButtonText;
                    submitButton.disabled = false;
                }
            })
            .catch(error => {
                console.error("Error:", error);
                alert("An error occurred while sending your message. Please try again later.");
                submitButton.textContent = originalButtonText;
                submitButton.disabled = false;
            });
        });
    } else {
        console.error("Contact form element not found!");
    }
});