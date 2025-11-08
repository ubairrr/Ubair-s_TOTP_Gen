from flask import Flask, request, jsonify
from flask_cors import CORS
from totp import TOTP
import time

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests

@app.route('/api/generate', methods=['POST'])
def generate_totp():
    """
    Generate TOTP code with custom parameters
    
    Expected JSON body:
    {
        "secret": "BASE32_SECRET_KEY",
        "time_step": 30,  # optional, default: 30
        "t0": 0,          # optional, default: 0
        "digits": 6,      # optional, default: 6
        "algorithm": "sha1"  # optional, default: "sha1", options: sha1, sha256, sha512
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'secret' not in data:
            return jsonify({'error': 'Secret key is required'}), 400
        
        secret = data.get('secret')
        time_step = data.get('time_step', 30)
        t0 = data.get('t0', 0)
        digits = data.get('digits', 6)
        algorithm = data.get('algorithm', 'sha1').lower()
        
        # Validate parameters
        if not isinstance(time_step, int) or time_step <= 0:
            return jsonify({'error': 'Time step must be a positive integer'}), 400
        
        if not isinstance(t0, int):
            return jsonify({'error': 'T0 must be an integer'}), 400
        
        if not isinstance(digits, int) or digits < 6 or digits > 10:
            return jsonify({'error': 'Digits must be between 6 and 10'}), 400
        
        if algorithm not in ['sha1', 'sha256', 'sha512']:
            return jsonify({'error': 'Algorithm must be sha1, sha256, or sha512'}), 400
        
        # Generate TOTP
        totp = TOTP(
            secret=secret,
            time_step=time_step,
            t0=t0,
            digits=digits,
            algorithm=algorithm
        )
        
        result = totp.generate()
        
        return jsonify({
            'success': True,
            'otp': result['otp'],
            'time_remaining': result['time_remaining'],
            'counter': result['counter'],
            'timestamp': result['timestamp'],
            'parameters': {
                'time_step': time_step,
                't0': t0,
                'digits': digits,
                'algorithm': algorithm
            }
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500


@app.route('/api/verify', methods=['POST'])
def verify_totp():
    """
    Verify TOTP code
    
    Expected JSON body:
    {
        "secret": "BASE32_SECRET_KEY",
        "otp": "123456",
        "time_step": 30,  # optional, default: 30
        "t0": 0,          # optional, default: 0
        "digits": 6,      # optional, default: 6
        "algorithm": "sha1",  # optional, default: "sha1"
        "window": 1       # optional, default: 1
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'secret' not in data or 'otp' not in data:
            return jsonify({'error': 'Secret key and OTP are required'}), 400
        
        secret = data.get('secret')
        otp = data.get('otp')
        time_step = data.get('time_step', 30)
        t0 = data.get('t0', 0)
        digits = data.get('digits', 6)
        algorithm = data.get('algorithm', 'sha1').lower()
        window = data.get('window', 1)
        
        # Verify TOTP
        totp = TOTP(
            secret=secret,
            time_step=time_step,
            t0=t0,
            digits=digits,
            algorithm=algorithm
        )
        
        is_valid = totp.verify(otp, window=window)
        
        return jsonify({
            'success': True,
            'valid': is_valid
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500


@app.route('/api/generate-secret', methods=['GET'])
def generate_secret():
    """
    Generate a random base32 secret key
    
    Optional query parameter:
    - length: Length of secret in bytes (default: 32)
    """
    try:
        length = request.args.get('length', default=32, type=int)
        
        if length < 16 or length > 64:
            return jsonify({'error': 'Length must be between 16 and 64'}), 400
        
        secret = TOTP.generate_secret(length)
        
        return jsonify({
            'success': True,
            'secret': secret
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': int(time.time())
    }), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
