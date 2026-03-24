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
    SECURITY FIX: No more Server-Side Template Injection (SSTI).
    The template is now static, and the user-provided data is passed 
    as a safe template variable. Jinja2 handles the escaping automatically.
    """
    user_name = request.args.get("user", "guest")
    tip = USER_TIPS.get(user_name, "No tip available for this user.")
    
    # SAFE: Using a static template string and passing variables for rendering
    template = """
    <html>
        <body>
            <h2>Tip for {{ user_name }}:</h2>
            <p>{{ user_tip }}</p>
        </body>
    </html>
    """
    
    return render_template_string(template, user_name=user_name, user_tip=tip)

if __name__ == "__main__":
    app.run(port=5002)
