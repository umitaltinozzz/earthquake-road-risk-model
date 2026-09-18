# Earthquake Road Risk Model

**Prototype for modeling earthquake-driven building collapse risk and likely road blockages in Istanbul using open data.**

![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=111&style=for-the-badge)
![TypeScript](https://img.shields.io/badge/TypeScript-4.9-3178C6?logo=typescript&logoColor=fff&style=for-the-badge)
![FastAPI](https://img.shields.io/badge/FastAPI-Prototype-009688?logo=fastapi&logoColor=fff&style=for-the-badge)
![Leaflet](https://img.shields.io/badge/Leaflet-GIS_Map-199900?logo=leaflet&logoColor=fff&style=for-the-badge)
![SQLite](https://img.shields.io/badge/SQLite-Local_Data-003B57?logo=sqlite&logoColor=fff&style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Archived-gray?style=for-the-badge)

---

## Overview

A GIS prototype for estimating earthquake-driven building collapse risk and likely road blockages in Istanbul using open-source urban data.

## Problem

After a major Istanbul earthquake, damaged or collapsed buildings can block streets, delay emergency access, and reduce the usefulness of evacuation routes. The early idea behind this project was to model that risk at street level by combining building attributes with terrain and ground context.

## Approach

The prototype stores building observations such as floor count, building age, structural material, slope, slope direction, and ground type. The backend calculates a simplified risk score and debris spread area, while the map interface visualizes buildings, assembly areas, debris impact zones, and route risk.

## Project Status

Archived portfolio prototype. It is not a certified engineering or disaster-response model; local databases, environment files and dependency folders are excluded from version control.

## Features

- Interactive Leaflet map for placing and reviewing buildings
- Building risk scoring based on age, material, floor count, slope, and ground type
- Debris spread estimation for potential street obstruction analysis
- Assembly area markers and route-risk visualization
- FastAPI backend with async SQLAlchemy and local SQLite storage
- React + TypeScript frontend

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React, TypeScript, React Leaflet, Axios |
| Backend | FastAPI, SQLAlchemy, SQLite |
| Mapping | OpenStreetMap tiles through Leaflet |
| Data | Local SQLite database for prototype records |

## Getting Started

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

## Project Structure

```
earthquake-road-risk-model/
├── backend/
│   ├── types/
├── frontend/
│   ├── deprem-harita/
│   ├── public/
├── LICENSE
├── README.md
├── package-lock.json
├── package.json
├── tsconfig.json
```

## License

[MIT License](./LICENSE)
