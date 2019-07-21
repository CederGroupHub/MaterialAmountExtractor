import argparse
import logging
import os

import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.web
from operations_extractor.operations_extractor import OperationsExtractor


class OperationsExtractionHandler(tornado.web.RequestHandler):
    route = r'/operations_extract'
    version = '2018080200'
    _oe = None

    def initialize(self, *args, **kwargs):
        if OperationsExtractionHandler._oe is None:
            OperationsExtractionHandler._oe = OperationsExtractor()
            self._oe = OperationsExtractionHandler._oe

    def post(self):
        def error_wrong_format():
            self.set_status(400)
            self.write({
                'status': False,
                'message': 'Input must be list of dictionaries containing "text" field.'
            })

        documents = tornado.escape.json_decode(self.request.body)

        if not isinstance(documents, list):
            return error_wrong_format()
        for x in documents:
            if not isinstance(x, dict) or 'text' not in x:
                return error_wrong_format()

        results = []

        for doc in documents:
            text = doc['text']
            ops, temperatures, max_temperature, times = self._oe.extract(text)
            result = {
                'operations': [],
                'temperatures': temperatures,
                'max_temperature': max_temperature,
                'times': times
            }

            for verb, type, start, end in ops:
                result['operations'].append({
                    'verb': verb,
                    'operation_type': type,
                    'start': start,
                    'end': end
                })
            results.append(result)

        self.write({
            'status': True,
            'results': results,
            'version': self.version
        })


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

    parser = argparse.ArgumentParser(description='Synthesis Project Web Service.')
    parser.add_argument('--address', action='store', type=str, default='127.0.0.1',
                        help='Listen address.')
    parser.add_argument('--port', action='store', type=int, default=7732,
                        help='Listen port.')

    args = parser.parse_args()

    os.environ['OMP_NUM_THREADS'] = '1'
    os.environ['MKL_NUM_THREADS'] = '1'
    os.environ['OPENBLAS_NUM_THREADS'] = '1'

    server = tornado.httpserver.HTTPServer(
        tornado.web.Application(
            [
                (OperationsExtractionHandler.route, OperationsExtractionHandler)
            ]
        )
    )
    server.bind(address=args.address, port=args.port)
    logging.info('Going to main loop on %s:%d...', args.address, args.port)
    logging.info('Spawning processes...')
    server.start()
    try:
        tornado.ioloop.IOLoop.current().start()
    except KeyboardInterrupt:
        pass
