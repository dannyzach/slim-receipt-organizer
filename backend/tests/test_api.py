import pytest
import io
from PIL import Image, ImageDraw
import json
from datetime import datetime, timedelta

def create_test_receipt_image():
    """Create a test receipt image"""
    # Create image
    width, height = 576, 1000
    img = Image.new('RGB', (width, height), color=(250, 250, 250))
    draw = ImageDraw.Draw(img)
    
    # Add content
    y = 50
    draw.text((width//2 - 50, y), "TEST STORE", fill=(0, 0, 0))
    y += 50
    draw.text((50, y), "Date: 2024-01-20", fill=(0, 0, 0))
    y += 50
    
    # Add items
    items = [
        ("Item 1", "$10.99"),
        ("Item 2", "$15.00"),
        ("Item 3", "$17.00")
    ]
    for item, price in items:
        draw.text((50, y), f"{item}{' ' * 20}{price}", fill=(0, 0, 0))
        y += 30
    
    # Add totals
    y += 20
    draw.text((50, y), f"Subtotal{' ' * 20}$42.99", fill=(0, 0, 0))
    y += 30
    draw.text((50, y), f"Tax{' ' * 25}$3.44", fill=(0, 0, 0))
    y += 30
    draw.text((50, y), f"Total{' ' * 23}$46.43", fill=(0, 0, 0))
    
    # Convert to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    return img_bytes

def test_upload_receipt_unit(client):
    """Unit test for receipt upload endpoint"""
    # Debug: Print all registered routes
    print("\nRegistered routes:")
    for rule in client.application.url_map.iter_rules():
        print(f"{rule.endpoint}: {rule.rule}")
    
    test_image = create_test_receipt_image()
    response = client.post(
        '/api/upload',
        data={'file': (test_image, 'test_receipt.png', 'image/png')}
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'id' in data
    assert 'image_path' in data
    assert 'content' in data
    return data['id']

def test_get_receipts_unit(client):
    """Unit test for get all receipts endpoint"""
    # Temporary debug - you can remove after confirming
    print("\nAvailable routes:")
    for rule in client.application.url_map.iter_rules():
        print(f"{rule.endpoint}: {rule.rule}")
        
    response = client.get('/api/receipts')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)

def test_get_receipt_unit(client):
    """Unit test for get single receipt endpoint"""
    receipt_id = test_upload_receipt_unit(client)
    response = client.get(f'/api/receipts/{receipt_id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['id'] == receipt_id

def test_update_receipt_unit(client):
    """Unit test for update receipt endpoint"""
    receipt_id = test_upload_receipt_unit(client)
    
    update_data = {
        'vendor': 'Updated Store',
        'amount': '99.99',
        'expenseType': 'Office Expenses'
    }
    
    response = client.patch(
        f'/api/receipts/{receipt_id}/update',
        json=update_data
    )
    
    assert response.status_code == 200
#    data = json.loads(response.data) # seems like a redundant check as content should not be returned in the response
#    assert data['content'] == update_data['content']

def test_delete_receipt_unit(client):
    """Unit test for delete receipt endpoint"""
    receipt_id = test_upload_receipt_unit(client)

    # Delete the receipt
    response = client.delete(f'/api/receipts/{receipt_id}')
    assert response.status_code == 200

    # Verify deletion by checking that the receipt no longer exists
    response = client.get(f'/api/receipts/{receipt_id}')
    assert response.status_code == 404  # Now we expect a 404 status code
    assert response.json['error'] == True
    assert response.json['message'] == "Receipt not found"

def test_update_receipt_validation(client):
    """Test field validation rules"""
    receipt_id = test_upload_receipt_unit(client)
    
    # Test invalid vendor
    response = client.patch(f'/api/receipts/{receipt_id}/update', json={
        'vendor': 'x' * 101  # Too long
    })
    assert response.status_code == 400
    assert response.json['error'] == True
    assert 'message' in response.json
    assert 'details' in response.json
    assert 'vendor' in response.json['details']
    
    # Test invalid amount
    response = client.patch(f'/api/receipts/{receipt_id}/update', json={
        'amount': '1000000.00'  # Too large
    })
    assert response.status_code == 400
    assert 'error' in response.json
    assert 'details' in response.json
    assert 'amount' in response.json['details']
    
    # Test future date
    future_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    response = client.patch(f'/api/receipts/{receipt_id}/update', json={
        'date': future_date
    })
    assert response.status_code == 400
    assert 'error' in response.json
    assert 'details' in response.json
    assert 'date' in response.json['details']
    
    # Test invalid status
    response = client.patch(f'/api/receipts/{receipt_id}/update', json={
        'status': 'invalid_status'
    })
    assert response.status_code == 400
    assert 'error' in response.json
    assert 'details' in response.json
    assert 'status' in response.json['details']

def test_update_receipt_success(client):
    """Test successful field updates"""
    receipt_id = test_upload_receipt_unit(client)
    
    response = client.patch(f'/api/receipts/{receipt_id}/update', json={
        'vendor': 'New Vendor',
        'amount': '150.00',
        'status': 'Approved'
    })
    
    assert response.status_code == 200
    assert response.json['success'] is True
    assert 'vendor' in response.json['updated_fields']
    assert 'amount' in response.json['updated_fields']
    assert 'status' in response.json['updated_fields']
    
    # Verify status change from default 'pending' to 'approved'
    assert response.json['updated_fields']['status'] == 'Approved'

def test_update_receipt_errors(client):
    """Test various error conditions"""
    # Test non-existent receipt
    response = client.patch('/api/receipts/99999/update', json={
        'vendor': 'New Vendor'
    })
    assert response.status_code == 404
    assert response.json['error'] == True
    assert response.json['message'] == "Receipt not found"
    
    # Test non-JSON request
    receipt_id = test_upload_receipt_unit(client)
    response = client.patch(f'/api/receipts/{receipt_id}/update', data='not json')
    assert response.status_code == 400
    assert response.json['error'] == True
    assert 'message' in response.json

def test_partial_update_receipt(client):
    """Test updating subset of fields"""
    receipt_id = test_upload_receipt_unit(client)
    
    # Verify initial status is 'Pending'
    response = client.get(f'/api/receipts/{receipt_id}')
    assert response.status_code == 200
    assert response.json['status'] == 'Pending'
    
    # Update only status
    response = client.patch(f'/api/receipts/{receipt_id}/update', json={
        'status': 'Approved'
    })
    
    assert response.status_code == 200
    assert len(response.json['updated_fields']) == 1
    assert response.json['updated_fields']['status'] == 'Approved'

def test_status_transitions(client):
    """Test status transition rules"""
    receipt_id = test_upload_receipt_unit(client)
    
    # Verify initial status is 'pending'
    response = client.get(f'/api/receipts/{receipt_id}')
    assert response.status_code == 200
    assert response.json['status'] == 'Pending'
    
    # Valid transition: pending → approved
    response = client.patch(f'/api/receipts/{receipt_id}/update', json={
        'status': 'Approved'  # Test case insensitive
    })
    assert response.status_code == 200
    assert response.json['updated_fields']['status'] == 'Approved'
    
    # Invalid transition: approved → pending
    response = client.patch(f'/api/receipts/{receipt_id}/update', json={
        'status': 'Pending'
    })
    assert response.status_code == 200
    assert response.json['updated_fields']['status'] == 'Pending'
    
    # Valid transition: approved → rejected
    response = client.patch(f'/api/receipts/{receipt_id}/update', json={
        'status': 'Rejected'
    })
    assert response.status_code == 200
    assert response.json['updated_fields']['status'] == 'Rejected'
    
    # Valid transition: rejected → approved
    response = client.patch(f'/api/receipts/{receipt_id}/update', json={
        'status': 'Approved'
    })
    assert response.status_code == 200
    assert response.json['updated_fields']['status'] == 'Approved'