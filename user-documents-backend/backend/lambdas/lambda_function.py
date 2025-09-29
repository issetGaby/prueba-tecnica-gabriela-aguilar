import json
import logging
import boto3
import boto3.dynamodb.conditions
from botocore.exceptions import ClientError
import uuid
from datetime import datetime
from decimal import Decimal


# Configurar logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
def convert_decimals(obj):
    """
    Convierte objetos Decimal de DynamoDB a tipos de Python serializables
    """
    if isinstance(obj, list):
        return [convert_decimals(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: convert_decimals(value) for key, value in obj.items()}
    elif hasattr(obj, 'to_eng_string'):  # Es un objeto Decimal
        return float(obj) if '.' in str(obj) else int(obj)
    else:
        return obj
    
def get_dynamodb_table():
    """Obtener la tabla de DynamoDB (lazy initialization)"""
    # Configurar región por defecto si no está establecida
    import os
    if 'AWS_DEFAULT_REGION' not in os.environ:
        os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
    
    dynamodb = boto3.resource('dynamodb')
    return dynamodb.Table('UserDocuments')

def get_s3_client():
    """Obtener cliente de S3 (lazy initialization)"""
    # Configurar región por defecto si no está establecida
    import os
    if 'AWS_DEFAULT_REGION' not in os.environ:
        os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
    
    return boto3.client('s3')

def lambda_handler(event, context):
    """
    Función principal que maneja las requests HTTP
    """
    try:
        logger.info(f"Event received: {json.dumps(event)}")
        
        http_method = event.get('httpMethod')
        path = event.get('path')
        
        if http_method == 'POST' and path == '/documents':
            return upload_document(event)
        elif http_method == 'GET' and path.startswith('/documents/'):
            return get_document(event)
        else:
            return create_response(404, {'error': 'Route not found'})
            
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return create_response(500, {'error': 'Internal server error'})

def create_response(status_code, body):
    """
    Crea una respuesta HTTP estándar
    """
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(body)
    }

def upload_document(event):
    """
    Maneja la subida de documentos (POST /documents)
    """
    try:
        # Parsear el cuerpo de la request
        if 'body' not in event:
            return create_response(400, {'error': 'Missing request body'})
        
        body = event['body']
        if isinstance(body, str):
            try:
                body = json.loads(body)
            except json.JSONDecodeError:
                return create_response(400, {'error': 'Invalid JSON in request body'})
        
        # Validar campos requeridos
        required_fields = ['user_id', 'document_type', 'file_name', 'file_content']
        for field in required_fields:
            if field not in body:
                return create_response(400, {'error': f'Missing required field: {field}'})
        
        user_id = body['user_id']
        document_type = body['document_type']
        file_name = body['file_name']
        file_content = body['file_content']
        
        # Validar tipos de datos
        if not isinstance(user_id, str) or not isinstance(document_type, str) or not isinstance(file_name, str):
            return create_response(400, {'error': 'user_id, document_type and file_name must be strings'})
        
        # Generar ID único para el documento
        document_id = str(uuid.uuid4())
        s3_key = f"{user_id}/{document_type}/{document_id}_{file_name}"
        
        # Decodificar el contenido del archivo (base64)
        try:
            import base64
            file_bytes = base64.b64decode(file_content)
        except Exception:
            return create_response(400, {'error': 'Invalid file_content - must be base64 encoded'})
        
        # Obtener clientes AWS
        s3_client = get_s3_client()
        table = get_dynamodb_table()
        
        # Subir archivo a S3
        s3_bucket = 'user-documents-bucket'
        try:
            s3_client.put_object(
                Bucket=s3_bucket,
                Key=s3_key,
                Body=file_bytes,
                ContentType='application/octet-stream'
            )
            logger.info(f"File uploaded to S3: {s3_key}")
        except ClientError as e:
            logger.error(f"S3 upload error: {str(e)}")
            return create_response(500, {'error': 'Failed to upload file to S3'})
        
        # Guardar metadatos en DynamoDB
        document_item = {
            'document_id': document_id,
            'user_id': user_id,
            'document_type': document_type,
            'file_name': file_name,
            's3_bucket': s3_bucket,
            's3_key': s3_key,
            'upload_date': datetime.utcnow().isoformat(),
            'file_size': len(file_bytes)
        }
        
        try:
            table.put_item(Item=document_item)
            logger.info(f"Metadata saved to DynamoDB for document: {document_id}")
        except ClientError as e:
            logger.error(f"DynamoDB put error: {str(e)}")
            # Intentar eliminar el archivo de S3 si falla DynamoDB
            try:
                s3_client.delete_object(Bucket=s3_bucket, Key=s3_key)
            except ClientError:
                pass
            return create_response(500, {'error': 'Failed to save document metadata'})
        
        # Respuesta exitosa
        response_data = {
            'message': 'Document uploaded successfully',
            'document_id': document_id,
            'user_id': user_id,
            'document_type': document_type,
            'file_name': file_name
        }
        
        return create_response(201, response_data)
        
    except Exception as e:
        logger.error(f"Unexpected error in upload_document: {str(e)}")
        return create_response(500, {'error': 'Internal server error'})

def get_document(event):
    """
    Maneja la consulta de documentos (GET /documents/{user_id}/{document_type})
    """
    try:
        # Extraer user_id y document_type del path
        path = event.get('path', '')
        path_parts = path.split('/')
        
        # El path debería ser: /documents/{user_id}/{document_type}
        if len(path_parts) < 4:
            return create_response(400, {'error': 'Invalid path format. Use /documents/{user_id}/{document_type}'})
        
        user_id = path_parts[2]
        document_type = path_parts[3]
        
        # Validar parámetros
        if not user_id or not document_type:
            return create_response(400, {'error': 'user_id and document_type are required'})
        
        # Obtener clientes AWS
        table = get_dynamodb_table()
        s3_client = get_s3_client()
        
        # Consultar DynamoDB para obtener el documento más reciente
        try:
            response = table.query(
                KeyConditionExpression=boto3.dynamodb.conditions.Key('user_id').eq(user_id),
                FilterExpression=boto3.dynamodb.conditions.Attr('document_type').eq(document_type),
                ScanIndexForward=False,  # Orden descendente (más reciente primero)
                Limit=1
            )
        except ClientError as e:
            logger.error(f"DynamoDB query error: {str(e)}")
            return create_response(500, {'error': 'Failed to query document metadata'})
        
        items = response.get('Items', [])
        if not items:
            return create_response(404, {'error': 'Document not found'})
        
        document_metadata = convert_decimals(items[0])
        s3_bucket = document_metadata['s3_bucket']
        s3_key = document_metadata['s3_key']
        file_name = document_metadata['file_name']
        
        # Descargar archivo de S3
        try:
            s3_response = s3_client.get_object(Bucket=s3_bucket, Key=s3_key)
            file_content = s3_response['Body'].read()
        except ClientError as e:
            logger.error(f"S3 download error: {str(e)}")
            return create_response(500, {'error': 'Failed to download file from S3'})
        
        # Codificar el contenido en base64 para la respuesta
        import base64
        file_content_base64 = base64.b64encode(file_content).decode('utf-8')
        
        # Preparar respuesta
        response_data = {
            'document_id': document_metadata['document_id'],
            'user_id': user_id,
            'document_type': document_type,
            'file_name': file_name,
            'file_content': file_content_base64,
            'upload_date': document_metadata['upload_date'],
            'file_size': document_metadata['file_size']
        }
        
        return create_response(200, response_data)
        
    except Exception as e:
        logger.error(f"Unexpected error in get_document: {str(e)}")
        return create_response(500, {'error': 'Internal server error'})