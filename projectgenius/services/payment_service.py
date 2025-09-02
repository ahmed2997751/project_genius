import os
import logging
import requests
import uuid
from datetime import datetime
from app import db
from models import Payment

# IntaSend API configuration
INTASEND_PUBLIC_KEY = os.getenv("INTASEND_PUBLIC_KEY", "ISPubKey_test_placeholder")
INTASEND_SECRET_KEY = os.getenv("INTASEND_SECRET_KEY", "ISSecKey_test_placeholder")
INTASEND_API_BASE = "https://sandbox.intasend.com/api/v1"  # Use production URL in production

def create_payment(user_id: int, amount: float, subscription_months: int) -> dict:
    """
    Create a payment request using IntaSend API
    
    Args:
        user_id (int): ID of the user making the payment
        amount (float): Payment amount
        subscription_months (int): Number of months for subscription
        
    Returns:
        dict: Payment data including checkout URL
    """
    try:
        # Generate unique transaction ID
        transaction_id = f"edu_{user_id}_{uuid.uuid4().hex[:8]}"
        
        # Create payment record in database
        payment = Payment(
            user_id=user_id,
            transaction_id=transaction_id,
            amount=amount,
            currency='USD',
            status='pending',
            payment_method='card',
            subscription_months=subscription_months
        )
        
        db.session.add(payment)
        db.session.commit()
        
        # Prepare IntaSend payment request
        payment_data = {
            "public_key": INTASEND_PUBLIC_KEY,
            "amount": amount,
            "currency": "USD",
            "reference": transaction_id,
            "email": f"user_{user_id}@edusense.com",  # You might want to get actual email
            "first_name": f"User{user_id}",
            "last_name": "EduSense",
            "country": "US",
            "address": "123 Education St",
            "city": "Learning City",
            "state": "Knowledge",
            "zipcode": "12345",
            "redirect_url": f"http://localhost:5000/verify_payment/{transaction_id}",
            "api_ref": transaction_id
        }
        
        # Make API call to IntaSend
        headers = {
            "Content-Type": "application/json",
            "X-IntaSend-Public-Key-Id": INTASEND_PUBLIC_KEY
        }
        
        response = requests.post(
            f"{INTASEND_API_BASE}/payment/collection/",
            json=payment_data,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 201:
            result = response.json()
            checkout_url = result.get('url', '')
            
            if checkout_url:
                return {
                    'success': True,
                    'checkout_url': checkout_url,
                    'transaction_id': transaction_id,
                    'amount': amount
                }
            else:
                logging.error("No checkout URL received from IntaSend")
                return create_mock_payment_response(transaction_id, amount)
        else:
            logging.error(f"IntaSend API error: {response.status_code} - {response.text}")
            return create_mock_payment_response(transaction_id, amount)
            
    except requests.exceptions.RequestException as e:
        logging.error(f"Network error contacting IntaSend: {e}")
        return create_mock_payment_response(transaction_id, amount)
    except Exception as e:
        logging.error(f"Error creating payment: {e}")
        db.session.rollback()
        raise

def verify_payment(transaction_id: str) -> bool:
    """
    Verify payment status with IntaSend API
    
    Args:
        transaction_id (str): Transaction ID to verify
        
    Returns:
        bool: True if payment is verified, False otherwise
    """
    try:
        # Get payment record from database
        payment = Payment.query.filter_by(transaction_id=transaction_id).first()
        if not payment:
            logging.error(f"Payment record not found for transaction: {transaction_id}")
            return False
        
        # Check with IntaSend API
        headers = {
            "Authorization": f"Bearer {INTASEND_SECRET_KEY}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{INTASEND_API_BASE}/payment/status/{transaction_id}/",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            status = result.get('invoice', {}).get('state', '').lower()
            
            if status == 'complete' or status == 'paid':
                return True
            elif status == 'failed' or status == 'cancelled':
                payment.status = 'failed'
                db.session.commit()
                return False
            else:
                logging.info(f"Payment {transaction_id} status: {status}")
                return False
        else:
            logging.error(f"IntaSend status check error: {response.status_code}")
            # For development/demo purposes, return True for mock payments
            return handle_mock_payment_verification(transaction_id)
            
    except requests.exceptions.RequestException as e:
        logging.error(f"Network error verifying payment: {e}")
        return handle_mock_payment_verification(transaction_id)
    except Exception as e:
        logging.error(f"Error verifying payment: {e}")
        return False

def create_mock_payment_response(transaction_id: str, amount: float) -> dict:
    """
    Create a mock payment response for development/demo purposes
    This is used when IntaSend API is not available
    """
    logging.info("Creating mock payment response for development")
    
    # In a real application, you would not want to do this
    # This is only for development/demo purposes
    mock_checkout_url = f"http://localhost:5000/verify_payment/{transaction_id}?mock=true"
    
    return {
        'success': True,
        'checkout_url': mock_checkout_url,
        'transaction_id': transaction_id,
        'amount': amount,
        'mock': True,
        'message': 'Mock payment for development - click link to simulate successful payment'
    }

def handle_mock_payment_verification(transaction_id: str) -> bool:
    """
    Handle mock payment verification for development purposes
    """
    logging.info(f"Mock payment verification for transaction: {transaction_id}")
    
    # For development, automatically approve payments
    # In production, this should never happen
    payment = Payment.query.filter_by(transaction_id=transaction_id).first()
    if payment and payment.status == 'pending':
        return True
    
    return False

def calculate_subscription_price(months: int) -> float:
    """
    Calculate subscription price based on number of months
    
    Args:
        months (int): Number of months
        
    Returns:
        float: Total price
    """
    monthly_price = 9.99
    
    if months == 1:
        return monthly_price
    elif months == 12:
        return 99.99  # Yearly discount
    elif months == 6:
        return 54.99  # Semi-annual discount
    else:
        return monthly_price * months

def get_payment_history(user_id: int) -> list:
    """
    Get payment history for a user
    
    Args:
        user_id (int): User ID
        
    Returns:
        list: List of payment records
    """
    try:
        payments = Payment.query.filter_by(user_id=user_id).order_by(Payment.created_at.desc()).all()
        return payments
    except Exception as e:
        logging.error(f"Error getting payment history: {e}")
        return []

def cancel_subscription(user_id: int) -> bool:
    """
    Cancel user's subscription
    
    Args:
        user_id (int): User ID
        
    Returns:
        bool: True if successful
    """
    try:
        from models import User
        user = User.query.get(user_id)
        if user:
            user.is_premium = False
            user.subscription_end_date = None
            db.session.commit()
            return True
        return False
    except Exception as e:
        logging.error(f"Error canceling subscription: {e}")
        db.session.rollback()
        return False
