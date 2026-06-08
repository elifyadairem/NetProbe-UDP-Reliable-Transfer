# NetProbe - UDP Tabanlı Güvenilir Dosya Aktarımı Sistemi

## Proje Hakkında

Bu proje, Bursa Teknik Üniversitesi Bilgisayar Ağları dersi dönem projesi kapsamında geliştirilmiştir.

Projede UDP protokolü üzerinde çalışan güvenilir bir dosya aktarım sistemi geliştirilmiştir. UDP doğası gereği güvenilirlik mekanizmaları içermediğinden; sequence number, ACK, timeout, retransmission ve bütünlük doğrulama gibi mekanizmalar uygulama katmanında gerçeklenmiştir.

Sistem ayrıca:

* trafik izleme,
* olay loglama,
* performans ölçümü,
* deneysel analiz

özelliklerini de içermektedir.

---

# Proje Özellikleri

* UDP tabanlı istemci-sunucu mimarisi
* Güvenilir dosya aktarımı
* Sequence Number mekanizması
* ACK tabanlı doğrulama
* Timeout kontrolü
* Retransmission desteği
* Duplicate packet kontrolü
* SHA256 hash doğrulaması
* Yapay paket kaybı simülasyonu
* ACK düşürme simülasyonu
* Throughput ölçümü
* Goodput ölçümü
* RTT ölçümü
* Retransmission rate analizi
* Grafik üretimi
* Ayrıntılı log sistemi

---

# Kullanılan Teknolojiler

* Python 3
* socket
* hashlib
* json
* matplotlib
* datetime
* time

---

# Proje Dosya Yapısı

```text
project/
│
├── server.py
├── client.py
├── experiment.py
├── generate_files.py
│
├── deneme.txt
├── kucuk.txt
├── orta.txt
├── buyuk.txt
│
├── client_log.txt
├── server_log.txt
│
├── throughput.png
├── goodput.png
├── timeout_test.png
├── loss_goodput.png
├── file_size_test.png
│
├── README.md
└── rapor.pdf
```

---

# Çalıştırma Adımları

## 1. Sunucuyu Başlat

```bash
python server.py
```

---

## 2. İstemciyi Başlat

```bash
python client.py
```

---

## 3. Deneyleri Çalıştır

```bash
python experiment.py
```

---

# Deneyler

Projede aşağıdaki deneyler gerçekleştirilmiştir:

1. Paket Boyutunun Throughput ve Goodput Üzerindeki Etkisi
2. Timeout Süresinin Completion Time Üzerindeki Etkisi
3. Paket Kaybı Oranının Goodput Üzerindeki Etkisi
4. Dosya Boyutunun Completion Time Üzerindeki Etkisi

---

# Güvenilirlik Mekanizmaları

Projede aşağıdaki güvenilirlik mekanizmaları uygulanmıştır:

* Stop-and-Wait yaklaşımı
* Sequence Number
* ACK kontrolü
* Timeout mekanizması
* Retransmission
* Duplicate packet detection
* SHA256 bütünlük doğrulaması

---

# Log Sistemi

İstemci ve sunucu tarafında tüm olaylar zaman damgası ile kayıt altına alınmaktadır.

Örnek olaylar:

* SEND
* ACK_RECEIVED
* TIMEOUT
* RETRANSMIT
* PACKET_DROPPED
* ACK_DROPPED
* TRANSFER_COMPLETE

---

# Performans Metrikleri

Projede aşağıdaki metrikler ölçülmüştür:

* Throughput
* Goodput
* Completion Time
* RTT
* Retransmission Rate

---



# Geliştiriciler

Elif İrem Şahin

Bursa Teknik Üniversitesi
Bilgisayar Mühendisliği Bölümü
