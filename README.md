# Earthquake Road Risk Model

![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=111)
![TypeScript](https://img.shields.io/badge/TypeScript-4.9-3178C6?logo=typescript&logoColor=fff)
![FastAPI](https://img.shields.io/badge/FastAPI-Prototype-009688?logo=fastapi&logoColor=fff)
![Leaflet](https://img.shields.io/badge/Leaflet-GIS_Map-199900?logo=leaflet&logoColor=fff)
![SQLite](https://img.shields.io/badge/SQLite-Local_Data-003B57?logo=sqlite&logoColor=fff)
![License](https://img.shields.io/badge/License-MIT-green)

A GIS prototype for estimating earthquake-driven building collapse risk and likely road blockages in Istanbul using open-source urban data.

## Problem

After a major Istanbul earthquake, damaged or collapsed buildings can block streets, delay emergency access, and reduce the usefulness of evacuation routes. The early idea behind this project was to model that risk at street level by combining building attributes with terrain and ground context.

## Approach

The prototype stores building observations such as floor count, building age, structural material, slope, slope direction, and ground type. The backend calculates a simplified risk score and debris spread area, while the map interface visualizes buildings, assembly areas, debris impact zones, and route risk.

This is a portfolio prototype, not a certified engineering or disaster-response model.

## Features

- Interactive Leaflet map for placing and reviewing buildings
- Building risk scoring based on age, material, floor count, slope, and ground type
- Debris spread estimation for potential street obstruction analysis
- Assembly area markers and route-risk visualization
- FastAPI backend with async SQLAlchemy and local SQLite storage
- React + TypeScript frontend

## Tech Stack

- **Frontend:** React, TypeScript, React Leaflet, Axios
- **Backend:** FastAPI, SQLAlchemy, SQLite
- **Mapping:** OpenStreetMap tiles through Leaflet
- **Data:** Local SQLite database for prototype records

## Repository Status

This repository is prepared for portfolio review. Local databases, environment files, dependency folders, and cache directories are intentionally excluded from version control.

## Local Development

```bash
# Backend
cd backend
uvicorn main:app --reload

# Frontend
cd frontend/deprem-harita
npm install
npm start
```

Create a `.env` file from `.env.example` if you want to override the local database URL.

## License

MIT License. See [LICENSE](LICENSE).
