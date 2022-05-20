from logging import Logger
from xml.dom import minidom
from lxml.etree import fromstring, XMLSchema, Error
from xml.etree.ElementTree import tostring, Element
from flask import make_response, json, request, abort

calendar = {
    "leden": "01",
    "únor": "02",
    "březen": "03",
    "duben": "04",
    "květen": "05",
    "červen": "06",
    "červenec": "07",
    "srpen": "08",
    "září": "09",
    "říjen": "10",
    "listopad": "11",
    "prosinec": "12"
}


def month_to_number(month):
    if month.lower() in calendar:
        month = calendar[month.lower()]
    return month


def prettify(elem: Element) -> str:
    rough_string = tostring(elem, 'utf-8')
    parsed = minidom.parseString(rough_string)
    return '\n'.join([line for line in parsed.toprettyxml(indent=' '*2).split('\n') if line.strip()])


def prepare_filter(filter_name):
    if filter_name not in request.form:
        return None
    attributes = request.form.get(filter_name, '').split(',')
    return list(map(lambda x: x.lower().strip(), attributes))


def xml_response_handler(data, code, headers):
    if isinstance(data, dict) and "xml" in data and isinstance(data["xml"], Element):
        data = prettify(data["xml"])
    resp = make_response(data, code)
    resp.headers.extend(headers)
    return resp


def xml_response(elem: Element) -> dict:
    return {"xml": elem}


def content_type_json(func):
    def wrapper():
        res = func()
        res.content_type = 'application/json'
        return res
    return wrapper


def exception_handler(e):
    """Return JSON instead of HTML for HTTP errors."""
    response = e.get_response()
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    return response


def validate(elem: Element, logger: Logger = None):
    xml_string = tostring(elem, 'utf-8')
    try:
        xml_file = fromstring(xml_string)
    except Error as e:
        # abort(500, description=str(e))
        if logger:
            logger.error(str(e))
        return

    try:
        xml_validator = XMLSchema(file="scheme/document.xsd")
    except Error as e:
        # abort(500, description=str(e))
        if logger:
            logger.error(str(e))
        return

    if not xml_validator.validate(xml_file):
        error = xml_validator.error_log.last_error
        message = "ERROR ON LINE %s: %s" % (error.line, error.message.encode("utf-8"))
        # abort(500, description=message)
        if logger:
            logger.error(message)
        return
