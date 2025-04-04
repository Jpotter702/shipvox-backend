# ShipVox Backend

Seed structure for Augment to implement modules.


## Project Setup

### 📦 Install Dependencies
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 🛠 Run Development Server
```bash
export FLASK_APP=run.py
flask run
```

### 📂 Folder Structure
- `/auth`: OAuth management per carrier
- `/rates`: Rate request modules
- `/labels`: Label creation modules
- `/pickup`: Pickup scheduler modules
- `/utils`: Validation, logging, exceptions
- `/data`: CSVs and static mapping data

### 🧪 Coming Soon
- Unit tests in `/tests`
- OpenAPI spec
- Carrier fallback handling
- Multi-label batch support
