from flask import Flask, render_template, request, jsonify, url_for, redirect
from flask_mail import Mail, Message
from dotenv import load_dotenv
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Mail configuration from environment
app.config['MAIL_SERVER'] = os.getenv("MAIL_SERVER")
app.config['MAIL_PORT'] = int(os.getenv("MAIL_PORT", 587))
app.config['MAIL_USE_TLS'] = os.getenv("MAIL_USE_TLS", "True").lower() in ("true", "1", "t")
app.config['MAIL_USE_SSL'] = os.getenv("MAIL_USE_SSL", "False").lower() in ("true", "1", "t")
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")
app.config['MAIL_DEFAULT_SENDER'] = os.getenv("MAIL_DEFAULT_SENDER")

# Log mail configuration (without password)
logger.info(f"Mail server: {app.config['MAIL_SERVER']}")
logger.info(f"Mail port: {app.config['MAIL_PORT']}")
logger.info(f"Mail use TLS: {app.config['MAIL_USE_TLS']}")
logger.info(f"Mail use SSL: {app.config['MAIL_USE_SSL']}")
logger.info(f"Mail username: {app.config['MAIL_USERNAME']}")
logger.info(f"Mail default sender: {app.config['MAIL_DEFAULT_SENDER']}")

mail = Mail(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/contact', methods=['POST'])
def contact():
    try:
        data = request.get_json()
        logger.info(f"Received contact form data: {data}")

        required_fields = ['name', 'email', 'subject', 'deadline', 'message']
        if not all(data.get(field) for field in required_fields):
            missing = [f for f in required_fields if not data.get(f)]
            logger.warning(f"Missing required fields: {missing}")
            return jsonify({'success': False, 'message': 'All fields are required.'}), 400

        try:
            msg = Message(
                subject=f"[Contact] {data['subject'].capitalize()}",
                sender=app.config['MAIL_DEFAULT_SENDER'],  # Use configured sender
                recipients=[app.config['MAIL_USERNAME']],
                reply_to=data['email'],  # Set reply-to as the user's email
                body=(
                    f"Name: {data['name']}\n"
                    f"Email: {data['email']}\n"
                    f"Subject Area: {data['subject']}\n"
                    f"Deadline: {data['deadline']}\n\n"
                    f"Message:\n{data['message']}"
                )
            )
            logger.info(f"Attempting to send email to {app.config['MAIL_USERNAME']}")
            mail.send(msg)
            logger.info("Email sent successfully")
            return jsonify({'success': True, 'redirect': url_for("success")})
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}", exc_info=True)
            return jsonify({'success': False, 'message': f'Failed to send email: {str(e)}'}), 500
    except Exception as e:
        logger.error(f"Error processing contact form: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': 'Server error processing your request.'}), 500
    
@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/test-email')
def test_email():
    """Test route to verify email functionality"""
    try:
        msg = Message(
            subject="Test Email",
            sender=app.config['MAIL_DEFAULT_SENDER'],
            recipients=[app.config['MAIL_USERNAME']],
            body="This is a test email to verify that the email functionality is working."
        )
        mail.send(msg)
        return jsonify({'success': True, 'message': 'Test email sent successfully!'})
    except Exception as e:
        logger.error(f"Test email failed: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': f'Test email failed: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)