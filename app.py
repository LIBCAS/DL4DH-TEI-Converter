from collections import OrderedDict
from flask import Flask, request, abort, Blueprint, redirect
from flask_restx.apidoc import apidoc
from werkzeug.exceptions import HTTPException
from converter import generate_tei_header, generate_tei_page, generate_tei_document
from info import APP_VERSION
from models import generate_merge_parser, generate_header_model, generate_page_model
from utils import xml_response, xml_response_handler, exception_handler, prepare_filter, content_type_json, validate
from flask_restx import Api, Resource

URL_PREFIX = '/tei'
apidoc.url_prefix = URL_PREFIX

# prepare api with xml responses and swagger info
blueprint = Blueprint('api', __name__)
api = Api(blueprint, version=APP_VERSION, title="TEI Converter", contact_email="sekan@inqool.cz")
api.representations = OrderedDict([("application/xml", xml_response_handler)])

# register app with api
app = Flask(__name__)
app.register_error_handler(HTTPException, exception_handler)
app.register_blueprint(blueprint, url_prefix=URL_PREFIX)
app.url_map.strict_slashes = False

# modify response content type for swagger.json specification
app.view_functions['api.specs'] = content_type_json(app.view_functions.get('api.specs'))

# prepare namespaces and inputs for merge endpoint
merge_space = api.namespace('merge')
convert_space = api.namespace('convert')
merge_parser = generate_merge_parser(api)


@app.before_request
def log_request_info():
    app.logger.debug('Headers: \n%s', str(request.headers).strip())
    app.logger.debug('Body: \n%s\n', request.get_data())


@app.route('/')
def default_page():
    return redirect(URL_PREFIX)


@merge_space.route('')
@merge_space.expect(merge_parser)
class Merge(Resource):
    @merge_space.response(200, 'Spojenie úspešne prebehlo. TEI dokument vrátený v response.')
    @merge_space.doc(description='Spojenie hlavičky so stránkami + prípadne filtrovanie obsahu.')
    def post(self):
        if 'header' not in request.files:
            abort(400, description="A file with name `header` does not found in the form data.")
        pages = request.files.getlist("page[]")
        if not pages:
            abort(400, description="Files array with name `page[]` is empty.")
        config = {
            'NameTag': prepare_filter('NameTag'),
            'UDPipe': prepare_filter('UDPipe'),
            'ALTO': prepare_filter('ALTO')
        }
        document = generate_tei_document(request.files.get('header'), pages, config)
        validate(document, app.logger)
        return xml_response(document)


@convert_space.route('/header')
class Header(Resource):
    @convert_space.expect(generate_header_model(api))
    @convert_space.response(200, 'Konverzia úspešne prebehal. XML hlavičky vrátené v response.')
    @convert_space.doc(description='Konverzia JSON objektu hlavičky z Kramerius+ do TEI hlavičky.')
    def post(self):
        return xml_response(generate_tei_header(request.get_json(True)))


@convert_space.route('/page')
class Page(Resource):
    @convert_space.expect(generate_page_model(api))
    @convert_space.response(200, 'Konverzia úspešne prebehal. XML stránky vrátená v response.')
    @convert_space.doc(description='Konverzia JSON objektu stránky z Kramerius+ do TEI elementu stránky.')
    def post(self):
        return xml_response(generate_tei_page(request.get_json(True)))


if __name__ == '__main__':
    app.run()
