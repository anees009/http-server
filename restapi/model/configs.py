from marshmallow import Schema, fields, post_load

# Main class that handles data structure for nested configs   
class Configs():
    '''
    Class that represents data-structure of all configs
    '''
    def __init__(self, dcname, metadata):
        self.dcname = dcname
        self.metadata = metadata

    def __repr__(self):
        return '<Config(dcname={self.dcname!r})>'.format(self=self)

class Cpu():
    def __init__(self, enabled, value):
        self.enabled = enabled
        self.value = value

class Monitor():
    def __init__(self, enabled):
        self.enabled = enabled

class Limits():
    def __init__(self, cpu):
        self.cpu = cpu

class Metadata():
    def __init__(self, monitoring, limits):
        self.monitoring = monitoring
        self.limits = limits

class MonitorSchema(Schema):
    enabled = fields.Bool()

class CpuSchema(Schema):
    enabled = fields.Bool()
    value = fields.Str()

class LimitsSchema(Schema):
    cpu = fields.Nested(CpuSchema)

class MetadataSchema(Schema):
    monitoring = fields.Nested(MonitorSchema)
    limits = fields.Nested(LimitsSchema)


class ConfigsSchema(Schema):
    dcname = fields.Str()
    metadata = fields.Nested(MetadataSchema)

    @post_load
    def make_config(self, data, **kwargs):
        return Configs(**data)
