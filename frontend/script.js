// Configuration
const API_BASE_URL = 'http://localhost:5000/api';

// State
let refreshInterval = null;
let currentConfig = null;

// DOM Elements
const elements = {
    secret: document.getElementById('secret'),
    algorithm: document.getElementById('algorithm'),
    digits: document.getElementById('digits'),
    timeStep: document.getElementById('timeStep'),
    t0: document.getElementById('t0'),
    generateBtn: document.getElementById('generateBtn'),
    generateSecretBtn: document.getElementById('generateSecretBtn'),
    resultSection: document.getElementById('resultSection'),
    otpCode: document.getElementById('otpCode'),
    timeRemaining: document.getElementById('timeRemaining'),
    timerBar: document.getElementById('timerBar'),
    counter: document.getElementById('counter'),
    timestamp: document.getElementById('timestamp'),
    usedAlgorithm: document.getElementById('usedAlgorithm'),
    copyBtn: document.getElementById('copyBtn'),
    autoRefresh: document.getElementById('autoRefresh'),
    verifyBtn: document.getElementById('verifyBtn'),
    verifyOtp: document.getElementById('verifyOtp'),
    verifyResult: document.getElementById('verifyResult'),
    errorToast: document.getElementById('errorToast'),
    errorMessage: document.getElementById('errorMessage')
};

// Event Listeners
elements.generateBtn.addEventListener('click', handleGenerate);
elements.generateSecretBtn.addEventListener('click', handleGenerateSecret);
elements.copyBtn.addEventListener('click', handleCopy);
elements.verifyBtn.addEventListener('click', handleVerify);
elements.autoRefresh.addEventListener('change', handleAutoRefreshToggle);

// Add enter key support for inputs
elements.secret.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') handleGenerate();
});

elements.verifyOtp.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') handleVerify();
});

// Functions
async function handleGenerate() {
    const secret = elements.secret.value.trim();
    
    if (!secret) {
        showError('Please enter a secret key');
        return;
    }
    
    // Add loading state
    elements.generateBtn.disabled = true;
    elements.generateBtn.innerHTML = `
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 12a9 9 0 11-6.219-8.56"></path>
        </svg>
        Generating...
    `;
    
    const config = {
        secret: secret,
        algorithm: elements.algorithm.value,
        digits: parseInt(elements.digits.value),
        time_step: parseInt(elements.timeStep.value),
        t0: parseInt(elements.t0.value)
    };
    
    currentConfig = config;
    
    try {
        console.log('Sending request to:', `${API_BASE_URL}/generate`);
        console.log('Config:', config);
        
        const response = await fetch(`${API_BASE_URL}/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(config)
        });
        
        console.log('Response status:', response.status);
        
        const data = await response.json();
        console.log('Response data:', data);
        
        if (!response.ok) {
            throw new Error(data.error || 'Failed to generate TOTP');
        }
        
        displayResult(data);
        
        if (elements.autoRefresh.checked) {
            startAutoRefresh();
        }
    } catch (error) {
        console.error('Error generating TOTP:', error);
        showError(error.message || 'Failed to connect to backend. Make sure the backend server is running on port 5000.');
    } finally {
        // Reset button
        elements.generateBtn.disabled = false;
        elements.generateBtn.innerHTML = `
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon>
            </svg>
            Generate TOTP Code
        `;
    }
}

async function handleGenerateSecret() {
    elements.generateSecretBtn.disabled = true;
    
    try {
        const response = await fetch(`${API_BASE_URL}/generate-secret`);
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Failed to generate secret');
        }
        
        elements.secret.value = data.secret;
        
        // Add animation to input
        elements.secret.style.animation = 'none';
        setTimeout(() => {
            elements.secret.style.animation = 'fadeIn 0.5s ease-out';
        }, 10);
        
    } catch (error) {
        showError(error.message);
    } finally {
        elements.generateSecretBtn.disabled = false;
    }
}

function displayResult(data) {
    // Animate code change
    elements.otpCode.style.opacity = '0';
    setTimeout(() => {
        elements.otpCode.textContent = data.otp;
        elements.otpCode.style.opacity = '1';
    }, 150);
    
    elements.timeRemaining.textContent = data.time_remaining;
    elements.counter.textContent = data.counter;
    elements.timestamp.textContent = new Date(data.timestamp * 1000).toLocaleString();
    elements.usedAlgorithm.textContent = data.parameters.algorithm.toUpperCase();
    
    // Update timer bar
    const percentage = (data.time_remaining / data.parameters.time_step) * 100;
    elements.timerBar.style.width = `${percentage}%`;
    
    // Update timer bar color based on remaining time
    if (percentage < 20) {
        elements.timerBar.style.background = 'var(--error)';
    } else if (percentage < 40) {
        elements.timerBar.style.background = 'var(--warning)';
    } else {
        elements.timerBar.style.background = 'linear-gradient(90deg, var(--primary) 0%, var(--secondary) 100%)';
    }
    
    // Show result section with animation
    if (elements.resultSection.style.display === 'none') {
        elements.resultSection.style.display = 'block';
        elements.resultSection.style.animation = 'fadeIn 0.5s ease-out';
    }
}

function startAutoRefresh() {
    stopAutoRefresh();
    
    refreshInterval = setInterval(async () => {
        if (currentConfig && elements.autoRefresh.checked) {
            try {
                const response = await fetch(`${API_BASE_URL}/generate`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(currentConfig)
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    displayResult(data);
                }
            } catch (error) {
                console.error('Auto-refresh failed:', error);
            }
        }
    }, 1000);
}

function stopAutoRefresh() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
        refreshInterval = null;
    }
}

function handleAutoRefreshToggle() {
    if (elements.autoRefresh.checked && currentConfig) {
        startAutoRefresh();
    } else {
        stopAutoRefresh();
    }
}

async function handleCopy() {
    const code = elements.otpCode.textContent;
    
    try {
        await navigator.clipboard.writeText(code);
        
        // Update button with success state
        const originalHTML = elements.copyBtn.innerHTML;
        elements.copyBtn.innerHTML = `
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="20 6 9 17 4 12"></polyline>
            </svg>
            Copied!
        `;
        elements.copyBtn.style.background = 'rgba(16, 185, 129, 0.2)';
        elements.copyBtn.style.borderColor = 'rgba(16, 185, 129, 0.5)';
        elements.copyBtn.style.color = 'var(--success)';
        
        setTimeout(() => {
            elements.copyBtn.innerHTML = originalHTML;
            elements.copyBtn.style.background = '';
            elements.copyBtn.style.borderColor = '';
            elements.copyBtn.style.color = '';
        }, 2000);
    } catch (error) {
        showError('Failed to copy to clipboard');
    }
}

async function handleVerify() {
    const secret = elements.secret.value.trim();
    const otp = elements.verifyOtp.value.trim();
    
    if (!secret) {
        showError('Please enter a secret key');
        return;
    }
    
    if (!otp) {
        showError('Please enter an OTP to verify');
        return;
    }
    
    // Add loading state
    elements.verifyBtn.disabled = true;
    
    const config = {
        secret: secret,
        otp: otp,
        algorithm: elements.algorithm.value,
        digits: parseInt(elements.digits.value),
        time_step: parseInt(elements.timeStep.value),
        t0: parseInt(elements.t0.value),
        window: 1
    };
    
    try {
        const response = await fetch(`${API_BASE_URL}/verify`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(config)
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Failed to verify TOTP');
        }
        
        showVerifyResult(data.valid);
    } catch (error) {
        showError(error.message);
    } finally {
        elements.verifyBtn.disabled = false;
    }
}

function showVerifyResult(isValid) {
    elements.verifyResult.style.display = 'flex';
    
    if (isValid) {
        elements.verifyResult.innerHTML = `
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="20 6 9 17 4 12"></polyline>
            </svg>
            Valid TOTP Code
        `;
        elements.verifyResult.className = 'verify-result success';
    } else {
        elements.verifyResult.innerHTML = `
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
            Invalid TOTP Code
        `;
        elements.verifyResult.className = 'verify-result error';
    }
    
    // Add animation
    elements.verifyResult.style.animation = 'fadeIn 0.3s ease-out';
    
    setTimeout(() => {
        elements.verifyResult.style.display = 'none';
    }, 5000);
}

function showError(message) {
    elements.errorMessage.textContent = message;
    elements.errorToast.style.display = 'flex';
    elements.errorToast.style.animation = 'slideInRight 0.3s ease-out';
    
    // Also log to console for debugging
    console.error('Error:', message);
    
    setTimeout(() => {
        elements.errorToast.style.animation = 'slideInRight 0.3s ease-out reverse';
        setTimeout(() => {
            elements.errorToast.style.display = 'none';
        }, 300);
    }, 4000);
}

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    stopAutoRefresh();
});

// Add smooth transitions
elements.otpCode.style.transition = 'opacity 0.15s ease-in-out';