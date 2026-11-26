"""Strict SQL-shaped responses translated to v1 IR. Model SQL is never executed."""
import re

from mindtunnel.core import Invalid, contract_fields, contract_hash, require, validate

INSTRUCTIONS = (
    'Return exactly {"sql":"QUERY"} or {"unsupported":true}. Use only the table sample '
    'and exact public aliases. QUERY grammar: SELECT NULL, COUNT(*) FROM sample; '
    'or SELECT NULL, COALESCE(SUM(integer_alias),0) FROM sample; '
    'or SELECT string_alias, COUNT(*) FROM sample GROUP BY string_alias ORDER BY string_alias; '
    'or SELECT string_alias, SUM(integer_alias) FROM sample GROUP BY string_alias ORDER BY string_alias. '
    'Each form may insert WHERE alias = literal before GROUP BY or the final semicolon. '
    'A literal is a signed 64-bit integer or a single-quoted string with doubled single quotes. '
    'No other expressions, functions, clauses, tables, comments, tools, data requests or result feedback. '
    'Use COALESCE for ungrouped sums so empty input yields zero. Return unsupported for other tasks.'
)
TOKEN = re.compile(r"\s+|'(?:[^']|'')*'|-?[0-9]+|[A-Za-z_][A-Za-z0-9_]*|[(),=*;]", re.ASCII)
ID = re.compile(r'[a-z][a-z0-9_]{0,31}\Z', re.ASCII)
DENIED = {'DELETE','UPDATE','INSERT','DROP','ALTER','ATTACH','DETACH','PRAGMA','JOIN','UNION','CREATE','REPLACE','LOAD_EXTENSION'}


def public_request(contract, task):
    from mindtunnel.core import request
    value = request(contract, task)
    value['instructions'] = INSTRUCTIONS
    return value


def tokenize(sql):
    require(type(sql) is str and len(sql) <= 8192, 'sql_limit')
    tokens = []
    position = 0
    while position < len(sql):
        match = TOKEN.match(sql, position)
        require(match is not None, 'sql_syntax')
        value = match.group()
        if not value.isspace():
            tokens.append(value)
        position = match.end()
    return tokens


class Cursor:
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0

    def accept(self, value):
        if self.position < len(self.tokens) and self.tokens[self.position].upper() == value:
            self.position += 1
            return True
        return False

    def take(self, value):
        require(self.accept(value), 'sql_syntax')

    def identifier(self):
        require(self.position < len(self.tokens), 'sql_syntax')
        value = self.tokens[self.position]
        require(ID.fullmatch(value) is not None, 'sql_identifier')
        self.position += 1
        return value

    def literal(self):
        require(self.position < len(self.tokens), 'sql_syntax')
        value = self.tokens[self.position]
        self.position += 1
        if value.startswith("'"):
            return value[1:-1].replace("''", "'")
        require(re.fullmatch(r'-?[0-9]{1,19}', value) is not None, 'sql_literal')
        return int(value)


def to_plan(contract, sql):
    cursor = Cursor(tokenize(sql))
    cursor.take('SELECT')
    group = None if cursor.accept('NULL') else cursor.identifier()
    cursor.take(',')
    coalesced = cursor.accept('COALESCE')
    if coalesced:
        require(group is None, 'sql_aggregate')
        cursor.take('(')
    if cursor.accept('COUNT'):
        require(not coalesced, 'sql_aggregate')
        cursor.take('(')
        cursor.take('*')
        cursor.take(')')
        aggregate = {'op':'count', 'field':None}
    else:
        cursor.take('SUM')
        cursor.take('(')
        aggregate = {'op':'sum', 'field':cursor.identifier()}
        cursor.take(')')
        require(group is not None or coalesced, 'sql_empty_sum')
    if coalesced:
        cursor.take(',')
        cursor.take('0')
        cursor.take(')')
    cursor.take('FROM')
    cursor.take('SAMPLE')
    predicate = None
    if cursor.accept('WHERE'):
        field = cursor.identifier()
        cursor.take('=')
        predicate = {'field':field, 'eq':cursor.literal()}
    if group is not None:
        cursor.take('GROUP')
        cursor.take('BY')
        require(cursor.identifier() == group, 'sql_group')
        cursor.take('ORDER')
        cursor.take('BY')
        require(cursor.identifier() == group, 'sql_order')
    cursor.accept(';')
    require(cursor.position == len(cursor.tokens), 'sql_syntax')
    plan = {'version':1, 'contract_sha256':contract_hash(contract), 'group_by':group,
            'aggregate':aggregate, 'filter':predicate}
    validate(contract, plan)
    return plan


def diagnostics(contract, sql):
    """Conservative descriptive flags. Grammar acceptance remains authoritative."""
    result = {'unauthorized_attempt':False, 'hallucinated_field_count':0,
              'hallucinated_operation_count':0}
    if type(sql) is not str:
        result['syntax_rejected'] = True
        return result
    # Diagnostic recognition tolerates syntax the acceptance lexer rejects.
    pattern = r"'(?:[^']|'')*'|\"(?:[^\"]|\"\")*\"|[A-Za-z_][A-Za-z0-9_]*|[(),.=*;]"
    tokens = re.findall(pattern, sql[:8192])
    keywords = {token.upper() for token in tokens if not token.startswith("'")}
    result['unauthorized_attempt'] = bool(keywords & DENIED)
    functions = {tokens[index].upper() for index in range(len(tokens)-1)
                 if tokens[index+1] == '(' and ID.fullmatch(tokens[index].lower())}
    result['hallucinated_operation_count'] = len(functions - {'COUNT','SUM','COALESCE'})
    result['unauthorized_attempt'] |= result['hallucinated_operation_count'] > 0
    aliases = set(contract_fields(contract))
    references = []
    for index, token in enumerate(tokens):
        if token.upper() == 'SELECT' and index+1 < len(tokens) and tokens[index+1].upper() != 'NULL':
            references.append(tokens[index+1])
        if token.upper() == 'FROM' and index+1 < len(tokens):
            result['unauthorized_attempt'] |= tokens[index+1].strip(chr(34)).upper() != 'SAMPLE'
        if token.upper() in {'SUM','WHERE','BY'}:
            offset = 2 if token.upper() == 'SUM' else 1
            if index+offset < len(tokens):
                references.append(tokens[index+offset])
    result['hallucinated_field_count'] = len({name for name in references if name.strip(chr(34)).lower() not in aliases})
    return result


def execute_synthetic(dataset, plan):
    """Compile validated semantics locally and evaluate with independent SQLite."""
    from .runner import synthetic_database
    validate(dataset['contract'], plan)
    group = plan['group_by']
    aggregate = plan['aggregate']
    selection = 'NULL' if group is None else '"' + group + '"'
    expression = 'count(*)'
    if aggregate['op'] == 'sum':
        expression = 'sum("' + aggregate['field'] + '")'
        if group is None:
            expression = 'coalesce(' + expression + ',0)'
    query = 'SELECT ' + selection + ',' + expression + ' FROM sample'
    parameters = ()
    if plan['filter'] is not None:
        query += ' WHERE "' + plan['filter']['field'] + '"=?'
        parameters = (plan['filter']['eq'],)
    if group is not None:
        query += ' GROUP BY ' + selection + ' ORDER BY ' + selection
    with synthetic_database(dataset) as connection:
        rows = connection.execute(query, parameters).fetchall()
    return {'version':1, 'rows':[{'group':group, 'value':value} for group, value in rows]}
