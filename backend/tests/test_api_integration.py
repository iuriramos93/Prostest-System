import unittest
from flask import Flask
from app import create_app, db
from app.models import User, Titulo, Remessa, Credor, Devedor
from datetime import datetime, timedelta
import json
import os

class ApiIntegrationTestCase(unittest.TestCase):
    def setUp(self):
        """Configuração executada antes de cada teste"""
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()
        
        # Criar dados de teste
        self.setup_test_data()
    
    def tearDown(self):
        """Limpeza executada após cada teste"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def setup_test_data(self):
        """Cria dados de teste no banco"""
        # Criar usuário de teste
        user = User(
            username='testuser',
            email='test@example.com',
            password='password123',
            nome_completo='Usuário de Teste',
            cargo='Tester',
            admin=True
        )
        db.session.add(user)
        
        # Criar credor e devedor
        credor = Credor(
            nome='Banco Teste',
            documento='12345678901234',
            endereco='Rua Teste, 123',
            cidade='São Paulo',
            uf='SP',
            cep='01234-567'
        )
        
        devedor = Devedor(
            nome='Cliente Teste',
            documento='98765432109',
            endereco='Av. Exemplo, 456',
            cidade='Rio de Janeiro',
            uf='RJ',
            cep='21000-000'
        )
        
        db.session.add_all([credor, devedor])
        db.session.commit()
        
        # Criar remessa
        remessa = Remessa(
            nome_arquivo='remessa_teste.xml',
            status='Processado',
            uf='SP',
            tipo='Remessa',
            data_envio=datetime.utcnow(),
            quantidade_titulos=2,
            usuario_id=user.id,
            data_processamento=datetime.utcnow()
        )
        
        db.session.add(remessa)
        db.session.commit()
        
        # Criar títulos
        titulo1 = Titulo(
            numero='TIT001',
            protocolo='PROT001',
            valor=1000.00,
            data_emissao=datetime.utcnow() - timedelta(days=30),
            data_vencimento=datetime.utcnow() + timedelta(days=30),
            status='Pendente',
            remessa_id=remessa.id,
            credor_id=credor.id,
            devedor_id=devedor.id,
            especie='DMI',
            aceite=True,
            nosso_numero='123456'
        )
        
        titulo2 = Titulo(
            numero='TIT002',
            protocolo='PROT002',
            valor=2000.00,
            data_emissao=datetime.utcnow() - timedelta(days=20),
            data_vencimento=datetime.utcnow() + timedelta(days=40),
            status='Protestado',
            remessa_id=remessa.id,
            credor_id=credor.id,
            devedor_id=devedor.id,
            especie='DM',
            aceite=False,
            nosso_numero='654321',
            data_protesto=datetime.utcnow()
        )
        
        db.session.add_all([titulo1, titulo2])
        db.session.commit()
        
        # Salvar IDs para uso nos testes
        self.user_id = user.id
        self.credor_id = credor.id
        self.devedor_id = devedor.id
        self.remessa_id = remessa.id
        self.titulo1_id = titulo1.id
        self.titulo2_id = titulo2.id
        
        # Criar credenciais de autenticação
        self.auth_headers = {
            'Authorization': 'Basic ' + 'testuser:password123'.encode('base64').decode('utf-8')
        }
    
    def test_get_titulos(self):
        """Testa a listagem de títulos"""
        response = self.client.get('/api/v1/titulos', headers=self.auth_headers)
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(len(data['data']['items']), 2)
        self.assertEqual(data['data']['total'], 2)
    
    def test_get_titulo_by_id(self):
        """Testa a obtenção de um título específico"""
        response = self.client.get(f'/api/v1/titulos/{self.titulo1_id}', headers=self.auth_headers)
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['data']['id'], self.titulo1_id)
        self.assertEqual(data['data']['numero'], 'TIT001')
    
    def test_create_titulo(self):
        """Testa a criação de um novo título"""
        new_titulo = {
            'numero': 'TIT003',
            'protocolo': 'PROT003',
            'valor': 3000.00,
            'data_emissao': (datetime.utcnow() - timedelta(days=10)).strftime('%Y-%m-%d'),
            'data_vencimento': (datetime.utcnow() + timedelta(days=50)).strftime('%Y-%m-%d'),
            'credor_id': self.credor_id,
            'devedor_id': self.devedor_id,
            'especie': 'CH',
            'aceite': True,
            'nosso_numero': '789012'
        }
        
        response = self.client.post(
            '/api/v1/titulos',
            data=json.dumps(new_titulo),
            content_type='application/json',
            headers=self.auth_headers
        )
        
        self.assertEqual(response.status_code, 201)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['data']['numero'], 'TIT003')
        self.assertEqual(data['data']['status'], 'Pendente')
    
    def test_update_titulo(self):
        """Testa a atualização de um título existente"""
        update_data = {
            'valor': 1500.00,
            'status': 'Pago'
        }
        
        response = self.client.put(
            f'/api/v1/titulos/{self.titulo1_id}',
            data=json.dumps(update_data),
            content_type='application/json',
            headers=self.auth_headers
        )
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['data']['valor'], 1500.00)
        self.assertEqual(data['data']['status'], 'Pago')
    
    def test_delete_titulo(self):
        """Testa a remoção de um título"""
        response = self.client.delete(f'/api/v1/titulos/{self.titulo1_id}', headers=self.auth_headers)
        self.assertEqual(response.status_code, 200)
        
        # Verificar se o título foi realmente removido
        check_response = self.client.get(f'/api/v1/titulos/{self.titulo1_id}', headers=self.auth_headers)
        self.assertEqual(check_response.status_code, 404)
    
    def test_filter_titulos(self):
        """Testa a filtragem de títulos"""
        response = self.client.get('/api/v1/titulos?status=Protestado', headers=self.auth_headers)
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(len(data['data']['items']), 1)
        self.assertEqual(data['data']['items'][0]['status'], 'Protestado')
    
    def test_validation_errors(self):
        """Testa a validação de dados ao criar um título"""
        invalid_titulo = {
            'numero': 'TIT004',
            'protocolo': 'PROT004',
            'valor': -1000.00,  # Valor negativo, deve falhar na validação
            'data_emissao': (datetime.utcnow() + timedelta(days=10)).strftime('%Y-%m-%d'),  # Data futura
            'data_vencimento': (datetime.utcnow() - timedelta(days=10)).strftime('%Y-%m-%d'),  # Data passada
            'credor_id': self.credor_id,
            'devedor_id': self.devedor_id
        }
        
        response = self.client.post(
            '/api/v1/titulos',
            data=json.dumps(invalid_titulo),
            content_type='application/json',
            headers=self.auth_headers
        )
        
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'error')
        self.assertIn('errors', data)

if __name__ == '__main__':
    unittest.main()
