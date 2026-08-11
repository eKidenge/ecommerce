import requests
import base64
import json
from datetime import datetime
from django.conf import settings
from django.core.cache import cache

class MpesaPaymentService:
    """Service class for handling M-Pesa payments"""
    
    def __init__(self):
        self.consumer_key = settings.MPESA_CONSUMER_KEY
        self.consumer_secret = settings.MPESA_CONSUMER_SECRET
        self.passkey = settings.MPESA_PASSKEY
        self.shortcode = settings.MPESA_SHORTCODE
        self.environment = settings.MPESA_ENVIRONMENT
        
        if self.environment == 'production':
            self.base_url = 'https://api.safaricom.co.ke'
        else:
            self.base_url = 'https://sandbox.safaricom.co.ke'
    
    def get_access_token(self):
        """Get M-Pesa access token"""
        # Check cache first
        token = cache.get('mpesa_access_token')
        if token:
            return token
        
        try:
            auth = base64.b64encode(
                f"{self.consumer_key}:{self.consumer_secret}".encode()
            ).decode('utf-8')
            
            response = requests.get(
                f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials",
                headers={
                    'Authorization': f'Basic {auth}',
                    'Content-Type': 'application/json'
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data.get('access_token')
                # Cache for 50 minutes (token expires in 1 hour)
                cache.set('mpesa_access_token', token, 3000)
                return token
            else:
                raise Exception(f"Failed to get M-Pesa token: {response.text}")
                
        except Exception as e:
            raise Exception(f"M-Pesa authentication failed: {str(e)}")
    
    def stk_push(self, phone_number, amount, account_reference, transaction_desc):
        """Initiate STK Push payment"""
        try:
            access_token = self.get_access_token()
            
            # Format phone number
            if phone_number.startswith('0'):
                phone_number = '254' + phone_number[1:]
            elif not phone_number.startswith('254'):
                phone_number = '254' + phone_number
            
            # Get timestamp
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            
            # Generate password
            password_str = f"{self.shortcode}{self.passkey}{timestamp}"
            password = base64.b64encode(password_str.encode()).decode('utf-8')
            
            # Prepare request data
            data = {
                'BusinessShortCode': self.shortcode,
                'Password': password,
                'Timestamp': timestamp,
                'TransactionType': 'CustomerPayBillOnline',
                'Amount': str(int(amount)),
                'PartyA': phone_number,
                'PartyB': self.shortcode,
                'PhoneNumber': phone_number,
                'CallBackURL': f"{settings.BASE_URL}/payment/mpesa/callback/",
                'AccountReference': account_reference[:12],
                'TransactionDesc': transaction_desc[:13]
            }
            
            # Make request
            response = requests.post(
                f"{self.base_url}/mpesa/stkpush/v1/processrequest",
                headers={
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                },
                json=data
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"STK Push failed: {response.text}")
                
        except Exception as e:
            raise Exception(f"M-Pesa payment failed: {str(e)}")
    
    def query_status(self, checkout_request_id):
        """Query M-Pesa payment status"""
        try:
            access_token = self.get_access_token()
            
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            password_str = f"{self.shortcode}{self.passkey}{timestamp}"
            password = base64.b64encode(password_str.encode()).decode('utf-8')
            
            data = {
                'BusinessShortCode': self.shortcode,
                'Password': password,
                'Timestamp': timestamp,
                'CheckoutRequestID': checkout_request_id
            }
            
            response = requests.post(
                f"{self.base_url}/mpesa/stkpushquery/v1/query",
                headers={
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                },
                json=data
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Status query failed: {response.text}")
                
        except Exception as e:
            raise Exception(f"M-Pesa status query failed: {str(e)}")
    
    def process_callback(self, callback_data):
        """Process M-Pesa callback"""
        try:
            # Extract data from callback
            result_code = callback_data.get('ResultCode')
            result_desc = callback_data.get('ResultDesc')
            
            if result_code == '0':
                # Payment successful
                return {
                    'success': True,
                    'result_code': result_code,
                    'result_desc': result_desc,
                    'mpesa_receipt': callback_data.get('MpesaReceiptNumber'),
                    'transaction_date': callback_data.get('TransactionDate'),
                    'phone_number': callback_data.get('PhoneNumber'),
                    'amount': callback_data.get('Amount'),
                }
            else:
                # Payment failed
                return {
                    'success': False,
                    'result_code': result_code,
                    'result_desc': result_desc,
                }
                
        except Exception as e:
            raise Exception(f"Callback processing failed: {str(e)}")