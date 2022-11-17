from flask import Flask, jsonify, request, abort
from restapi.model.configs import Configs, ConfigsSchema, Monitor, Limits, Cpu, Metadata
from restapi.model.metrics_exporter import ConfigMetrics
from pythonjsonlogger import jsonlogger
from jaeger_client import Config
from flask_opentracing import FlaskTracer

app = Flask(__name__)

# Jaeger tracing implementation
def  initialize_tracer():
  "Tracing setup method"
  config = Config(
			    config={
      'sampler': {'type': 'const', 'param': 1},
    },
    service_name='restapi')
  return config.initialize_tracer()

flaskTracer = FlaskTracer(lambda: initialize_tracer(), True, app)


formatter = jsonlogger.JsonFormatter(
    '%(asctime) %(levelname) %(funcName) %(message)')

app.logger.handlers[0].setFormatter(formatter)

# Initialize with a dataset to work on
all_configs = [ Configs('datacenter-1', Metadata(Monitor(True), Limits(Cpu(True, '500m')))),
            Configs('datacenter-2', Metadata(Monitor(True), Limits(Cpu(True, '500m')))) ]

# The below dicts are for metric exporter
http_requests_config_metrics = {}
http_requests_metrics = {}

@app.route('/')
def home_page():
    app.logger.info('Accessing Home Page')
    return "Welcome to Home Page\n"

# Get all configs
@app.route('/configs')
def get_all_configs(http_requests_config_metrics=http_requests_config_metrics):
    app.logger.info('Retriving all configs')
    # Serialize object inorder to use as json
    schema = ConfigsSchema(many=True)
    result = schema.dump(all_configs)
    endpoint = "/configs"
    # Export operation to metrics exporter
    http_requests_config_metrics = ConfigMetrics.get_configs(
                                                   http_requests_config_metrics,
                                                   endpoint)
    return jsonify(result)

# API route to get individual config
@app.route('/configs/<config>')
def get_config(config):
    app.logger.info('GET: /configs/%s' % config)
    schema = ConfigsSchema(many=True)
    result = schema.dump(
        filter(lambda t: t.dcname == config, all_configs)
        )
    return jsonify(result)

# API route to create a new config
@app.route('/configs', methods=['POST'])
def add_config(http_requests_metrics=http_requests_metrics):  
    # Load (De-Serialize) object
    config = ConfigsSchema().load(request.get_json())
    app.logger.info('POST: Adding new config %s' % config.dcname) 
    # Check for duplicates, Check if resource already exists.
    for obj in all_configs:    
        if obj.dcname == config.dcname:
            app.logger.error('Adding new config %s failed.' % config.dcname)
            app.logger.info('Resource %s already exists.' % config.dcname) 
            return_code = "403"
            http_requests_metrics = ConfigMetrics.get_http_requests(
                                                    http_requests_metrics,
                                                    request.method.lower(),
                                                    return_code)
            abort(403, description="Resource already exists")
    all_configs.append(config)
    app.logger.info('Adding new config %s successful.' % config.dcname)
    return_code = "204"
    http_requests_metrics = ConfigMetrics.get_http_requests(
                                http_requests_metrics,
                                request.method.lower(),
                                return_code)
    return "", int(return_code)

# API for DELETE operation
@app.route('/configs/<config>', methods=['DELETE'])
def delete_config(config, http_requests_metrics=http_requests_metrics):
    app.logger.info('DELETE: Deleting config %s.' % config)
    return_code = "204"
    counter = False
    for item, obj in enumerate(all_configs):
        if obj.dcname == config:
            del all_configs[item]
            app.logger.info('config successfully deleted.')
            counter = True
            http_requests_metrics = ConfigMetrics.get_http_requests(
                                                    http_requests_metrics,
                                                    request.method.lower(),
                                                    return_code)
            break
    if counter == False:
        app.logger.error('Delete failed: Resource Not Found')
        return_code = "404"
        http_requests_metrics = ConfigMetrics.get_http_requests(
                                                    http_requests_metrics,
                                                    request.method.lower(),
                                                    return_code)
        abort(404, description="Resource not found")
    return "", int(return_code)

# API for PUT
# Validate new data, check for existing data, delete old data and append new data
@app.route('/configs/<config>', methods=['PUT'])
def put_config(config):
    # load to validate data structure
    app.logger.info('PUT: Changing config %s' % config)
    new_config = ConfigsSchema().load(request.get_json())
    if new_config.dcname != config:
        app.logger.error('%s config Resource not found.' % config)
        abort(404, description="Resource not found")

    for item, obj in enumerate(all_configs):
        if obj.dcname == config:
            del all_configs[item]
            break
    all_configs.append(new_config)
    app.logger.info('PUT: Changing config %s successful' % config)
    return "", 204

# Prometheus Metrics
@app.route('/metrics')
def metrics():
    app.logger.info('Querying metrics data')
    metrics = ConfigMetrics.export_metrics(http_requests_config_metrics,
                                                  http_requests_metrics)
    app.logger.info('Querying metrics data Successful')
    return metrics

if __name__ == "__main__":
    app.run()
