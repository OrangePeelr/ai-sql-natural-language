import argparse
import json
import sqlite3
from .client import Client
from .database import DB_PATH, initialize, query
from .prompts import sql_messages, answer_messages


def ask(client, question, strategy='zero-shot'):
    record = {'question': question, 'strategy': strategy, 'model': client.model,
              'sql': None, 'results': None, 'answer': None, 'calls': [], 'error': None}
    try:
        content, meta = client.complete(sql_messages(question, strategy), json_output=True)
        record['calls'].append(meta)
        record['raw_sql_response'] = content
        decision = json.loads(content)
        sql = decision['sql']
        reason = decision['reason']
        if not isinstance(reason, str) or (sql is not None and (not isinstance(sql, str) or not sql.strip())):
            raise ValueError('Invalid SQL response format.')
        record['sql'] = sql
        if sql is None:
            record['answer'] = reason
            record['status'] = 'unsupported'
            return record
        record['results'] = query(sql)
        answer, meta = client.complete(answer_messages(question, sql, record['results']))
        record['calls'].append(meta)
        record['answer'] = answer
        record['status'] = 'answered'
    except (ValueError, KeyError, IndexError, TypeError, sqlite3.Error, RuntimeError, TimeoutError) as exc:
        record['error'] = str(exc)
        record['status'] = 'error'
    return record


def main():
    parser = argparse.ArgumentParser(description='Ask questions about the employee database.')
    parser.add_argument('question', nargs='?')
    parser.add_argument('--strategy', choices=['zero-shot', 'few-shot'], default='zero-shot')
    parser.add_argument('--model', help='OpenRouter model ID; overrides .env')
    parser.add_argument('--json', action='store_true', help='Print the full result and usage record')
    args = parser.parse_args()
    if not DB_PATH.exists():
        initialize()
    client = Client(args.model)
    def run(question):
        result = ask(client, question, args.strategy)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print('\nSQL:', result['sql'] or '(no query)')
            print('Answer:', result['answer'] or result['error'])
        return result
    if args.question:
        raise SystemExit(1 if run(args.question)['error'] else 0)
    print(f'Employee analytics | {client.model} | {args.strategy}. Type quit to exit.')
    while True:
        try:
            question = input('\nQuestion: ').strip()
        except (EOFError, KeyboardInterrupt):
            break
        if question.lower() in ('quit', 'exit'):
            break
        if question:
            run(question)


if __name__ == '__main__':
    try:
        main()
    except (ValueError, RuntimeError) as exc:
        raise SystemExit(str(exc))

