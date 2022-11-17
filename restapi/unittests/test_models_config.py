"""
This file (test_models_config.py) contains the unit tests for the configs.py file.
"""
import unittest
from restapi.model.configs import Configs, Metadata, Monitor, Limits, Cpu

class TestConfigs(unittest.TestCase):
    
    def test_monitor(self):
        '''
        Given a Monitor Model
        When new bool value is set
        Then check if it is defined correctly
        '''
        monitor = Monitor(False)
        assert monitor.enabled != True

    def test_cpu(self):
        cpu = Cpu(True, "300")
        assert cpu.enabled == True
        assert cpu.value != "500m"

    def test_limits(self):
        limits = Limits(Cpu(False, "100m"))
        assert limits.cpu.value == "100m"

    def test_metadate(self):
        metadata = Metadata(Monitor(True), Limits(Cpu(True, "250m")))
        assert metadata.monitoring != False
        assert metadata.limits.cpu.value == "250m"

    def test_get_configs(self):
        '''
        Given a Configs Model
        When new config is creat4ed
        Then check dcname and all the nested metadata is defined correctly
        '''
        config = Configs('datacenter-1', Metadata(Monitor(True), Limits(Cpu(True, '500m'))))
        assert config.dcname == 'datacenter-1'
        assert config.metadata.limits.cpu.value == '500m'
        assert config.metadata.limits.cpu.enabled != False
        assert config.metadata.monitoring.enabled != False
    
if __name__ == '__main__':
    unittest.main()
