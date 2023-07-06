def app(environ, start_response):
    path = environ.get('PATH_INFO', '').lstrip('/')
    if path == 'static_nginx_gunicorn/sample.html':
        status = '200 OK'
        headers = [('Content-type', 'text/html')]
        start_response(status, headers)
        with open('static_nginx_gunicorn/sample.html', mode='r') as f:
            return [f.read().encode('utf-8')]
    else:
        status = '404 Not Found'
        headers = [('Content-type', 'text/plain')]
        start_response(status, headers)
        return [b'404 Not Found']
