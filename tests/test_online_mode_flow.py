import json
import pytest
from app_flask import app

def test_health_endpoint():
    client = app.test_client()
    resp = client.get('/health')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data.get('status') == 'healthy'


def test_process_quantities_with_assumed_values():
    client = app.test_client()

    # Build minimal project data similar to /quantity-filling
    work_items = [
        {'item_no': '1', 'description': 'Item 1', 'unit': 'Nos', 'Rate': 100.0},
        {'item_no': '2', 'description': 'Item 2', 'unit': 'Nos', 'Rate': 200.0},
    ]
    title_data = {
        'Name of Work': 'Test Work',
        'Agreement No.': 'AGR/TEST/001',
        'Reference to work order or Agreement': 'WO/TEST/001'
    }
    project = {
        'title_data': title_data,
        'work_order_data': work_items,
        'bill_quantity_data': [],
        'extra_items_data': []
    }

    form_data = {
        'project_data': json.dumps(project),
        'quantity_0': '5',  # assume quantities
        'rate_0': '100',
        'quantity_1': '3',
        'rate_1': '200'
    }

    resp = client.post('/process-quantities', data=form_data)
    assert resp.status_code == 200, resp.data
    data = resp.get_json()
    assert data.get('success') is True
    assert 'download_url' in data
