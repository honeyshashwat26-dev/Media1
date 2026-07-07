import http.server
import json
import os

class AVRecordingHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/upload-video':
            content_length = int(self.headers['Content-Length'])
            raw_data = self.rfile.read(content_length)
            
            try:
                boundary = self.headers['Content-Type'].split("=")[1].encode()
                header_end = raw_data.find(b'\r\n\r\n') + 4
                file_end = raw_data.rfind(boundary) - 4
                video_bytes = raw_data[header_end:file_end]
                
                # Saves the uploaded video file right onto the server
                output_filename = "user_recording.webm"
                with open(output_filename, "wb") as f:
                    f.write(video_bytes)
                
                print(f"[+] Success! Saved file as {output_filename}")
                
                self.send_response(200)
                self.send_header('Content-Type', 'text/plain')
                self.end_headers()
                self.wfile.write(b"Video stored successfully.")
                
            except Exception as e:
                print(f"[-] Error parsing video data: {e}")
                self.send_error(500, "Internal Server Error")
        else:
            self.send_error(404, "Not Found")

# Render automatically handles the website's port setup
port = int(os.environ.get("PORT", 8443))
server_address = ('0.0.0.0', port)
httpd = http.server.HTTPServer(server_address, AVRecordingHandler)

print(f"[*] Server running online on port {port}")
httpd.serve_forever()