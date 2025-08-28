import asyncio
import aiohttp
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, jsonify
import concurrent.futures
import time
from urllib.parse import urlparse
import random

app = Flask(__name__)

# List of user agents to rotate
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
]

def get_random_user_agent():
    return random.choice(USER_AGENTS)

def validate_proxy(proxy):
    """Validate proxy format"""
    if ':' not in proxy:
        return False
    parts = proxy.split(':')
    if len(parts) != 2:
        return False
    ip, port = parts
    try:
        # Validate IP address
        if not all(0 <= int(part) <= 255 for part in ip.split('.')):
            return False
        # Validate port
        if not 1 <= int(port) <= 65535:
            return False
    except:
        return False
    return True

async def test_proxy_async(proxy, test_url, timeout=10):
    """Test a proxy asynchronously"""
    try:
        proxy_url = f"http://{proxy}"
        headers = {'User-Agent': get_random_user_agent()}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(test_url, proxy=proxy_url, headers=headers, timeout=timeout) as response:
                if response.status == 200:
                    return {
                        'proxy': proxy,
                        'status': 'working',
                        'response_time': response.response_info.total_seconds if hasattr(response.response_info, 'total_seconds') else None,
                        'status_code': response.status
                    }
                else:
                    return {
                        'proxy': proxy,
                        'status': 'error',
                        'error': f'HTTP Status: {response.status}'
                    }
    except asyncio.TimeoutError:
        return {
            'proxy': proxy,
            'status': 'error',
            'error': 'Timeout'
        }
    except Exception as e:
        return {
            'proxy': proxy,
            'status': 'error',
            'error': str(e)
        }

def scrape_proxies(proxy_source=None):
    """Scrape proxies from free sources"""
    sources = [
        "https://www.sslproxies.org/",
        "https://free-proxy-list.net/",
        "https://www.us-proxy.org/"
    ]
    
    if proxy_source:
        sources = [proxy_source]
    
    proxies = []
    for source in sources:
        try:
            headers = {'User-Agent': get_random_user_agent()}
            response = requests.get(source, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find proxy table
            table = soup.find('table')
            if table:
                rows = table.find_all('tr')
                for row in rows[1:11]:  # Limit to 10 proxies per source
                    cols = row.find_all('td')
                    if len(cols) >= 2:
                        ip = cols[0].text.strip()
                        port = cols[1].text.strip()
                        proxy = f"{ip}:{port}"
                        if validate_proxy(proxy):
                            proxies.append(proxy)
        except Exception as e:
            print(f"Error scraping {source}: {str(e)}")
            continue
    
    return list(set(proxies))  # Remove duplicates

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check_proxy', methods=['POST'])
def check_proxy():
    data = request.json
    proxy = data.get('proxy', '').strip()
    test_url = data.get('test_url', 'https://httpbin.org/ip').strip()
    
    if not proxy:
        return jsonify({'error': 'No proxy provided'}), 400
    
    if not validate_proxy(proxy):
        return jsonify({'error': 'Invalid proxy format. Use IP:PORT format'}), 400
    
    # Test the proxy
    try:
        start_time = time.time()
        headers = {'User-Agent': get_random_user_agent()}
        response = requests.get(test_url, 
                               proxies={'http': f'http://{proxy}', 'https': f'http://{proxy}'},
                               headers=headers,
                               timeout=10)
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            result = {
                'proxy': proxy,
                'status': 'working',
                'response_time': round(response_time, 2),
                'status_code': response.status_code,
                'response_content': response.text[:500] + "..." if len(response.text) > 500 else response.text
            }
        else:
            result = {
                'proxy': proxy,
                'status': 'error',
                'error': f'HTTP Status: {response.status_code}',
                'status_code': response.status_code
            }
    except requests.exceptions.Timeout:
        result = {
            'proxy': proxy,
            'status': 'error',
            'error': 'Timeout'
        }
    except Exception as e:
        result = {
            'proxy': proxy,
            'status': 'error',
            'error': str(e)
        }
    
    return jsonify(result)

@app.route('/scrape_proxies', methods=['POST'])
def scrape_proxies_route():
    data = request.json
    source = data.get('source', '').strip() or None
    test_url = data.get('test_url', 'https://httpbin.org/ip').strip()
    
    try:
        # Scrape proxies
        proxies = scrape_proxies(source)
        
        # Test all proxies asynchronously
        async def test_all_proxies():
            tasks = [test_proxy_async(proxy, test_url) for proxy in proxies]
            return await asyncio.gather(*tasks)
        
        results = asyncio.run(test_all_proxies())
        
        # Filter working proxies
        working_proxies = [result for result in results if result['status'] == 'working']
        failed_proxies = [result for result in results if result['status'] == 'error']
        
        return jsonify({
            'total_found': len(proxies),
            'working': working_proxies,
            'failed': failed_proxies
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
