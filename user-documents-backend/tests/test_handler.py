import json
import base64
import pytest
import sys
import os
from moto import mock_aws
import boto3

# Añadir el directorio raíz al path de Python
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.lambdas.lambda_function import lambda_handler, upload_document, get_document, create_response

@pytest.fixture
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    import os
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

@pytest.fixture
def dynamodb_mock(aws_credentials):
    """Mock DynamoDB resource."""
    with mock_aws():
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        
        # Crear tabla de DynamoDB
        table = dynamodb.create_table(
            TableName='UserDocuments',
            KeySchema=[
                {
                    'AttributeName': 'user_id',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'document_id',
                    'KeyType': 'RANGE'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'user_id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'document_id',
                    'AttributeType': 'S'
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        
        yield table

@pytest.fixture
def s3_mock(aws_credentials):
    """Mock S3 resource."""
    with mock_aws():
        s3 = boto3.client('s3', region_name='us-east-1')
        
        # Crear bucket de S3
        s3.create_bucket(Bucket='user-documents-bucket')
        
        yield s3

def test_upload_document_valid(s3_mock, dynamodb_mock):
    """Test upload de documento válido."""
    # Preparar evento de prueba
    file_content = "Este es el contenido de mi documento de prueba"
    file_content_base64 = base64.b64encode(file_content.encode('utf-8')).decode('utf-8')
    
    event = {
        'httpMethod': 'POST',
        'path': '/documents',
        'body': json.dumps({
            'user_id': 'user123',
            'document_type': 'identification',
            'file_name': 'test_document.txt',
            'file_content': file_content_base64
        })
    }
    
    context = {}  # Contexto vacío para pruebas
    
    # Ejecutar la función Lambda
    response = lambda_handler(event, context)
    
    # Verificar respuesta
    assert response['statusCode'] == 201
    response_body = json.loads(response['body'])
    assert response_body['message'] == 'Document uploaded successfully'
    assert 'document_id' in response_body
    assert response_body['user_id'] == 'user123'
    assert response_body['document_type'] == 'identification'

def test_upload_document_invalid_payload():
    """Test upload con payload inválido."""
    event = {
        'httpMethod': 'POST',
        'path': '/documents',
        'body': 'invalid json'
    }
    
    context = {}
    
    response = lambda_handler(event, context)
    
    assert response['statusCode'] == 400
    response_body = json.loads(response['body'])
    assert 'error' in response_body

def test_upload_document_missing_fields():
    """Test upload con campos faltantes."""
    event = {
        'httpMethod': 'POST',
        'path': '/documents',
        'body': json.dumps({
            'user_id': 'user123'
            # Faltan otros campos requeridos
        })
    }
    
    context = {}
    
    response = lambda_handler(event, context)
    
    assert response['statusCode'] == 400
    response_body = json.loads(response['body'])
    assert 'error' in response_body

def test_get_document_existing(s3_mock, dynamodb_mock):
    """Test consulta de documento existente."""
    # Primero subir un documento
    file_content = "Contenido del documento para consulta"
    file_content_base64 = base64.b64encode(file_content.encode('utf-8')).decode('utf-8')
    
    upload_event = {
        'httpMethod': 'POST',
        'path': '/documents',
        'body': json.dumps({
            'user_id': 'user456',
            'document_type': 'contract',
            'file_name': 'contract.pdf',
            'file_content': file_content_base64
        })
    }
    
    context = {}
    
    # Subir documento primero
    upload_response = lambda_handler(upload_event, context)
    assert upload_response['statusCode'] == 201
    
    # Ahora consultar el documento
    get_event = {
        'httpMethod': 'GET',
        'path': '/documents/user456/contract'
    }
    
    get_response = lambda_handler(get_event, context)
    
    # Verificar respuesta
    assert get_response['statusCode'] == 200
    response_body = json.loads(get_response['body'])
    assert response_body['user_id'] == 'user456'
    assert response_body['document_type'] == 'contract'
    assert response_body['file_name'] == 'contract.pdf'
    assert 'file_content' in response_body

def test_get_document_not_found(s3_mock, dynamodb_mock):
    """Test consulta de documento inexistente."""
    event = {
        'httpMethod': 'GET',
        'path': '/documents/nonexistent/user/invoice'
    }
    
    context = {}
    
    response = lambda_handler(event, context)
    
    assert response['statusCode'] == 404
    response_body = json.loads(response['body'])
    assert 'error' in response_body
    assert 'not found' in response_body['error'].lower()

def test_invalid_route():
    """Test para ruta no válida."""
    event = {
        'httpMethod': 'PUT',  # Método no soportado
        'path': '/invalid'
    }
    
    context = {}
    
    response = lambda_handler(event, context)
    
    assert response['statusCode'] == 404
    response_body = json.loads(response['body'])
    assert 'error' in response_body