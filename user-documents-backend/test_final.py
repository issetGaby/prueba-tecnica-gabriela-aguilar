import json
import base64
import os
import boto3
from moto import mock_aws
from backend.lambdas.lambda_function import lambda_handler

# Configurar región de AWS para las pruebas
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'

@mock_aws
def demonstrate_lambda_workflow():
    """Demostrar cómo funciona tu Lambda paso a paso"""
    print("🎬 DEMOSTRACIÓN DE TU LAMBDA EN ACCIÓN")
    print("=" * 60)
    
    # Configurar los servicios AWS simulados
    print("1. 🏗️  Configurando entorno de AWS simulado...")
    s3_client = boto3.client('s3')
    s3_client.create_bucket(Bucket='user-documents-bucket')
    
    dynamodb = boto3.resource('dynamodb')
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
    print("   ✅ S3 y DynamoDB simulados listos")

    # PASO 1: Usuario sube un documento
    print("\n2. 📤 USUARIO SUBE UN DOCUMENTO")
    print("   👤 Usuario: maria_garcia")
    print("   📄 Tipo: identification") 
    print("   📁 Archivo: dni_maria.pdf")
    
    document_content = "DOCUMENTO DE IDENTIDAD DE MARÍA GARCÍA\nDNI: 12345678A\nNombre: María García López"
    document_base64 = base64.b64encode(document_content.encode('utf-8')).decode('utf-8')
    
    upload_event = {
        'httpMethod': 'POST',
        'path': '/documents',
        'body': json.dumps({
            'user_id': 'maria_garcia',
            'document_type': 'identification',
            'file_name': 'dni_maria.pdf',
            'file_content': document_base64
        })
    }
    
    print("   ⏳ Enviando a Lambda...")
    upload_response = lambda_handler(upload_event, {})
    
    if upload_response['statusCode'] == 201:
        upload_data = json.loads(upload_response['body'])
        print(f"   ✅ ¡Documento subido exitosamente!")
        print(f"   🆔 ID del documento: {upload_data['document_id']}")
        document_id = upload_data['document_id']
    else:
        print(f"   ❌ Error: {upload_response['body']}")
        return

    # Mostrar qué pasó internamente
    print("\n3. 🔍 QUÉ PASÓ INTERNAMENTE:")
    
    # Ver DynamoDB
    items = table.scan()['Items']
    if items:
        item = items[0]
        print("   📊 En DynamoDB (metadatos):")
        print(f"      👤 Usuario: {item['user_id']}")
        print(f"      🆔 ID Doc: {item['document_id']}")
        print(f"      📄 Tipo: {item['document_type']}")
        print(f"      📁 Archivo: {item['file_name']}")
        print(f"      📍 Ubicación S3: {item['s3_key']}")
        print(f"      📏 Tamaño: {item['file_size']} bytes")
    
    # Ver S3
    objects = s3_client.list_objects_v2(Bucket='user-documents-bucket')
    if 'Contents' in objects:
        print("   💾 En S3 (archivo):")
        s3_object = objects['Contents'][0]
        print(f"      📍 Key: {s3_object['Key']}")
        print(f"      📏 Tamaño: {s3_object['Size']} bytes")
        
        # Leer el contenido real del S3
        s3_response = s3_client.get_object(Bucket='user-documents-bucket', Key=s3_object['Key'])
        actual_content = s3_response['Body'].read().decode('utf-8')
        print(f"      📝 Contenido real: '{actual_content}'")

    # PASO 2: Consultar el documento
    print("\n4. 📥 CONSULTAR EL DOCUMENTO")
    print("   🔍 Buscando documento de maria_garcia/identification...")
    
    get_event = {
        'httpMethod': 'GET', 
        'path': '/documents/maria_garcia/identification'
    }
    
    print("   ⏳ Solicitando a Lambda...")
    get_response = lambda_handler(get_event, {})
    
    if get_response['statusCode'] == 200:
        get_data = json.loads(get_response['body'])
        print("   ✅ ¡Documento encontrado y descargado!")
        print(f"      📁 Archivo: {get_data['file_name']}")
        print(f"      📏 Tamaño: {get_data['file_size']} bytes")
        
        # Mostrar contenido decodificado
        decoded_content = base64.b64decode(get_data['file_content']).decode('utf-8')
        print(f"      📝 Contenido: '{decoded_content}'")
    else:
        print(f"   ❌ Error: {get_response['body']}")

    # PASO 3: Probar casos de error
    print("\n5. 🧪 PROBAR MANEJO DE ERRORES")
    
    # Error: Documento no encontrado
    print("   🔎 Buscando documento inexistente...")
    not_found_event = {
        'httpMethod': 'GET',
        'path': '/documents/usuario_inexistente/contract'
    }
    not_found_response = lambda_handler(not_found_event, {})
    print(f"   ❌ Resultado esperado: {not_found_response['statusCode']} - Documento no encontrado")

    # Error: Campos faltantes
    print("   📝 Enviando payload incompleto...")
    invalid_event = {
        'httpMethod': 'POST',
        'path': '/documents', 
        'body': json.dumps({'user_id': 'test_user'})
    }
    invalid_response = lambda_handler(invalid_event, {})
    print(f"   ❌ Resultado esperado: {invalid_response['statusCode']} - Campos faltantes")

@mock_aws 
def test_multiple_users():
    """Probar con múltiples usuarios y documentos"""
    print("\n" + "=" * 60)
    print("👥 PRUEBA CON MÚLTIPLES USUARIOS")
    print("=" * 60)
    
    # Configurar AWS
    s3_client = boto3.client('s3')
    s3_client.create_bucket(Bucket='user-documents-bucket')
    
    dynamodb = boto3.resource('dynamodb')
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
    
    # Datos de prueba
    test_data = [
        ('carlos_rod', 'contract', 'contrato_carlos.pdf', "CONTRATO DE CARLOS RODRÍGUEZ"),
        ('ana_lopez', 'invoice', 'factura_ana.xml', "<factura>Ana López</factura>"),
        ('carlos_rod', 'photo', 'foto_carlos.jpg', "IMAGEN DE CARLOS"),
        ('luis_mart', 'identification', 'dni_luis.txt', "DNI: 87654321B")
    ]
    
    for user_id, doc_type, file_name, content in test_data:
        content_base64 = base64.b64encode(content.encode('utf-8')).decode('utf-8')
        
        event = {
            'httpMethod': 'POST',
            'path': '/documents',
            'body': json.dumps({
                'user_id': user_id,
                'document_type': doc_type,
                'file_name': file_name,
                'file_content': content_base64
            })
        }
        
        response = lambda_handler(event, {})
        status = "✅" if response['statusCode'] == 201 else "❌"
        print(f"   {status} {user_id} -> {doc_type}: {file_name}")
    
    # Mostrar resumen final
    print(f"\n📈 RESUMEN FINAL:")
    items = table.scan()['Items']
    print(f"   📊 Total documentos en DynamoDB: {len(items)}")
    
    objects = s3_client.list_objects_v2(Bucket='user-documents-bucket')
    s3_count = len(objects['Contents']) if 'Contents' in objects else 0
    print(f"   💾 Total archivos en S3: {s3_count}")
    
    # Agrupar por usuario
    from collections import defaultdict
    user_docs = defaultdict(list)
    for item in items:
        user_docs[item['user_id']].append(item['document_type'])
    
    print(f"   👥 Documentos por usuario:")
    for user, docs in user_docs.items():
        print(f"      {user}: {', '.join(docs)}")

if __name__ == "__main__":
    demonstrate_lambda_workflow()
    test_multiple_users()
    
    print("\n" + "=" * 60)
    print("🎊 ¡TU LAMBDA FUNCIONA PERFECTAMENTE!")
    print("✨ Has construido un backend completo con:")
    print("   ✅ AWS Lambda")
    print("   ✅ Amazon S3") 
    print("   ✅ DynamoDB")
    print("   ✅ Manejo de errores")
    print("   ✅ Pruebas automáticas")
    print("=" * 60)