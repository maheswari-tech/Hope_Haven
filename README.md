# 🍱 HopeHaven – Smart Food Donation Platform

HopeHaven is a community-driven food donation platform that connects donors ( to donate excess food from celebrations and functions like weddings, corporate gatherings) with nearby orphanages and old-age homes using AI-powered matching and live routing. Built with Streamlit (frontend chatbot) and FastAPI (backend API), the system ensures smart matching, and timely food delivery.

---

## 🌟 Features

- 🧠 **Smart Chatbot**: Interacts with users to collect donation details.
- 📍 **Location Matching**: Finds nearby orphanages using geolocation and current needs.
- 🧮 **Resident-Based Matching**: Matches donations with orphanages based on resident count.
- 🗺️ **Live Routing**: Suggests Google Maps links with travel distance and ETA using OpenRouteService.
- ⏰ **Delivery-Aware Filtering**: Avoids routing to homes closed during late hours.
- 📱 **WhatsApp Contact**: Provides contact links to communicate with orphanages directly.

---

## 🏗️ Tech Stack

| Component      | Tech Used                  |
|----------------|----------------------------|
| Frontend Chatbot | [Streamlit](https://streamlit.io) |
| Backend API    | [FastAPI](https://fastapi.tiangolo.com) |
| Geocoding      | Nominatim / OpenStreetMap  |
| Routing API    | [OpenRouteService](https://openrouteservice.org/) |
| Map Link       | Google Maps URL Integration |
| Dataset        | Custom JSON (Orphanages)   |

---
