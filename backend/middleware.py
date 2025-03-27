from flask import request, jsonify
from functools import wraps
import time
from collections import defaultdict
from config import Config

# Simple in-memory rate limiting
class RateLimiter:
    def __init__(self):
        self.requests = defaultdict(list)
    
    def is_rate_limited(self, ip: str, limit: int = 100, window: int = 60) -> bool:
        current_time = time.time()
        # Clean old requests
        self.requests[ip] = [req_time for req_time in self.requests[ip] 
                           if current_time - req_time < window]
        
        # Check if rate limit is exceeded
        if len(self.requests[ip]) >= limit:
            return True
            
        # Add current request
        self.requests[ip].append(current_time)
        return False

rate_limiter = RateLimiter()

def rate_limit(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        ip = request.remote_addr
        if rate_limiter.is_rate_limited(ip):
            return jsonify({"error": "Rate limit exceeded"}), 429
        return f(*args, **kwargs)
    return decorated_function

def add_security_headers(response):
    """
    Add security headers to the response
    """
    for header, value in Config.SECURITY_HEADERS.items():
        response.headers[header] = value
    return response

def validate_request_data(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 400
            
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        return f(*args, **kwargs)
    return decorated_function 