# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

import module_service_pb2 as module__service__pb2

GRPC_GENERATED_VERSION = "1.71.0"
GRPC_VERSION = grpc.__version__
_version_not_supported = False

try:
    from grpc._utilities import first_version_is_lower

    _version_not_supported = first_version_is_lower(
        GRPC_VERSION, GRPC_GENERATED_VERSION
    )
except ImportError:
    _version_not_supported = True

if _version_not_supported:
    raise RuntimeError(
        f"The grpc package installed is at version {GRPC_VERSION},"
        + f" but the generated code in module_service_pb2_grpc.py depends on"
        + f" grpcio>={GRPC_GENERATED_VERSION}."
        + f" Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}"
        + f" or downgrade your generated code using grpcio-tools<={GRPC_VERSION}."
    )


class ModuleServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.execute = channel.unary_unary(
            "/ModuleService/execute",
            request_serializer=module__service__pb2.MethodRequest.SerializeToString,
            response_deserializer=module__service__pb2.MethodResponse.FromString,
            _registered_method=True,
        )


class ModuleServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def execute(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")


def add_ModuleServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
        "execute": grpc.unary_unary_rpc_method_handler(
            servicer.execute,
            request_deserializer=module__service__pb2.MethodRequest.FromString,
            response_serializer=module__service__pb2.MethodResponse.SerializeToString,
        ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
        "ModuleService", rpc_method_handlers
    )
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers("ModuleService", rpc_method_handlers)


# This class is part of an EXPERIMENTAL API.
class ModuleService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def execute(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/ModuleService/execute",
            module__service__pb2.MethodRequest.SerializeToString,
            module__service__pb2.MethodResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True,
        )
