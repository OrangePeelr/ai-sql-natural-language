"""OpenRouter integration using standard-library HTTP; never logs credentials."""
import json
import os
from urllib import request, error
from .database import ROOT

DEFAULT_MODEL = 'google/gemini-3.1-flash-lite'


def load_env():
    path = ROOT / '.env'
    if path.exists():
        for line in path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            key, value = line.removeprefix('export ').split('=', 1)
            os.environ.setdefault(key.strip(), value.strip().strip('\"\''))


class Client:
    def __init__(self, model=None):
        load_env()
        self.key = os.getenv('OPENROUTER_API_KEY') or os.getenv('OPEN_ROUTER')
        if not self.key:
            raise ValueError('Set OPENROUTER_API_KEY (or OPEN_ROUTER) in .env.')
        self.model = model or os.getenv('OPENROUTER_MODEL', DEFAULT_MODEL)

    def complete(self, messages, json_output=False):
        body = {'model': self.model, 'messages': messages, 'temperature': 0,
                'max_tokens': 1200}
        if json_output:
            body['response_format'] = {'type': 'json_object'}
        req = request.Request('https://openrouter.ai/api/v1/chat/completions',
                              data=json.dumps(body).encode(),
                              headers={'Authorization': 'Bearer ' + self.key,
                                       'Content-Type': 'application/json'})
        try:
            with request.urlopen(req, timeout=60) as response:
                data = json.load(response)
        except error.HTTPError as exc:
            # Do not echo response bodies: they could contain sensitive request data.
            raise RuntimeError(f'OpenRouter HTTP {exc.code}; check credits, model access, or rate limits.') from None
        except error.URLError:
            raise RuntimeError('Cannot reach OpenRouter; check network access.') from None
        if data.get('error'):
            raise RuntimeError('OpenRouter returned an API error.')
        choice = data['choices'][0]
        if choice.get('finish_reason') == 'length':
            raise RuntimeError('Model output exceeded the token limit.')
        content = choice['message'].get('content')
        if not isinstance(content, str) or not content.strip():
            raise RuntimeError('Model returned no text.')
        return content, {'model': data.get('model', self.model), 'usage': data.get('usage', {})}

    def pricing(self):
        try:
            with request.urlopen('https://openrouter.ai/api/v1/models', timeout=30) as response:
                models = json.load(response)['data']
            return next(m['pricing'] for m in models if m['id'] == self.model)
        except (error.URLError, StopIteration):
            return None

