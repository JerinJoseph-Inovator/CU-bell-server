# 🔔 Christ University IoT Bell – Backend Service

This project is the **backend** component of the **IoT-based university bell system** deployed at Christ University. Built using **Flask** and hosted on a **Raspberry Pi**, it integrates **hardware control (via GPIO)** with **REST APIs** to automate bell schedules, emergency alerts, and display event data in real time.

---

## 🚀 Project Overview

The bell system allows:
- Automated scheduling of bells for **holidays**, **mid-semesters**, and **end-semesters**
- Immediate relay activation for **emergency alerts**
- Dynamic updates via JSON-based APIs
- A REST endpoint to **serve event data from CSV** for frontend UI
- Secure local deployment with **self-signed SSL**

---

## 🛠️ Tech Stack

- **Python 3**
- **Flask** (with CORS)
- **RPi.GPIO** for hardware relay control
- **Pandas** for CSV/XLSX file handling
- **Raspberry Pi** (BCM pin configuration)
- **Self-signed certificates** for HTTPS

---

## 🧠 Key Features

| Feature         | Endpoint             | Description |
|----------------|----------------------|-------------|
| Holiday Config | `/holiday`           | Log and store holiday events |
| Midsem Bell    | `/midsem`            | Mid-semester bell triggers |
| Endsem Bell    | `/endsem`            | End-semester bell triggers |
| Emergency Bell | `/emergency`         | Immediately activates relay for emergencies |
| Bell Schedule  | `/schedule`          | Triggers bell after X minutes (delayed run) |
| Event Display  | `/display`           | Returns bell events in structured JSON |
| Health Check   | `/`                  | Confirms server is running |

---

## 📁 Project Structure (Snapshot)

```
.
├── app.py                  # Flask backend with GPIO control
├── bell_events.csv         # Event log (used in /display)
├── bell.py, ghantiya.py    # Additional control logic
├── input.txt               # Log file for inputs
├── processing.py           # Input processing logic
├── selfsigned.pem/key     # SSL certificates
├── run_script.sh           # Boot/startup script
├── Schedulefinal.py        # External scheduling logic
├── README.md               # You are here!
```

---

## 🔐 SSL Setup

For HTTPS support on local Raspberry Pi:
```bash
openssl req -x509 -newkey rsa:4096 -keyout selfsigned.key -out selfsigned.pem -days 365 -nodes
```
Ensure both `.pem` and `.key` files are present for `ssl_context` in `app.py`.

---

## 🧪 Example Payloads

### 📅 Holiday Payload
```json
{
  "mode": "0",
  "date": "01/06/2025"
}
```

### 📚 Midsem Payload
```json
{
  "mode": "1",
  "slot": "B",
  "start date": "01/06/2025",
  "end date": "05/06/2025",
  "start_time": "10:00:00"
}
```

### 🚨 Emergency Trigger
```json
{}
```

---

## ✅ Deployment

On the Raspberry Pi:
```bash
python3 app.py
```
Or make executable:
```bash
chmod +x run_script.sh
./run_script.sh
```

---

## 🌐 Access

Once deployed, the backend will be available at:
```
https://<your-pi-ip>:5000/
```

---

## 🙋 Author

Developed by **Jerin Joseph Alour**  
🔗 [jerin.cloud](https://jerin.cloud)

---

## 📌 Notes

- This project includes sensitive keys and logs. Ensure `.gitignore` is properly configured.
- Designed for intranet usage with basic SSL; consider hardened certs if exposed publicly.
- GPIO pin 4 (BCM) is used to trigger the bell relay.

---

## 🏁 Future Improvements

- JWT/Token-based access control
- Schedule visualization dashboard
- Mobile notification for emergency trigger
