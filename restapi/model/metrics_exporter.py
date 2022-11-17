class ConfigMetrics():
    '''
    Class that implements the metrics exporter
    All the count increment for each metric is done in this class
    All the metrics formatting for promethues consumption is done in this class

    '''

    def get_configs(http_requests_config_metrics, endpoint):
        if endpoint not in http_requests_config_metrics:
            http_requests_config_metrics[endpoint] = 1            
        else:
            http_requests_config_metrics[endpoint] += 1
        return http_requests_config_metrics
    
    def get_http_requests(http_requests_metrics, method, return_code):
        if (method, return_code) not in http_requests_metrics:
            http_requests_metrics[(method, return_code)] = 1
        else:
            http_requests_metrics[(method, return_code)] += 1
        return http_requests_metrics
    
    def export_metrics(http_requests_config_metrics, http_requests_metrics):
        metrics = ""
        metrics += "# HELP http_requests_config The total number of HTTP requests for /config. \n# TYPE http_requests_config counter\n"
        for id in http_requests_config_metrics:
            metrics += 'http_requests_config{endpoint="%s", method="get", code="200"} %s\n' % (id, 
                            http_requests_config_metrics[id])
        metrics += "# HELP http_requests The total number of HTTP requests. \n# TYPE http_requests counter\n"
        for id in http_requests_metrics:
            metrics += 'http_requests{method="%s", code="%s"} %s\n' % (id[0], 
                            id[1], http_requests_metrics[id])   
        return metrics
