import socket
from app import app

def is_port_available(port):
    """Check if a port is available."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('localhost', port))
            return True
        except socket.error:
            return False

def find_available_port(start_port=5000, max_attempts=10):
    """Find an available port starting from start_port."""
    for port in range(start_port, start_port + max_attempts):
        if is_port_available(port):
            return port
    raise RuntimeError(f"No available ports found between {start_port} and {start_port + max_attempts - 1}")

if __name__ == "__main__":
    try:
        # Find an available port
        port = find_available_port()
        
        print("\n=== Starting Local Development Server ===")
        print(f"Website will be available at: http://localhost:{port}")
        print("Press Ctrl+C to stop the server")
        
        # Run the Flask app
        app.run(debug=True, port=port, host='localhost')
        
    except RuntimeError as e:
        print(f"\nError: {e}")
        print("Please make sure no other applications are using the required ports.")
    except Exception as e:
        print(f"\nUnexpected error occurred: {e}")
        print("Please check if Flask is properly installed and app.py exists.")
    except KeyboardInterrupt:
        print("\n\nServer stopped by user. Goodbye!") 