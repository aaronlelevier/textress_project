alert_messages = {
    'no_twilio_phone_number_alert': "Click here to purchase a phone number in order to send SMS",
    'no_funds_alert': "SMS sending and receiving has been deactivated. Please \
contact your system admin to reactivate the account. This is most likely due to insufficient funds.",
    'no_customer_alert': "No account funds. Click the link to add initial funds and avoid the \
account being deactivated."
}

dj_messages = {
    # Admin
    'delete_admin_fail': "Cannot delete Hotel Admin record.",
    # Contact
    'coming_soon': "Thank you for your interest. We'll be in touch when we get closer to launch!",
    'contact_thanks': "Thank you for contacting us.  We look forward to speaking with you.",
    'contact_not_sent': "Contact email not sent, please check the errors below",
    'hotel_updated': "Hotel info successfully updated",
    'profile_updated': "Profile info successfully updated",
    # Hotel
    'no_hotel': "No Hotel associated with this account.",
    'hotel_not_active': "The Hotel associated with this account is not active.",
    # Payment
    'payment_success': "Payment of ${amount:.2f} successfully processed. Email \
confirmation sent to {email}",
    'payment_fail': "Payment failure, please check your payment method or contact \
{support_email} for further assistance.",
    'complete_registration': "Please complete registration in order to active your account"
    }

login_messages = {
    'now_logged_in': 'You are now logged in',
    'now_logged_out': 'You are now logged out',
    'no_match': 'Please check username and password',
    'no_register': 'Please use a valid username, email, and password',
    'not_active': "Your account hasn't been activated. Please check your email in order \
to activate your account.",
    'activate_via_email': 'Please check your email in order to activate your account.',
    'account_active': 'Your account has been successfully activated. Please Login.',
    'username_taken': 'Username already taken',
    'email_taken': 'Email already taken.',
    'invalid_username': 'Invalid Username',
    'no_email_match': 'No account matching that email.',
    'no_username_match': 'Username misspelled or not registered. Please try again.',
    'login_error': 'Login unsuccessful. Please try again.',
    'passwords_dont_match': 'Passwords do not match',
    'password_has_reset': 'Your password has been reset. You are now logged in.',
    'reset_pw_sent': 'Temporary password sent. Please check your email.',
    'hotel_not_found': "The Hotel that you were trying to reach could not be found. \
Please contact their main phone number. Thank you."
    }

sms_messages = {
    "limit_reached": "Daily text message limit reached. Please try again tomorrow.",
    "sent": "SMS message successfully sent.",
    "send_failed": "SMS failed to send. Please check that is a valid U.S. phone number.",
    "enter_valid_ph": "Please enter a valid phone number."
}
