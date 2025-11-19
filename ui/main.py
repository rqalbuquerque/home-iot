from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
import requests

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

COORDINATOR_URL = "http://coordinator:8000"

@app.get("/", response_class=HTMLResponse)
def index():
    resp = requests.get(f"{COORDINATOR_URL}/devices")
    data = resp.json()
    registered = data.get("registered", [])
    unregistered = data.get("unregistered", [])
    html = f"""
    <html>
    <head>
        <title>Device Management UI</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background: #f7f7f7; }}
            h1 {{ color: #333; text-align: center; }}
            .container {{ max-width: 1400px; margin: auto; background: #fff; padding: 30px; border-radius: 8px; box-shadow: 0 2px 8px #ccc; }}
            .section {{ margin-bottom: 30px; }}
            table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
            th, td {{ padding: 10px; text-align: left; }}
            th {{ background: #1976d2; color: #fff; }}
            tr.registered {{ background: #e8f5e9; }}
            tr.unregistered {{ background: #ffebee; }}
            tr:nth-child(even) {{ background: #f5f5f5; }}
            .registered-text {{ color: #2e7d32; font-weight: bold; }}
            .unregistered-text {{ color: #c62828; font-weight: bold; }}
            .msg {{ background: #e3f2fd; color: #1565c0; padding: 10px; border-radius: 5px; margin-bottom: 20px; }}
            button {{ background: #1976d2; color: #fff; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; }}
            button:hover {{ background: #1565c0; }}
        </style>
    </head>
    <body>
    <div class="container">
    <h1></h1>
        <div class="section">
            <h2>Registered Devices</h2>
            <table>
                <tr>
                    <th>Alias</th>
                    <th>Device Type</th>
                    <th>Model Name</th>
                    <th>ID</th>
                    <th>Action</th>
                </tr>
    """
    for d in registered:
        html += f"<tr class='registered'><td class='registered-text'>{d['alias']}</td><td>{d['device_type']}</td><td>{d['model_name']}</td><td>{d['id']}</td><td><form method='post' action='/sync_energy' style='display:inline;'><input type='hidden' name='device_id' value='{d['id']}'><button type='submit'>Sync Energy</button></form></td></tr>"
    html += """
            </table>
        </div>
        <div class="section">
            <h2>Unregistered Devices</h2>
            <form method='post' action='/register'>
            <table>
                <tr>
                    <th>Alias</th>
                    <th>Device Type</th>
                    <th>Model Name</th>
                    <th>ID</th>
                    <th>Action</th>
                </tr>
    """
    for d in unregistered:
        html += f"<tr class='unregistered'><td class='unregistered-text'>{d['alias']}</td><td>{d['device_type']}</td><td>{d['model_name']}</td><td>{d['id']}</td><td><input type='checkbox' name='device_ids' value='{d['id']}'></td></tr>"
    html += """
            </table>
            <button type='submit'>Register Selected Devices</button>
            </form>
        </div>
    </div>
    </body>
    </html>
    """
    return html


@app.post("/register")
async def register(request: Request):
    form = await request.form()
    device_ids = form.getlist('device_ids')
    resp = requests.post(f"{COORDINATOR_URL}/devices/register", json={"device_ids": device_ids})
    return RedirectResponse("/", status_code=303)

# Endpoint to trigger device energy consumption sync
@app.post("/sync_energy")
async def sync_energy(request: Request):
    form = await request.form()
    device_id = form.get('device_id')
    if device_id:
        requests.post(f"{COORDINATOR_URL}/devices/sync_energy", json={"device_id": device_id})
    return RedirectResponse("/", status_code=303)
