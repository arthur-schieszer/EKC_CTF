# EKC CTF Web Exploit Challenges
A simple (and intentionally vulnerable) Flask web server used for teaching basic web exploitation techniques:  
- **Challenge 1:** Source code investigation / hidden flag discovery  
- **Challenge 2:** Cookie manipulation (base64-encoded role escalation)  
- **Challenge 3:** JWT algorithm tampering (`alg: none` exploit)

---

## Setup
1. Clone or copy the project files to the competition environment.
2. Ensure Python 3.9+ and `pip` are installed.
3. (Optional but recommended) create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
4. Install Dependencies:
    ```bash
    pip install -r requirements.txt
    ```
5. Run the server:
    ```bash
    python app.py
    ```


## Flags
### Challenge 1
ekc{h1dd3n_in_pl41n_s1ght}
### Challenge 2
ekc{c00k13s_4r3_n0t_s3cur3}
### Challenge 3
ekc{jwt_n0n3_alg0r1thm_pwn3d}


## Hints
### Challenge 1
No Hints
### Challenge 2
#### Hint 1
The website has a way of determining if you are a user or admin.
#### Hint 2
Examine your stored cookies carefully.
### Challenge 3
#### Hint 1
Check your cookies for a token value.
#### Hint 2
Research the structure that the token follows.


## Solutions
### Challenge 1 — Hidden in the page
1. Open the Challenge 1 page (`/challenge1`) in a browser.
2. View page source (right-click → View Page Source) or inspect the inline SVG.
3. The flag is present in the embedded content (inline SVG text).  
### Challenge 2 — Cookie manipulation (base64 role)
1. Open the Challenge 2 page (`/challenge2`).
2. Attempt a login to the site to recieve a role. The username and password do not matter.
3. Open DevTools → Application (Storage) → Cookies → find cookie named `role`.
4. Change the cookie value to the base64 for `"admin"`
5. Log in again to receive the flag
### Challenge 3 - JWT `alg: none` exploit
1. Open the Challenge 3 page (`/challenge3`).
2. Open DevTools → Application → Cookies → find cookie named token. Default token is HS256 and non-admin.
3. Alter the header so the algorithm is `"none"`.
4. Alter the payload so the role is `"admin"`.
5. Set the newly edited token as the `token` cookie.
6. Log in to the webpage again to receive the flag.