#!/usr/bin/env python3
"""
Simple HTTP server to generate LiveKit access tokens for the web client.
This makes testing easier by providing tokens via HTTP instead of manual copy/paste.
"""
import os
from dotenv import load_dotenv
from livekit import api
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from urllib.parse import urlparse, parse_qs

# Load environment variables
load_dotenv(".env.local")
load_dotenv()


class TokenHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests for token generation"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/token':
            # Parse query parameters
            params = parse_qs(parsed_path.query)
            room_name = params.get('room', ['voice-room'])[0]
            participant_name = params.get('identity', ['test-user'])[0]
            
            try:
                # Generate token
                api_key = os.getenv("LIVEKIT_API_KEY")
                api_secret = os.getenv("LIVEKIT_API_SECRET")
                
                if not api_key or not api_secret:
                    raise ValueError("LIVEKIT_API_KEY and LIVEKIT_API_SECRET must be set")
                
                token = api.AccessToken(api_key, api_secret) \
                    .with_identity(participant_name) \
                    .with_name(participant_name) \
                    .with_grants(api.VideoGrants(
                        room_join=True,
                        room=room_name,
                        can_publish=True,
                        can_subscribe=True,
                    ))
                
                # Send response
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = {
                    'token': token.to_jwt(),
                    'url': os.getenv('LIVEKIT_URL', 'ws://127.0.0.1:7880')
                }
                self.wfile.write(json.dumps(response).encode())
                
                print(f"✅ Generated token for {participant_name} joining {room_name}")
                
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode())
                print(f"❌ Error: {e}")
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Suppress default logging"""
        pass


if __name__ == '__main__':
    PORT = 8081
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, TokenHandler)
    
    print(f"\n🚀 Token server running on http://localhost:{PORT}")
    print(f"   Generate tokens at: http://localhost:{PORT}/token?room=voice-room&identity=test-user")
    print(f"\n   Press Ctrl+C to stop\n")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 Token server stopped")
        httpd.server_close()
