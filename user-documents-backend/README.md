# User Documents Backend - AWS Lambda

Un backend serverless para manejo de documentos de usuarios usando AWS Lambda, S3 y DynamoDB, operando dentro de una VPC privada con VPC Endpoints.

## 🚀 Características

- **POST /documents**: Subir documentos a S3 y guardar metadata en DynamoDB
- **GET /documents/{user_id}/{document_type}**: Consultar documentos por usuario y tipo
- **Arquitectura serverless** dentro de VPC privada (solo VPC Endpoints, sin NAT Gateway)
- **Pruebas unitarias completas** con mocks de AWS
- **Manejo de errores** robusto y logging
- **Múltiples usuarios** y tipos de documento soportados

## 📋 Prerrequisitos

- Python 3.11
- pip (gestor de paquetes de Python)
- Git

## 🛠️ Instalación y Configuración

1. **Clonar el repositorio:**
   ```bash
   git clone <tu-repositorio>
   cd user-documents-backend