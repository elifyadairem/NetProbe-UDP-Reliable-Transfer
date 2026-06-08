
import socket
import json
import hashlib
import time
import os
import sys
from datetime import datetime

SERVER_ADDRESS = ("127.0.0.1", 5000)

FILE_NAME = "deneme.txt"

CHUNK_SIZE = 1024

TIMEOUT = 1.0

MAX_RETRIES = 5

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

client.settimeout(TIMEOUT)

if hasattr(socket, 'SIO_UDP_CONNRESET'):
    client.ioctl(socket.SIO_UDP_CONNRESET, False)


with open("client_log.txt", "w", encoding="utf-8") as f:
    f.write("time,event,packet,details\n")


def log_event(event_type, packet_seq, details=""):

    current_time = datetime.now().strftime("%H:%M:%S")

    line = f"{current_time},{event_type},{packet_seq}"

    if details:
        line += f",{details}"

    print(line)

    with open("client_log.txt", "a", encoding="utf-8") as log:
        log.write(line + "\n")


def calculate_checksum(data):
    return hashlib.md5(data.encode()).hexdigest()


file_size = os.path.getsize(FILE_NAME)

total_packets = (
    file_size // CHUNK_SIZE
    +
    (1 if file_size % CHUNK_SIZE != 0 else 0)
)

with open(FILE_NAME, "rb") as f:
    file_hash = hashlib.sha256(f.read()).hexdigest()

seq_number = 1

total_retransmissions = 0

rtt_list = []

start_transfer_time = time.time()

with open(FILE_NAME, "rb") as file:

    while True:

        chunk = file.read(CHUNK_SIZE)

        if not chunk:
            break

        packet = {
            "type": "DATA",
            "seq": seq_number,
            "total_packets": total_packets,
            "payload_length": len(chunk),
            "checksum": calculate_checksum(chunk.decode("latin-1")),
            "data": chunk.decode("latin-1")
        }

        packet_bytes = json.dumps(packet).encode()

        ack_received = False

        retry_count = 0

        while not ack_received:

            try:

                send_time = time.time()

                client.sendto(
                    packet_bytes,
                    SERVER_ADDRESS
                )

                if retry_count == 0:

                    log_event(
                        "SEND",
                        seq_number
                    )

                else:

                    total_retransmissions += 1

                    log_event(
                        "RETRANSMIT",
                        seq_number,
                        f"{retry_count}/{MAX_RETRIES}"
                    )

                raw_ack, _ = client.recvfrom(4096)

                ack_packet = json.loads(raw_ack.decode())

                # ACK checksum doğrulama
                received_checksum = ack_packet["checksum"]

                calculated_checksum = calculate_checksum(
                    str(ack_packet["ack"])
                )

                if received_checksum != calculated_checksum:

                    log_event(
                        "ACK_CORRUPTED",
                        seq_number
                    )

                    continue

                if ack_packet["ack"] == seq_number:

                    rtt = time.time() - send_time

                    rtt_list.append(rtt)

                    log_event(
                        "ACK_RECEIVED",
                        seq_number,
                        f"RTT={round(rtt,4)} sn"
                    )

                    ack_received = True

                    seq_number += 1

            except socket.timeout:

                retry_count += 1

                log_event(
                    "TIMEOUT",
                    seq_number,
                    f"{retry_count}/{MAX_RETRIES}"
                )

                if retry_count >= MAX_RETRIES:

                    abort_packet = {
                        "type": "ABORT",
                        "seq": seq_number
                    }

                    client.sendto(
                        json.dumps(abort_packet).encode(),
                        SERVER_ADDRESS
                    )

                    log_event(
                        "TRANSFER_ABORTED",
                        seq_number
                    )

                    client.close()

                    sys.exit()

# END PACKET
end_packet = {
    "type": "END",
    "seq": seq_number,
    "hash": file_hash
}

while True:

    try:

        client.sendto(
            json.dumps(end_packet).encode(),
            SERVER_ADDRESS
        )

        raw_ack, _ = client.recvfrom(4096)

        response = json.loads(raw_ack.decode())

        if response["status"] == "OK":

            log_event(
                "FILE_TRANSFER_SUCCESS",
                "-"
            )

        break

    except:
        continue

end_transfer_time = time.time()

completion_time = (
    end_transfer_time - start_transfer_time
)

average_rtt = (
    sum(rtt_list) / len(rtt_list)
    if rtt_list else 0
)

retransmission_rate = (
    total_retransmissions / total_packets
)

print("\n========== İSTATİSTİKLER ==========")

print(f"Toplam Paket: {total_packets}")

print(f"Retransmission Sayısı: {total_retransmissions}")

print(f"Retransmission Rate: %{round(retransmission_rate*100,2)}")

print(f"Average RTT: {round(average_rtt,4)} sn")

print(f"Completion Time: {round(completion_time,2)} sn")

client.close()

