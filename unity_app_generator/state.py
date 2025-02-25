import os
import json
import logging

STORE_BASENAME = "app_state.json"

logger = logging.getLogger(__name__)

class ApplicationStateError(Exception):
    pass

class ApplicationState(object):


    state_values = {
        "app_base_path": "",
        "cwl_output_path": "",

        "source_repository": None,
        "docker_image_namespace": None,
        "docker_image_repository": None,
        "docker_image_tag": None,
        "docker_image_reference": None,
        "docker_url": None,
        "app_registry_id": None,
    }

    def __init__(self, state_directory, app_base_path=None, source_repository=None):

        self.state_directory = os.path.realpath(state_directory)
        self.values_store_filename = os.path.join(self.state_directory, STORE_BASENAME)

        # Initialize state directory and store file
        if self.__class__.exists(self.state_directory):
            logger.debug(f"Reading existing application state directory {self.state_directory}")
            self._read_state()
        else:
            logger.debug(f"Initializing new application state directory {self.state_directory}")
            self._init_new(app_base_path, source_repository)

    def _init_new(self, app_base_path, source_repository=None):

        if app_base_path is None:
            raise ApplicationStateError(f"app_base_path must be supplied when state directory or store file does not already exist. State directory: {state_directory}, Store filename: {self.values_store_filename}")

        self.state_values["app_base_path"] = app_base_path

        if os.path.exists(source_repository):
            self.state_values["source_repository"] = os.path.realpath(source_repository)
        else:
            self.state_values["source_repository"] = source_repository

        # Default path
        self.cwl_output_path = os.path.join(self.state_directory, "cwl")

        self._write_state()

    def _read_state(self):

        if not os.path.exists(self.values_store_filename):
            raise ApplicationStateError(f"Values store file does not exist: {self.values_store_filename}")

        with open(self.values_store_filename, "r") as dump_file:
            self.state_values.update(json.load(dump_file))

    def _write_state(self):

        state_parent_dir = os.path.dirname(self.state_directory)
        if not os.path.exists(state_parent_dir):
            raise ApplicationStateError(f"Can not create {self.state_directory} since parent directory {state_parent_dir} does not exist.")

        if not os.path.exists(self.state_directory):
            os.mkdir(self.state_directory)

        with open(self.values_store_filename, "w") as dump_file:
            json.dump(self.state_values, dump_file, sort_keys=True, indent=4)

    @classmethod
    def exists(cls, state_directory):
        values_store_filename = os.path.join(state_directory, STORE_BASENAME)

        if os.path.exists(values_store_filename):
            return True

    def __getattr__(self, name):

        if not name in self.state_values:
            raise ApplicationStateError(f"{name} is not a valid state value name")

        return self.state_values[name]

    def __setattr__(self, name, new_value):

        if name in self.state_values:
            self.state_values[name] = new_value
            self._write_state()
        else:
            self.__dict__[name] = new_value
