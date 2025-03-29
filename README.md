This project upgrades a JSON Web Key Set (JWKS) server by adding SQLite for permanent key storage. 
The server authenticates users by signing JSON Web Tokens (JWTs) using securely kept private keys.
The database maintains availability and prevents vulnerabilities like SQL injection.       


Features


SQLite-backed key storage to ensure persistence across server restarts.
JWT signing with private keys retrieved from the database.
REST API endpoints for key retrieval and authentication.
Protection against SQL Injection using query parameterization.
Automated testing to ensure stability and functionality.

Prerequisites

Before running this project, ensure the following is installed:
Python 3.x (if using Python)
SQLite3 (included with Python, or install separately if needed)
Required Python packages 


Installation

Clone the repository: git clone https://github.com/SaujanyaPandey/jwks-server
Install dependencies: pip install -r requirements.txt
Set up the SQLite database: python setup_db.py



Running the Server

To start the JWKS server, run: python app.py
The server should now be running at http://localhost:8080/.

API Endpoints

1. Generate JWT
POST /auth
Generates a JWT signed with a valid (unexpired) private key.
If expired=true is passed as a query parameter, the JWT is signed with an expired key.

2. Fetch Public Keys
GET /.well-known/jwks.json
Retrieves all valid (non-expired) public keys.


Testing

Run the test suite to verify functionality:
pytest --cov
Expected test coverage: 80%+

Debugging

If the server fails to start:
Ensure that the totally_not_my_privateKeys.db is created.
Check for missing dependencies and install them.
Review server logs for error messages.

Deliverables

GitHub Repo: Provide a link to the repository.
Gradebot Output Screenshot: Include a screenshot of the Gradebot test client output.
Test Suite Output Screenshot: Include test coverage results.

License
This project is licensed under the MIT License. See LICENSE for details.






