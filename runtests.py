#!/usr/bin/env python

"""Run topology tests and validate focused Django test labels."""

import os
import sys

from openwisp_utils.test.runner import (
    InvalidTestArgument,
    compile_test_label_pattern,
    parse_test_arguments,
    validate_test_labels,
)

sys.path.insert(0, "tests")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "openwisp2.settings")


def run_focused_tests(arguments):
    import django

    sample_modules = (
        "openwisp2.sample_network_topology.tests",
        "openwisp2.sample_integration_device.tests",
    )
    pattern = compile_test_label_pattern(
        module_roots=(
            "openwisp_network_topology.tests",
            "openwisp_network_topology.integrations.device.tests",
        ),
        exact_modules=sample_modules,
        allow_subpackages=True,
    )
    try:
        labels, flags = parse_test_arguments(
            arguments, pattern, ("--failfast", "--noinput"), require_label=True
        )
        # Websocket tests use pytest functions, which Django's runner cannot discover.
        if any(label.group("module").endswith(".test_websockets") for label in labels):
            raise InvalidTestArgument(
                "Unsupported test argument: use pytest for websocket tests"
            )
        sample_labels = [
            label for label in labels if label.group("module") in sample_modules
        ]
        if sample_labels and len(sample_labels) != len(labels):
            raise InvalidTestArgument(
                "Unsupported test argument: run sample app tests separately"
            )
        if sample_labels:
            os.environ["SAMPLE_APP"] = "1"
        sys.argv[1:] = ["test", *(label.group(0) for label in labels), *flags]
        django.setup()
        validate_test_labels(labels)
    except InvalidTestArgument as error:
        print(error, file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    import pytest
    from django.core.management import execute_from_command_line

    if sys.argv[1:2] == ["--focused"]:
        run_focused_tests(sys.argv[2:])
        execute_from_command_line(sys.argv)
        sys.exit(0)

    args = sys.argv
    args.insert(1, "test")
    if not os.environ.get("SAMPLE_APP", False):
        args.insert(2, "openwisp_network_topology")
        args.insert(3, "openwisp_network_topology.integrations.device")
    else:
        args.insert(2, "openwisp2")
    if os.environ.get("WIFI_MESH", False):
        args.extend(["--tag", "wifi_mesh"])
    else:
        args.extend(["--exclude-tag", "wifi_mesh"])
    execute_from_command_line(args)
    sys.exit(
        pytest.main(
            [os.path.join("openwisp_network_topology", "tests", "test_websockets.py")]
        )
    )
