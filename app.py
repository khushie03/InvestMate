from flask import Flask, render_template, request, jsonify
app = Flask(__name__, static_folder='static', template_folder='templates')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/features')
def features():
    return render_template('index.html', _anchor='features')

@app.route('/how-it-works')
def how_it_works():
    return render_template('index.html', _anchor='how-it-works')

@app.route('/testimonials')
def testimonials():
    return render_template('index.html', _anchor='testimonials')

@app.route('/pricing')
def pricing():
    return "Pricing page coming soon!"

@app.route('/chat')
def chat():
    return render_template('chatbot.html')

@app.route('/process_investment', methods=['POST'])
def process_investment():
    try:
        data = request.json
        salary = data.get('salary', 0)
        savings = data.get('savings', 0)
        investment = data.get('investment', 0)
        investment_firm = data.get('platform', '')
        
        # Import here to avoid loading these modules unless needed
        from serpapi import GoogleSearch
        import requests
        from bs4 import BeautifulSoup
        import google.generativeai as genai
        
        # Search for news about the investment platform
        params = {
            "engine": "google_news",
            "q": f"Finance " + investment_firm,
            "gl": "us",
            "hl": "en",
            "api_key": "Your serpapi key"
        }
        
        search = GoogleSearch(params)
        results = search.get_dict()
        news_results = results.get("news_results", [])
        
        # Get content from first few news articles
        news_content = []
        for article in news_results[:5]:
            try:
                url = article.get('link')
                if url:  
                    response = requests.get(url, timeout=5)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, "html.parser")
                        # Get text from the main content, limiting size
                        text = soup.get_text()[:5000]
                        news_content.append(text)
            except Exception as e:
                print(f"Error fetching article: {e}")
        
        # Combine the news content
        combined_news = "\n".join(news_content)
        
        # Use Gemini to analyze the investment
        genai.configure(api_key="Your gemini api key")
        model = genai.GenerativeModel("gemini-2.0-flash")
        
        prompt = f"""
        On the basis of the current salary Rs.{salary} and the amount of savings Rs.{savings} 
        and the amount invested Rs.{investment} in {investment_firm}, can you give me:
        1. Details of the investment and if it's profitable or not
        2. Details about {investment_firm} as an investment firm
        3. Recommendations for better investment strategies based on my financial situation
        
        Additional context from recent news:
        {combined_news[:1000]}
        """
        
        response = model.generate_content(prompt)
        
        return jsonify({
            "status": "success",
            "analysis": response.text
        })
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        })

if __name__ == '__main__':
    app.run(debug=True)