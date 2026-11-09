@app.route('/ssti')
def ssti():
    user_input = request.args.get('input', '')
    # CHANGED: render a fixed template and pass untrusted input as data.
    return render_template_string("Hello, {{ user_input }}!", user_input=user_input)
