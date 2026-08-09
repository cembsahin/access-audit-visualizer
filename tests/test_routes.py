def test_index_page_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Access Review" in response.data


def test_upload_with_no_file_redirects_home(client):
    response = client.post("/upload", data={}, content_type="multipart/form-data")
    assert response.status_code == 302
    assert response.headers["Location"] == "/"


def test_upload_rejects_non_csv_extension(client):
    data = {"file": (__import__("io").BytesIO(b"not a csv"), "notes.txt")}
    response = client.post("/upload", data=data, content_type="multipart/form-data")
    assert response.status_code == 302
    assert response.headers["Location"] == "/"


def test_upload_rejects_missing_columns(client):
    bad_csv = __import__("io").BytesIO(b"username,department\njsmith,Engineering\n")
    data = {"file": (bad_csv, "bad.csv")}
    response = client.post("/upload", data=data, content_type="multipart/form-data")
    assert response.status_code == 302
    assert response.headers["Location"] == "/"


def test_upload_valid_csv_redirects_to_dashboard(client, sample_csv_bytes):
    data = {"file": (sample_csv_bytes, "access_log.csv")}
    response = client.post("/upload", data=data, content_type="multipart/form-data")
    assert response.status_code == 302
    assert response.headers["Location"] == "/dashboard"


def test_dashboard_renders_after_upload(client, sample_csv_bytes):
    data = {"file": (sample_csv_bytes, "access_log.csv")}
    client.post("/upload", data=data, content_type="multipart/form-data")

    response = client.get("/dashboard")
    assert response.status_code == 200
    assert b"Access Review Dashboard" in response.data
    assert b"jsmith" in response.data


def test_department_breakdown_api(client, sample_csv_bytes):
    data = {"file": (sample_csv_bytes, "access_log.csv")}
    client.post("/upload", data=data, content_type="multipart/form-data")

    response = client.get("/api/department-breakdown")
    assert response.status_code == 200
    payload = response.get_json()
    assert "Engineering" in payload["labels"]
    assert "IT" in payload["labels"]
    assert sum(payload["values"]) == 4


def test_stale_vs_active_api(client, sample_csv_bytes):
    data = {"file": (sample_csv_bytes, "access_log.csv")}
    client.post("/upload", data=data, content_type="multipart/form-data")

    response = client.get("/api/stale-vs-active")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["labels"] == ["Active", "Stale (90+ days)"]
    assert sum(payload["values"]) == 4
