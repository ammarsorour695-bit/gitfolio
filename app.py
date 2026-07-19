from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__)

# GitHub API base URL
GITHUB_API = "https://api.github.com"

@app.route('/')
def index():
    """Serve the home page"""
    return render_template('index.html')

@app.route('/portfolio')
def portfolio():
    """Serve the portfolio page with GitHub data"""
    username = request.args.get('user', '')
    return render_template('portfolio.html', username=username)

@app.route('/api/github/<username>')
def get_github_data(username):
    """Fetch real GitHub data for a user"""
    try:
        # Fetch user profile
        user_response = requests.get(f"{GITHUB_API}/users/{username}")
        
        if user_response.status_code == 404:
            return jsonify({'error': 'User not found'}), 404
        
        if user_response.status_code != 200:
            return jsonify({'error': 'GitHub API error'}), user_response.status_code
        
        user_data = user_response.json()
        
        # Fetch user repos
        repos_response = requests.get(
            f"{GITHUB_API}/users/{username}/repos",
            params={'sort': 'updated', 'per_page': 6}
        )
        repos_data = repos_response.json() if repos_response.status_code == 200 else []
        
        # Calculate total stars
        total_stars = sum(repo.get('stargazers_count', 0) for repo in repos_data)
        
        # Extract languages
        languages = set()
        for repo in repos_data:
            if repo.get('language'):
                languages.add(repo['language'])
        
        # Prepare response
        result = {
            'name': user_data.get('name', username),
            'login': user_data.get('login', username),
            'bio': user_data.get('bio', ''),
            'avatar_url': user_data.get('avatar_url', ''),
            'public_repos': user_data.get('public_repos', 0),
            'followers': user_data.get('followers', 0),
            'following': user_data.get('following', 0),
            'total_stars': total_stars,
            'languages': sorted(list(languages))[:10],
            'repos': [
                {
                    'name': repo.get('name', ''),
                    'description': repo.get('description', 'No description'),
                    'stars': repo.get('stargazers_count', 0),
                    'forks': repo.get('forks_count', 0),
                    'language': repo.get('language', 'Unknown'),
                    'url': repo.get('html_url', '#')
                }
                for repo in repos_data[:6]
            ]
        }
        
        return jsonify(result)
        
    except requests.exceptions.RequestException as e:
        return jsonify({'error': 'Network error'}), 500
    except Exception as e:
        return jsonify({'error': 'Server error'}), 500

if __name__ == '__main__':
    # Use PORT from environment for Railway
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port)