# Localized Trekking & Expedition Management Application

## 📌 Project Overview
This project is a modular, role-based web application designed to streamline operations for adventure organizations, trek organizers, field staff, and participants. The platform modernizes manual workflows by centralizing trek scheduling, managing booking state persistence, enforcing capacity constraints, and maintaining archival records.

## ⚙️ Core Architecture & Requirements
Built strictly under structural constraints utilizing server-side rendering architecture with zero client-side JavaScript execution dependencies for core workflows.

* **Role-Based Access Control (RBAC):** Implemented strict authorization states segregating system actions between Platform Administrators, Field Trek Staff, and Users (Trekkers).
* **State Persistence & Constraints:** Engineered real-time backend validation loops to manage user reservation pipelines and systematically eliminate overbooking anomalies.

## 🛠️ Tech Stack & Mandatory Frameworks

* **Backend Framework:** Flask (Python)
* **Database Object-Relational Mapping:** SQLAlchemy ORM with an SQLite database engine
* **Template Rendering Engine:** Jinja2 
* **Frontend Interface & Layout:** Responsive HTML5, CSS3, and Bootstrap grid mechanics

## 📊 Database Schema & Key Entities
The relational schema uses SQLAlchemy models to map dependencies across core operational structures:
* `User`: Manages authentication metadata, profiling data, and structural RBAC markers.
* `Trek`: Main record tracking location details, structural parameters, difficulty tiers, and scheduling parameters.
* `Booking`: Tracks transaction linkages, participant registries, and operational approval states.
