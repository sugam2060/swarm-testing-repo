from flask import Flask, request, render_template_string

app = Flask(__name__)

# SIMULATED DATABASE
USER_TIPS = {
    "admin": "Remember to rotate the production secrets every 30 days.",
    "guest": "Welcome to our platform! Please upgrade your account for more features."
}

@app.route("/")
def home():
    return "<h1>Welcome to the User Dashboard</h1><p>Use /tip?user=admin to see your daily tip.</p>"

@app.route("/tip")
def get_tip():
    """
    VULNERABILITY: Server-Side Template Injection (SSTI)
    The 'user' parameter is concatenated directly into a template string 
    before being rendered by Flask/Jinja2. 
    An attacker can pass: /tip?user={{7*7}} or /tip?user={{config}}
    """
    user = request.args.get("user", "guest")
    tip = USER_TIPS.get(user, "No tip available for this user.")
    
    # DANGEROUS: Concatenating user input into the template string
    template = f"""
    <html>
        <body>
            <h2>Tip for {user}:</h2>
            <p>{tip}</p>
        </body>
    </html>
    """
    
    return render_template_string(template)

if __name__ == "__main__":
    app.run(port=5002)
