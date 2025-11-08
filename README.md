# TOTP Generator - RFC 6238 Implementation

A full-stack TOTP (Time-based One-Time Password) generator with customizable parameters based on RFC 6238 specification.

## Features

- ✅ **RFC 6238 Compliant**: Fully compliant implementation of TOTP algorithm
- 🔐 **Multiple Hash Algorithms**: Support for SHA-1, SHA-256, and SHA-512
- ⚙️ **Customizable Parameters**:
  - Time step (X seconds)
  - T0 (Unix epoch start time)
  - OTP length (6-10 digits)
  - Hash algorithm selection
- 🔄 **Auto-refresh**: Automatic TOTP regeneration
- ✓ **Verification**: Verify existing TOTP codes
- 🎲 **Secret Generation**: Generate random Base32 secrets
- 📱 **Responsive Design**: Works on desktop and mobile devices

## Project Structure

```
totp-generator/
├── backend/
│   ├── app.py              # Flask REST API
│   ├── totp.py             # TOTP implementation
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── index.html          # Main HTML file
│   ├── style.css           # Styles
│   └── script.js           # Frontend logic
└── README.md               # Documentation
```

## Installation

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the Flask server:
```bash
python app.py
```

The backend will start on `http://localhost:5000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Open `index.html` in a web browser, or serve it using a simple HTTP server:
```bash
# Using Python
python -m http.server 8000

# Or using Node.js
npx http-server -p 8000
```

3. Access the application at `http://localhost:8000`

## API Documentation

### Endpoints

#### 1. Generate TOTP
**POST** `/api/generate`

Request body:
```json
{
  "secret": "JBSWY3DPEHPK3PXP",
  "time_step": 30,
  "t0": 0,
  "digits": 6,
  "algorithm": "sha1"
}
```

Response:
```json
{
  "success": true,
  "otp": "123456",
  "time_remaining": 25,
  "counter": 12345,
  "timestamp": 1730000000,
  "parameters": {
    "time_step": 30,
    "t0": 0,
    "digits": 6,
    "algorithm": "sha1"
  }
}
```

#### 2. Verify TOTP
**POST** `/api/verify`

Request body:
```json
{
  "secret": "JBSWY3DPEHPK3PXP",
  "otp": "123456",
  "time_step": 30,
  "t0": 0,
  "digits": 6,
  "algorithm": "sha1",
  "window": 1
}
```

Response:
```json
{
  "success": true,
  "valid": true
}
```

#### 3. Generate Secret
**GET** `/api/generate-secret?length=32`

Response:
```json
{
  "success": true,
  "secret": "JBSWY3DPEHPK3PXPJBSWY3DPEHPK3PXP"
}
```

#### 4. Health Check
**GET** `/api/health`

Response:
```json
{
  "status": "healthy",
  "timestamp": 1730000000
}
```

## Usage Example

### Python TOTP Class

```python
from totp import TOTP

# Create TOTP instance
totp = TOTP(
    secret='JBSWY3DPEHPK3PXP',
    time_step=30,
    t0=0,
    digits=6,
    algorithm='sha1'
)

# Generate OTP
result = totp.generate()
print(f"OTP: {result['otp']}")
print(f"Valid for: {result['time_remaining']} seconds")

# Verify OTP
is_valid = totp.verify('123456')
print(f"Valid: {is_valid}")

# Generate random secret
secret = TOTP.generate_secret()
print(f"New secret: {secret}")
```

## Configuration Options

### Time Step
- Default: 30 seconds
- Valid range: 1-300 seconds
- Common values: 30s (Google), 60s (Microsoft)

### T0 (Unix Epoch)
- Default: 0 (January 1, 1970)
- Can be adjusted for custom time synchronization

### Digits
- Options: 6, 7, 8, 9, or 10 digits
- Default: 6 digits
- Most services use 6 digits

### Hash Algorithm
- **SHA-1**: Default, most compatible
- **SHA-256**: More secure, better for new implementations
- **SHA-512**: Highest security, less common

## Security Considerations

1. **Secret Key Storage**: Never store secrets in plain text
2. **HTTPS**: Always use HTTPS in production
3. **Rate Limiting**: Implement rate limiting on verification endpoints
4. **Time Sync**: Ensure server time is synchronized with NTP
5. **Window Size**: Keep verification window small (1-2 steps)

## Testing

Test with known test vectors from RFC 6238:

```python
# SHA-1 test vector
secret = "GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ"
# At timestamp 1111111109, should generate: 050471
# At timestamp 1234567890, should generate: 005924
```

## Troubleshooting

### Backend Issues
- **Port already in use**: Change port in `app.py`
- **Import errors**: Ensure all dependencies are installed
- **CORS errors**: Check CORS configuration in `app.py`

### Frontend Issues
- **API connection failed**: Verify backend is running on port 5000
- **Update API_BASE_URL** in `script.js` if using different host/port

## RFC 6238 Compliance

This implementation follows RFC 6238 specification:
- HOTP algorithm (RFC 4226) as base
- Time-based counter calculation: T = (Current Unix time - T0) / X
- Dynamic truncation
- Support for multiple hash algorithms

## License

MIT License - Feel free to use and modify for your projects.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## References

- [RFC 6238 - TOTP](https://tools.ietf.org/html/rfc6238)
- [RFC 4226 - HOTP](https://tools.ietf.org/html/rfc4226)
