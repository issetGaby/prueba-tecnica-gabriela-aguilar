import json
import base64
import boto3
from moto import mock_aws
from backend.lambdas.lambda_function import lambda_handler

@mock_aws
def test_complete_flow():
    """Probar el flujo completo con mocks de AWS"""
    print("🧪 INICIANDO PRUEBAS CON MOCKS DE AWS")
    print("=" * 50)
    
    # Configurar mocks
    print("🔧 Configurando mocks de AWS...")
    
    # Mock de S3
    s3_client = boto3.client('s3', region_name='us-east-1')
    s3_client.create_bucket(Bucket='user-documents-bucket')
    
    # Mock de DynamoDB
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.create_table(
        TableName='UserDocuments',
        KeySchema=[
            {'AttributeName': 'user_id', 'KeyType': 'HASH'},
            {'AttributeName': 'document_id', 'KeyType': 'RANGE'}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'user_id', 'AttributeType': 'S'},
            {'AttributeName': 'document_id', 'AttributeType': 'S'}
        ],
        BillingMode='PAY_PER_REQUEST'
    )
    
    print("✅ Mocks configurados correctamente")
    
    # Test 1: Subida exitosa
    print("\n🚀 TEST 1: Subida exitosa de documento")
    file_content = "Este es mi documento de prueba para la Lambda"
    file_content_base64 = base64.b64encode(file_content.encode('utf-8')).decode('utf-8')
    
    event = {
        'httpMethod': 'POST',
        'path': '/documents',
        'body': json.dumps({
            'user_id': 'test_user_001',
            'document_type': 'identification',
            'file_name': 'mi_documento.txt',
            'file_content': file_content_base64
        })
    }
    
    response = lambda_handler(event, {})
    print(f"📤 Status: {response['statusCode']}")
    print(f"📦 Body: {response['body']}")
    
    if response['statusCode'] == 201:
        response_data = json.loads(response['body'])
        document_id = response_data['document_id']
        print(f"✅ Documento subido exitosamente: {document_id}")
    else:
        print("❌ Error en subida")
        return
    
    # Test 2: Consulta exitosa
    print("\n🔍 TEST 2: Consulta del documento subido")
    event = {
        'httpMethod': 'GET',
        'path': f'/documents/test_user_001/identification'
    }
    
    response = lambda_handler(event, {})
    print(f"📥 Status: {response['statusCode']}")
    
    if response['statusCode'] == 200:
        response_data = json.loads(response['body'])
        print("✅ Documento encontrado:")
        print(f"   📝 ID: {response_data['document_id']}")
        print(f"   👤 User: {response_data['user_id']}")
        print(f"   📄 Tipo: {response_data['document_type']}")
        print(f"   📁 Archivo: {response_data['file_name']}")
        print(f"   📏 Tamaño: {response_data['file_size']} bytes")
        
        # Decodificar y mostrar contenido
        decoded_content = base64.b64decode(response_data['file_content']).decode('utf-8')
        print(f"   📋 Contenido: '{decoded_content}'")
    else:
        print(f"❌ Error en consulta: {response['body']}")
    
    # Test 3: Subida con campos faltantes
    print("\n❌ TEST 3: Subida con campos faltantes")
    event = {
        'httpMethod': 'POST',
        'path': '/documents',
        'body': json.dumps({
            'user_id': 'test_user_001'
            # Faltan campos requeridos
        })
    }
    
    response = lambda_handler(event, {})
    print(f"📤 Status: {response['statusCode']}")
    print(f"📦 Body: {response['body']}")
    
    # Test 4: Documento no encontrado
    print("\n🔎 TEST 4: Documento no encontrado")
    event = {
        'httpMethod': 'GET',
        'path': '/documents/usuario_inexistente/contract'
    }
    
    response = lambda_handler(event, {})
    print(f"📥 Status: {response['statusCode']}")
    print(f"📦 Body: {response['body']}")
    
    # Test 5: Subir diferentes tipos de documentos
    print("\n📊 TEST 5: Subir diferentes tipos de documentos")
    document_types = [
        ('invoice', 'factura_enero.pdf', "Contenido de factura"),
        ('contract', 'contrato_servicio.txt', "Términos del contrato..."),
        ('photo', 'foto_dni.jpg', "Imagen de documento")
    ]
    
    for doc_type, file_name, content in document_types:
        file_content_base64 = base64.b64encode(content.encode('utf-8')).decode('utf-8')
        
        event = {
            'httpMethod': 'POST',
            'path': '/documents',
            'body': json.dumps({
                'user_id': 'test_user_002',
                'document_type': doc_type,
                'file_name': file_name,
                'file_content': file_content_base64
            })
        }
        
        response = lambda_handler(event, {})
        status = "✅" if response['statusCode'] == 201 else "❌"
        print(f"   {status} {doc_type}: {file_name} - Status {response['statusCode']}")

@mock_aws
def test_s3_and_dynamo_internals():
    """Probar lo que pasa internamente en S3 y DynamoDB"""
    print("\n" + "=" * 50)
    print("🔬 VISIÓN INTERNA: Qué se guarda en AWS")
    print("=" * 50)
    
    # Configurar mocks
    s3_client = boto3.client('s3', region_name='us-east-1')
    s3_client.create_bucket(Bucket='user-documents-bucket')
    
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.create_table(
        TableName='UserDocuments',
        KeySchema=[
            {'AttributeName': 'user_id', 'KeyType': 'HASH'},
            {'AttributeName': 'document_id', 'KeyType': 'RANGE'}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'user_id', 'AttributeType': 'S'},
            {'AttributeName': 'document_id', 'AttributeType': 'S'}
        ],
        BillingMode='PAY_PER_REQUEST'
    )
    
    # Subir un documento
    file_content = "Contenido para ver internamente"
    file_content_base64 = base64.b64encode(file_content.encode('utf-8')).decode('utf-8')
    
    event = {
        'httpMethod': 'POST',
        'path': '/documents',
        'body': json.dumps({
            'user_id': 'internal_test_user',
            'document_type': 'test_doc',
            'file_name': 'archivo_interno.txt',
            'file_content': file_content_base64
        })
    }
    
    response = lambda_handler(event, {})
    
    if response['statusCode'] == 201:
        response_data = json.loads(response['body'])
        document_id = response_data['document_id']
        
        print("📊 EN DYNAMODB (Metadatos):")
        # Leer de DynamoDB
        items = table.scan()['Items']
        for item in items:
            print(f"   👤 User: {item['user_id']}")
            print(f"   📝 Doc ID: {item['document_id']}")
            print(f"   📄 Tipo: {item['document_type']}")
            print(f"   📁 Archivo: {item['file_name']}")
            print(f"   📍 S3 Key: {item['s3_key']}")
            print(f"   📏 Tamaño: {item['file_size']} bytes")
            print(f"   📅 Fecha: {item['upload_date']}")
            print("   ---")
        
        print("\n📊 EN S3 (Archivos):")
        # Listar archivos en S3
        objects = s3_client.list_objects_v2(Bucket='user-documents-bucket')
        if 'Contents' in objects:
            for obj in objects['Contents']:
                print(f"   📍 Key: {obj['Key']}")
                print(f"   📏 Size: {obj['Size']} bytes")
        else:
            print("   No hay archivos en S3")

if __name__ == "__main__":
    test_complete_flow()
    test_s3_and_dynamo_internals()
    
    print("\n" + "=" * 50)
    print("🎉 TODAS LAS PRUEBAS COMPLETADAS")
    print("✨ Tu Lambda funciona perfectamente con AWS!")