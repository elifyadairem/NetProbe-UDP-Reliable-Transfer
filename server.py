
import socket
import json
import random
import hashlib
from datetime import datetime

SERVER_IP = "0.0.0.0"
SERVER_PORT = 5000
BUFFER_SIZE = 65535

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind((SERVER_IP, SERVER_PORT))

OUTPUT_FILE = "gelen_dosya.txt"

with open("server_log.txt", "w", encoding="utf-8") as f:
    f.write("time,event,packet,details\n")


def log_event(event_type, packet_seq, details=""):
    current_time = datetime.now().strftime("%H:%M:%S")

    line = f"{current_time},{event_type},{packet_seq}"

    if details:
        line += f",{details}"

    print(line)

    with open("server_log.txt", "a", encoding="utf-8") as log:
        log.write(line + "\n")


def calculate_checksum(data):
    return hashlib.md5(data.encode()).hexdigest()


print("UDP Güvenilir Dosya Aktarım Sunucusu Başladı")
print("-" * 50)

while True:

    raw_data, addr = server.recvfrom(BUFFER_SIZE)

    try:
        packet = json.loads(raw_data.decode("utf-8"))
    except:
        continue

    log_event("NEW_TRANSFER", "-", f"{addr}")

    expected_seq = 1

    successful_packets = 0
    duplicate_packets = 0
    dropped_packets = 0

    with open(OUTPUT_FILE, "wb") as file:

        while True:

            packet_type = packet.get("type")

            loss_rate = packet.get("loss_rate", 0.20)

            # Yapay paket kaybı
            if random.random() < loss_rate:
                dropped_packets += 1

                log_event(
                    "PACKET_DROPPED",
                    packet.get("seq", "?"),
                    f"Loss Rate %{int(loss_rate*100)}"
                )

                raw_data, addr = server.recvfrom(BUFFER_SIZE)
                packet = json.loads(raw_data.decode("utf-8"))
                continue

            # ABORT
            if packet_type == "ABORT":

                log_event(
                    "TRANSFER_ABORTED",
                    packet["seq"],
                    "İstemci transferi iptal etti."
                )

                break

            # END
            if packet_type == "END":

                log_event(
                    "END_PACKET",
                    packet["seq"],
                    "Dosya sonu paketi alındı."
                )

                client_hash = packet["hash"]

                file.flush()

                with open(OUTPUT_FILE, "rb") as f:
                    server_hash = hashlib.sha256(f.read()).hexdigest()

                if client_hash == server_hash:

                    response = {
                        "type": "FINAL_ACK",
                        "ack": packet["seq"],
                        "status": "OK",
                        "checksum": calculate_checksum(str(packet["seq"]))
                    }

                    log_event(
                        "HASH_OK",
                        packet["seq"],
                        server_hash
                    )

                else:

                    response = {
                        "type": "FINAL_ACK",
                        "ack": packet["seq"],
                        "status": "HASH_ERROR",
                        "checksum": calculate_checksum(str(packet["seq"]))
                    }

                    log_event(
                        "HASH_ERROR",
                        packet["seq"],
                        f"{server_hash} != {client_hash}"
                    )

                server.sendto(
                    json.dumps(response).encode(),
                    addr
                )

                log_event(
                    "TRANSFER_COMPLETE",
                    "-",
                    f"Başarılı={successful_packets}, Duplicate={duplicate_packets}, Dropped={dropped_packets}"
                )

                print("-" * 50)

                break

            # DATA
            if packet_type == "DATA":

                current_seq = packet["seq"]

                # Duplicate kontrolü
                if current_seq < expected_seq:

                    duplicate_packets += 1

                    log_event(
                        "DUPLICATE_PACKET",
                        current_seq
                    )

                    ack_packet = {
                        "type": "ACK",
                        "ack": current_seq,
                        "checksum": calculate_checksum(str(current_seq))
                    }

                    server.sendto(
                        json.dumps(ack_packet).encode(),
                        addr
                    )

                elif current_seq == expected_seq:

                    successful_packets += 1

                    payload = packet["data"].encode("latin-1")

                    file.write(payload)

                    log_event(
                        "PACKET_RECEIVED",
                        f"{current_seq}/{packet['total_packets']}"
                    )

                    # ACK düşürme simülasyonu
                    if random.random() < 0.50:

                        log_event(
                            "ACK_DROPPED",
                            current_seq
                        )

                    else:

                        ack_packet = {
                            "type": "ACK",
                            "ack": current_seq,
                            "checksum": calculate_checksum(str(current_seq))
                        }

                        server.sendto(
                            json.dumps(ack_packet).encode(),
                            addr
                        )

                        log_event(
                            "ACK_SENT",
                            current_seq
                        )

                    expected_seq += 1

            raw_data, addr = server.recvfrom(BUFFER_SIZE)
            packet = json.loads(raw_data.decode("utf-8"))

