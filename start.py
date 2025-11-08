#!/usr/bin/env python3
"""
TOTP Generator Application Launcher
Place this file in the totp-generator/ directory
Starts both backend and frontend servers
"""

import os
import sys
import subprocess
import time
import signal
import platform

# Global process list to track running servers
processes = []


def is_port_in_use(port):
    """Check if a port is already in use"""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0


def get_python_command():
    """Get the appropriate Python command for the system"""
    # Try python3 first, then python
    try:
        subprocess.run(['python3', '--version'], 
                      capture_output=True, check=True)
        return 'python3'
    except (subprocess.CalledProcessError, FileNotFoundError):
        try:
            subprocess.run(['python', '--version'], 
                          capture_output=True, check=True)
            return 'python'
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Error: Python is not installed or not in PATH")
            sys.exit(1)


def check_project_structure():
    """Verify that we're in the correct directory"""
    backend_exists = os.path.exists('backend') and os.path.isdir('backend')
    frontend_exists = os.path.exists('frontend') and os.path.isdir('frontend')
    
    if not backend_exists or not frontend_exists:
        print("Error: This script must be run from the totp-generator/ directory!")
        print("\nExpected structure:")
        print("totp-generator/")
        print("├── start.py       ← You are here")
        print("├── backend/")
        print("└── frontend/")
        return False
    
    return True



def start_backend():
    """Start the Flask backend server"""
    app_file = os.path.join('backend', 'app.py')
    
    if not os.path.exists(app_file):
        print(f"Error: {app_file} not found!")
        return None
    
    print("\n" + "="*60)
    print("Starting Backend Server...")
    print("="*60)
    
    # Check if port 5000 is already in use
    if is_port_in_use(5000):
        print("⚠ Warning: Port 5000 is already in use!")
        print("Backend server may already be running or port is occupied.")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            return None
    
    python_cmd = get_python_command()
    
    try:
        # Start backend process
        if platform.system() == 'Windows':
            # On Windows, use CREATE_NEW_PROCESS_GROUP
            process = subprocess.Popen(
                [python_cmd, 'app.py'],
                cwd='backend',
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            )
        else:
            # On Unix-like systems
            process = subprocess.Popen(
                [python_cmd, 'app.py'],
                cwd='backend',
                preexec_fn=os.setsid
            )
        
        print(f"✓ Backend server started (PID: {process.pid})")
        print(f"✓ Backend running at: http://localhost:5000")
        print(f"✓ API endpoints: http://localhost:5000/api/*")
        
        return process
        
    except Exception as e:
        print(f"✗ Failed to start backend: {e}")
        return None


def start_frontend():
    """Start the frontend HTTP server"""
    index_file = os.path.join('frontend', 'index.html')
    
    if not os.path.exists(index_file):
        print(f"Error: {index_file} not found!")
        return None
    
    print("\n" + "="*60)
    print("Starting Frontend Server...")
    print("="*60)
    
    # Check if port 8000 is already in use
    if is_port_in_use(8000):
        print("⚠ Warning: Port 8000 is already in use!")
        print("Frontend server may already be running or port is occupied.")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            return None
    
    python_cmd = get_python_command()
    
    try:
        # Start frontend HTTP server
        if platform.system() == 'Windows':
            process = subprocess.Popen(
                [python_cmd, '-m', 'http.server', '8000'],
                cwd='frontend',
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        else:
            process = subprocess.Popen(
                [python_cmd, '-m', 'http.server', '8000'],
                cwd='frontend',
                preexec_fn=os.setsid,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        
        print(f"✓ Frontend server started (PID: {process.pid})")
        print(f"✓ Frontend running at: http://localhost:8000")
        
        return process
        
    except Exception as e:
        print(f"✗ Failed to start frontend: {e}")
        return None


def cleanup(signum=None, frame=None):
    """Clean up and terminate all processes"""
    print("\n\n" + "="*60)
    print("Shutting down servers...")
    print("="*60)
    
    for process in processes:
        if process and process.poll() is None:
            try:
                if platform.system() == 'Windows':
                    # On Windows, send CTRL_BREAK_EVENT
                    process.send_signal(signal.CTRL_BREAK_EVENT)
                else:
                    # On Unix-like systems, kill the process group
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                
                # Wait for process to terminate
                process.wait(timeout=5)
                print(f"✓ Process {process.pid} terminated")
            except subprocess.TimeoutExpired:
                # Force kill if it doesn't terminate gracefully
                if platform.system() == 'Windows':
                    process.kill()
                else:
                    os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                print(f"✓ Process {process.pid} force killed")
            except Exception as e:
                print(f"✗ Error terminating process {process.pid}: {e}")
    
    print("\n✓ All servers stopped.")
    sys.exit(0)


def open_browser():
    """Attempt to open the browser automatically"""
    import webbrowser
    try:
        print("\nOpening browser...")
        webbrowser.open('http://localhost:8000')
    except Exception as e:
        print(f"Could not open browser automatically: {e}")


def main():
    """Main entry point"""
    print("="*60)
    print("TOTP Generator - Application Launcher")
    print("="*60)
    
    # Verify project structure
    print("\nVerifying project structure...")
    if not check_project_structure():
        sys.exit(1)
    print("✓ Project structure valid")
    
    # Register signal handlers for cleanup
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)
    
    # Start backend
    backend_process = start_backend()
    if backend_process:
        processes.append(backend_process)
        # Wait a bit for backend to start
        time.sleep(2)
    else:
        print("\n✗ Failed to start backend server!")
        sys.exit(1)
    
    # Start frontend
    frontend_process = start_frontend()
    if frontend_process:
        processes.append(frontend_process)
        # Wait a bit for frontend to start
        time.sleep(1)
    else:
        print("\n✗ Failed to start frontend server!")
        cleanup()
        sys.exit(1)
    
    # Display success message
    print("\n" + "="*60)
    print("✓ All servers started successfully!")
    print("="*60)
    print("\n🌐 Application URLs:")
    print("   Frontend:  http://localhost:8000")
    print("   Backend:   http://localhost:5000")
    print("   API Health: http://localhost:5000/api/health")
    print("\n📝 Instructions:")
    print("   1. Open http://localhost:8000 in your browser")
    print("   2. Press Ctrl+C here to stop all servers")
    print("="*60 + "\n")
    
    # Open browser automatically (no prompt)
    open_browser()
    
    print("\n⏳ Servers running... Press Ctrl+C to stop\n")
    
    # Keep the script running
    try:
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            for i, process in enumerate(processes):
                if process.poll() is not None:
                    server_name = "Backend" if i == 0 else "Frontend"
                    print(f"\n✗ {server_name} server stopped unexpectedly!")
                    cleanup()
                    sys.exit(1)
                    
    except KeyboardInterrupt:
        cleanup()


if __name__ == "__main__":
    main()
