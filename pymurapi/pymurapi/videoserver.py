#!/bin/env python3

import io
import os
import logging
import time

import socketserver
import http.server
import threading
import subprocess

import cv2
import numpy

HELP="""
This library can stream OpenCV images to MUR IDE. Usage:

    import pymurapi as mur
    auv = mur.mur_init()
    mur_view = auv.get_videoserver()
    ...
    mur_view.show(opencv_image, 0)
    # put your image and number of video output (0 or 1)
    ...
    mur_view.stop()
"""

PAGE="""
<html>
    <head>
    <title>Cameras</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {padding: 0 !important; margin:0 !important;}
    </style>
</head>
<body>
<center>
    <img src="/cam_0.mjpg" width="640" height="480">
    <img src="/cam_1.mjpg" width="640" height="480">
</center>
</body>
</html>
"""

DEMO_TEXT = (
    "[0] Hello from OpenCV!",
    "[1] It works",
)

GST_PIPE=('gst-launch-1.0 -v souphttpsrc location="http://127.0.0.1:8002/cam_{0}.mjpg" retries=0 keep-alive=true do-timestamp=true is_live=true timeout=0 !'
        'multipartdemux ! jpegdec ! videoconvert ! videorate ! video/x-raw,format=YUY2,framerate=10/1 ! jpegenc quality=20 ! rtpjpegpay ! udpsink async=true send-duplicates=false sync=false host={1} port=500{0}')

blank_img = numpy.zeros((480,640,3), dtype=numpy.uint8)

class VideoServer:
    _streams = list()
    _gst_threads = list()
    _gst_processes = list()
    _target_host = '127.0.0.1'

    _main_server = None
    _main_thread = threading.Thread()

    class StreamingOutput(object):
        def __init__(self):
            self.frame = None
            self.buffer = io.BytesIO()
            self.condition = threading.Condition()

        def write(self, buf):
            if buf.startswith(b'\xff\xd8'):
                self.buffer.truncate()
                self.buffer.write(buf)
                with self.condition:
                    self.frame = self.buffer.getvalue()
                    self.condition.notify_all()
                self.buffer.seek(0)

    class StreamingHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/':
                self.send_response(301)
                self.send_header('Location', '/index.html')
                self.end_headers()
            elif self.path == '/index.html':
                content = PAGE.encode('utf-8')
                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.send_header('Content-Length', len(content))
                self.end_headers()
                self.wfile.write(content)
            elif self.path.startswith('/cam_') and self.path.endswith('.mjpg') and self.path[5:6].isnumeric():
                cam_index = int(self.path[5:6])
                self.send_response(200)
                self.send_header('Age', 0)
                self.send_header('Cache-Control', 'no-cache, private')
                self.send_header('Pragma', 'no-cache')
                self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
                self.end_headers()
                try:
                    while True:
                        output = self.server.streams[cam_index]
                        with output.condition:
                            output.condition.wait()
                            frame = output.frame
                        self.wfile.write(b'--FRAME\r\n')
                        self.send_header('Content-Type', 'image/jpeg')
                        self.send_header('Content-Length', len(frame))
                        self.end_headers()
                        self.wfile.write(frame)
                        self.wfile.write(b'\r\n')
                except Exception as e:
                    logging.warning(
                        'Removed streaming client %s: %s',
                        self.client_address, str(e))
            else:
                self.send_error(404)
                self.end_headers()

        def log_message(self, format, *args):
            pass

    class StreamingServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
        allow_reuse_address = True
        daemon_threads = True

    def _init_server(self, streams_count, address):
        self._streams = list(self.StreamingOutput() for i in range(streams_count))

        try:
            self._main_server = self.StreamingServer(address, self.StreamingHandler)
            self._main_server.streams = self._streams
            self._main_server.serve_forever()
        except Exception as e:
            print(e)

    def _init_gstreamer(self, stream_index):
        proc = subprocess.Popen([GST_PIPE.format(stream_index, self._target_host)], stdout=subprocess.PIPE, shell=True)
        self._gst_processes.append(proc)

    def __init__(self, streams_count=2, host=None):
        address=('', 8002)

        if host is None:
            print("ERROR: empty host in VideoServer")
            return

        self._target_host = host

        print("VideoStream to", self._target_host)

        self._main_thread = threading.Thread(target=self._init_server, args=(streams_count,address))
        self._main_thread.start()

        for stream_index in range(streams_count):
            self._gst_threads.append(threading.Thread(target=self._init_gstreamer, args=(stream_index,)))
            self._gst_threads[stream_index].start()

        time.sleep(1.5)

        self.show(blank_img, 0)
        self.show(blank_img, 1)

    def stop(self):
        for gst_proc in self._gst_processes:
            gst_proc.stdout.close()
            gst_proc.terminate()
            gst_proc.kill()

        for gst in self._gst_threads:
            gst.join()

        self._main_server.shutdown()

    def show(self, img, index=0, quality=70):
        encode_param=[int(cv2.IMWRITE_JPEG_QUALITY), quality]
        ok, jpg_img = cv2.imencode(".jpg", img, encode_param)

        if ok:
            self._streams[index].write(bytearray(jpg_img))

    def demo(self):
        font = cv2.FONT_HERSHEY_PLAIN
        for i in range(2):
            img = blank_img.copy()
            cv2.putText(img,DEMO_TEXT[i],(5,50), font, 3,(255,255,255),2,cv2.LINE_AA)
            self.show(img, i)

if __name__ == '__main__':
    print(HELP)

    v = VideoServer(host="192.168.1.0")
    v.demo()
    v.stop()

