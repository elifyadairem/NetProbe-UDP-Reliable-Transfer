
import socket
import json
import hashlib
import time
import matplotlib.pyplot as plt

SERVER_ADDRESS = ("127.0.0.1", 5000)

FILES = [
    "kucuk.txt",
    "orta.txt",
    "buyuk.txt"
]

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

if hasattr(socket, 'SIO_UDP_CONNRESET'):
    client.ioctl(socket.SIO_UDP_CONNRESET, False)


def run_experiment(
        file_name,
        chunk_size,
        timeout_val,
        loss_rate
):

    client.settimeout(timeout_val)

    with open(file_name, "rb") as f:
        file_content = f.read()

    file_size = len(file_content)

    file_hash = hashlib.sha256(file_content).hexdigest()

    total_packets = (
        file_size // chunk_size
        +
        (1 if file_size % chunk_size != 0 else 0)
    )

    pointer = 0

    seq_number = 1

    retransmissions = 0

    total_bytes_sent = 0

    start_time = time.time()

    while pointer < file_size:

        chunk = file_content[
            pointer:pointer+chunk_size
        ]

        packet = {
            "type": "DATA",
            "seq": seq_number,
            "total_packets": total_packets,
            "payload_length": len(chunk),
            "data": chunk.decode("latin-1"),
            "loss_rate": loss_rate
        }

        packet_bytes = json.dumps(packet).encode()

        ack_received = False

        retry_count = 0

        while not ack_received and retry_count < 5:

            try:

                client.sendto(
                    packet_bytes,
                    SERVER_ADDRESS
                )

                total_bytes_sent += len(packet_bytes)

                raw_ack, _ = client.recvfrom(4096)

                ack = json.loads(raw_ack.decode())

                if ack["ack"] == seq_number:

                    ack_received = True

                    seq_number += 1

            except:

                retry_count += 1

                retransmissions += 1

        pointer += chunk_size

    end_packet = {
        "type": "END",
        "seq": seq_number,
        "hash": file_hash,
        "loss_rate": loss_rate
    }

    try:

        client.sendto(
            json.dumps(end_packet).encode(),
            SERVER_ADDRESS
        )

        client.recvfrom(4096)

    except:
        pass

    elapsed = time.time() - start_time

    throughput = total_bytes_sent / elapsed

    goodput = file_size / elapsed

    retransmission_rate = (
        retransmissions / total_packets
    )

    return (
        throughput,
        goodput,
        elapsed,
        retransmission_rate
    )


# DENEY 1
sizes = [512, 1024, 2048, 4096]

throughputs = []

goodputs = []

for s in sizes:

    tp, gp, _, _ = run_experiment(
        "buyuk.txt",
        s,
        1.0,
        0.20
    )

    throughputs.append(tp)

    goodputs.append(gp)

plt.figure()

plt.plot(sizes, throughputs, marker='o')

plt.title("Paket Boyutu vs Throughput")

plt.xlabel("Paket Boyutu")

plt.ylabel("Throughput")

plt.grid(True)

plt.savefig("throughput.png")

plt.figure()

plt.plot(sizes, goodputs, marker='o')

plt.title("Paket Boyutu vs Goodput")

plt.xlabel("Paket Boyutu")

plt.ylabel("Goodput")

plt.grid(True)

plt.savefig("goodput.png")


# DENEY 2
timeouts = [0.5, 1.0, 2.0]

completion_times = []

for t in timeouts:

    _, _, elapsed, _ = run_experiment(
        "buyuk.txt",
        1024,
        t,
        0.20
    )

    completion_times.append(elapsed)

plt.figure()

plt.bar(
    [str(x) for x in timeouts],
    completion_times
)

plt.title("Timeout vs Completion Time")

plt.xlabel("Timeout")

plt.ylabel("Completion Time")

plt.grid(True)

plt.savefig("timeout_test.png")


# DENEY 3
losses = [0.0, 0.10, 0.20, 0.30]

loss_goodputs = []

for l in losses:

    _, gp, _, _ = run_experiment(
        "buyuk.txt",
        1024,
        1.0,
        l
    )

    loss_goodputs.append(gp)

plt.figure()

plt.plot(
    [int(x*100) for x in losses],
    loss_goodputs,
    marker='o'
)

plt.title("Loss Rate vs Goodput")

plt.xlabel("Loss Rate (%)")

plt.ylabel("Goodput")

plt.grid(True)

plt.savefig("loss_goodput.png")


# DENEY 4
file_sizes = []

completion_results = []

for file in FILES:

    size = len(open(file, "rb").read())

    file_sizes.append(size)

    _, _, elapsed, _ = run_experiment(
        file,
        1024,
        1.0,
        0.20
    )

    completion_results.append(elapsed)

plt.figure()

plt.plot(
    file_sizes,
    completion_results,
    marker='o'
)

plt.title("Dosya Boyutu vs Completion Time")

plt.xlabel("Dosya Boyutu (Byte)")

plt.ylabel("Completion Time")

plt.grid(True)

plt.savefig("file_size_test.png")

print("\nTüm deneyler tamamlandı.")

client.close()

