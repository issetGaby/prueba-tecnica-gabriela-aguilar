import json
import base64
from backend.lambdas.lambda_function import lambda_handler

def test_upload_document():
    """Probar la subida de un documento"""
    print("🚀 Probando SUBIDA de documento...")
    
    # Crear contenido de archivo de prueba
    file_content = "Este es mi documento de prueba para la Lambda"
    file_content_base64 = base64.b64encode(file_content.encode('utf-8')).decode('utf-8')
    
    # Simular evento POST
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
    
    context = {}  # Contexto vacío para pruebas
    
    # Ejecutar la Lambda
    response = lambda_handler(event, context)
    
    print(f"📤 Response Status: {response['statusCode']}")
    print(f"📦 Response Body: {response['body']}")
    
    # Guardar el document_id para la prueba de consulta
    if response['statusCode'] == 201:
        response_data = json.loads(response['body'])
        return response_data['document_id']
    return None

def test_get_document(document_id):
    """Probar la consulta de un documento"""
    print(f"\n🔍 Probando CONSULTA de documento {document_id}...")
    
    # Simular evento GET
    event = {
        'httpMethod': 'GET',
        'path': '/documents/test_user_001/identification'
    }
    
    context = {}
    
    # Ejecutar la Lambda
    response = lambda_handler(event, context)
    
    print(f"📥 Response Status: {response['statusCode']}")
    
    if response['statusCode'] == 200:
        response_data = json.loads(response['body'])
        print(f"✅ Documento encontrado:")
        print(f"   User ID: {response_data['user_id']}")
        print(f"   Tipo: {response_data['document_type']}")
        print(f"   Nombre: {response_data['file_name']}")
        print(f"   Tamaño: {response_data['file_size']} bytes")
        
        # Decodificar el contenido
        file_content = base64.b64decode(response_data['file_content']).decode('utf-8')
        print(f"   Contenido: '{file_content}'")
    else:
        print(f"❌ Error: {response['body']}")

def test_invalid_upload():
    """Probar subida inválida"""
    print(f"\n❌ Probando SUBIDA INVÁLIDA...")
    
    event = {
        'httpMethod': 'POST',
        'path': '/documents',
        'body': json.dumps({
            'user_id': 'test_user_001'
            # Faltan campos requeridos
        })
    }
    
    context = {}
    response = lambda_handler(event, context)
    
    print(f"📤 Response Status: {response['statusCode']}")
    print(f"📦 Response Body: {response['body']}")

def test_document_not_found():
    """Probar documento no encontrado"""
    print(f"\n🔎 Probando DOCUMENTO NO ENCONTRADO...")
    
    event = {
        'httpMethod': 'GET',
        'path': '/documents/usuario_inexistente/contract'
    }
    
    context = {}
    response = lambda_handler(event, context)
    
    print(f"📥 Response Status: {response['statusCode']}")
    print(f"📦 Response Body: {response['body']}")

if __name__ == "__main__":
    print("🧪 INICIANDO PRUEBAS INTERACTIVAS DE LA LAMBDA")
    print("=" * 50)
    
    # Probar subida válida
    document_id = test_upload_document()
    
    if document_id:
        # Probar consulta del documento subido
        test_get_document(document_id)
    
    # Probar casos de error
    test_invalid_upload()
    test_document_not_found()
    
    print("\n" + "=" * 50)
    print("🎉 PRUEBAS COMPLETADAS")