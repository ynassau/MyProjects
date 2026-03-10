import os
from flask import Flask, render_template, request, jsonify
import anthropic

app = Flask(__name__)
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are a roast-style compliment generator. Your job is to write affectionate,
funny roast-style compliments about a colleague. The tone should be:
- Warm and clearly affectionate underneath the teasing
- Office-appropriate and never actually mean or hurtful
- Playful and witty, like something a close friend would say
- Focused on lovable quirks, not real flaws

Generate exactly 3 roast-style compliments for the colleague based on their name and any traits provided.
Format your response as a JSON array of 3 strings, each being one compliment. Example:
["Compliment 1 here", "Compliment 2 here", "Compliment 3 here"]

Return ONLY the JSON array, no other text."""


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()
    name = data.get("name", "").strip()
    traits = data.get("traits", "").strip()

    if not name:
        return jsonify({"error": "Please provide a colleague's name"}), 400

    user_prompt = f"Generate 3 roast-style compliments for my colleague named {name}."
    if traits:
        user_prompt += f" Here are some of their traits/quirks: {traits}"

    try:
        with client.messages.stream(
            model="claude-opus-4-6",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        ) as stream:
            full_response = stream.get_final_message()

        raw_text = full_response.content[0].text.strip()

        import json
        compliments = json.loads(raw_text)

        return jsonify({"compliments": compliments, "name": name})

    except Exception as e:
        return jsonify({"error": f"Something went wrong: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
