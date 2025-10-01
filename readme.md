# Heart Disease Prediction Web Service

## Overview

This repository contains the complete code for a functional, full-stack machine learning web service I developed to predict the risk of heart disease based on user-provided health inputs.

I deployed the application using **Docker Compose**, structuring it around three main services:

1.  **Frontend:** A modern web application (e.g., React/Vite) that I built to collect user data and display the model's prediction.
2.  **Backend (FastAPI):** A high-performance Python API that I use to host the pre-trained machine learning model and execute the necessary feature engineering.
3.  **Database (PostgreSQL):** I use this database for persistent storage, specifically for auditing and logging every prediction made by the API.

***

## Getting Started

These instructions will guide you through setting up and running my project on your local machine.

### Prerequisites

You must have the following software installed:

* **Git**
* **Docker**
* **Docker Compose**

### Installation

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/RituArora-DevOps/heart-disease-predictor.git
    cd heart-disease-predictor
    ```

2.  **Ensure Artifacts are Present:**
    My project requires a pre-trained model and preprocessor. I've stored these essential files in the `./backend/artifacts` directory:
    * `model.pkl`
    * `preprocessor.pkl`
    * `optimal_threshold.txt`

3.  **Build and Run the Containers:**
    I use the following command to build the Docker images (FastAPI and Nginx/Frontend), create the necessary containers, and start the services in detached mode (`-d`).

    ```bash
    docker compose up --build -d
    ```

### Accessing the Application

Once all containers are running, you can access the application via your browser:

| Service | Access URL |
| :--- | :--- |
| **Frontend (User Interface)** | `http://localhost:[Frontend Port, e.g., 8000 or 5173]` |
| **Backend API (Health Check)** | `http://localhost:[Nginx Port]/api/health` |

***

## Project Architecture

This table summarizes the components I've used in the application stack:

| Component | Technology | Port (Internal) | Role |
| :--- | :--- | :--- | :--- |
| **Frontend** | [e.g., React/Vite] | 80 | Collects data, displays results. |
| **Backend** | **FastAPI** / Uvicorn | 8000 | Model inference, feature engineering, database interaction. |
| **Reverse Proxy** | **Nginx** | 80 | Routes `/api` traffic to the backend, serves frontend static files. |
| **Database** | **PostgreSQL** | 5432 | Stores audit logs (`user_assessments` table). |

### Data Flow

1.  A user submits data through the **Frontend**.
2.  The request is sent to Nginx (`/api/predict`).
3.  **Nginx** forwards the request to the **FastAPI Backend**.
4.  The **FastAPI** application performs feature engineering, runs model inference, logs the result to **PostgreSQL**, and returns the prediction.
5.  The **Frontend** displays the final result to the user.

***

## Development and Debugging

### Database Inspection

To verify that prediction logs are being saved, I connect directly to the running PostgreSQL container:

1.  **Execute into the DB container:**
    ```bash
    docker compose exec db sh
    ```
2.  **Log into PostgreSQL:**
    ```bash
    psql -U user -d heartdb
    ```
3.  **Check the logs table:**
    ```sql
    \dt                               -- List all tables
    SELECT * FROM user_assessments;   -- View the prediction logs
    \q                                -- Exit psql
    exit                              -- Exit container shell
    ```

### Viewing Logs

If I encounter issues, I check the logs for the specific service:

```bash
# View backend (FastAPI) logs
docker compose logs backend

# View reverse proxy (Nginx) logs
docker compose logs frontend