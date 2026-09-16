def test_read_assets_empty(client):
    response = client.get("/api/v1/assets/")
    assert response.status_code == 200
    assert response.json() == []

def test_create_asset(client):
    asset_data = {
        "asset_number": "TEST-001",
        "name": "Test Asset",
        "category_id": None,
        "location_id": None,
        "status": "ปกติ",
        "purchase_date": None,
        "purchase_price": 1000.0,
        "supplier": "Test Supplier",
        "serial_number": "SN-001",
        "description": "A test asset"
    }
    response = client.post("/api/v1/assets/", json=asset_data)
    assert response.status_code == 200
    data = response.json()
    assert data["asset_number"] == "TEST-001"
    assert data["name"] == "Test Asset"
    assert "qr_code_id" in data
    
    # Test reading the created asset
    response = client.get("/api/v1/assets/")
    assert response.status_code == 200
    assets = response.json()
    assert len(assets) == 1
    assert assets[0]["asset_number"] == "TEST-001"

def test_create_duplicate_asset(client):
    asset_data = {
        "asset_number": "TEST-002",
        "name": "Test Asset 2",
    }
    client.post("/api/v1/assets/", json=asset_data)
    
    # Try again with same asset_number
    response = client.post("/api/v1/assets/", json=asset_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Asset number already exists"
