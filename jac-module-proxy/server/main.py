"""Jac Proxy Server."""

import sys
import threading
import traceback
from concurrent import futures
from importlib import import_module
from logging import INFO, basicConfig, debug, error, info
from typing import Any

import grpc

from grpc_health.v1 import health, health_pb2, health_pb2_grpc

from uuid6 import uuid7

from .grpc_local import module_service_pb2, module_service_pb2_grpc

basicConfig(level=INFO, format="%(asctime)s %(levelname)s %(message)s")


class ObjectRegistry:
    """Thread-safe registry for storing objects with unique IDs."""

    def __init__(self) -> None:
        """Initialize Object Registry."""
        self.lock = threading.Lock()
        self.objects: dict[str, object] = {}
        debug("ObjectRegistry initialized.")

    def add(self, obj: object) -> str:
        """Add object."""
        obj_id = str(uuid7())
        with self.lock:
            self.objects[obj_id] = obj
            debug(f"Object added with ID {obj_id}: {obj}")
        return obj_id

    def get(self, obj_id: str) -> object:
        """Get object."""
        with self.lock:
            obj = self.objects.get(obj_id)
            debug(f"Object retrieved with ID {obj_id}: {obj}")
            return obj

    def remove(self, obj_id: str) -> None:
        """Remove object."""
        with self.lock:
            if obj_id in self.objects:
                del self.objects[obj_id]
                debug(f"Object with ID {obj_id} removed.")


object_registry = ObjectRegistry()


class ModuleService(module_service_pb2_grpc.ModuleServiceServicer):
    """Module Service."""

    def __init__(self, module_name: str) -> None:
        """Override init."""
        debug(f"Initializing ModuleService with module '{module_name}'")
        try:
            self.module = import_module(module_name.replace("-", "_"))
            info(f"Module '{module_name}' imported successfully.")
        except Exception as e:
            error(f"Failed to import module '{module_name}': {e}")
            raise e

    def execute(self, request: Any, context: Any) -> Any:  # noqa: ANN401
        """Override execute."""
        try:
            debug(f"Received ExecuteMethod request: {request}")
            if request.obj_id:
                # Method call on an object instance
                obj = object_registry.get(request.obj_id)
                if obj is None:
                    error_msg = f"Object with ID {request.obj_id} not found"
                    error(error_msg)
                    raise Exception(error_msg)
            else:
                # Method call on the module
                obj = self.module
                debug(f"Using module '{self.module.__name__}' for method execution.")

            # Get the attribute or method
            attr = getattr(obj, request.method_name, None)
            if attr is None:
                error_msg = f"Attribute '{request.method_name}' not found in '{obj}'"
                error(error_msg)
                raise AttributeError(error_msg)

            debug(f"Executing method '{request.method_name}' on '{obj}'")

            # Deserialize arguments
            import json

            def deserialize_arg(arg: Any) -> Any:  # noqa: ANN401
                import numpy as np
                import base64

                if arg["type"] == "primitive" or arg["type"] == "json":
                    return arg["value"]
                elif arg["type"] == "ndarray":
                    data_bytes = base64.b64decode(arg["data"])
                    array = np.frombuffer(data_bytes, dtype=arg["dtype"])
                    array = array.reshape(arg["shape"])
                    return array
                elif arg["type"] == "ndarray_list":
                    value = arg["value"]
                    return np.array(value, dtype=object)
                elif arg["type"] == "object":
                    obj = object_registry.get(arg["obj_id"])
                    if obj is None:
                        raise Exception(f"Object with ID {arg['obj_id']} not found")
                    return obj
                else:
                    raise Exception(f"Unknown argument type: {arg.get('type')}")

            args = [deserialize_arg(json.loads(arg)) for arg in request.args]
            kwargs = {
                key: deserialize_arg(json.loads(value))
                for key, value in request.kwargs.items()
            }

            debug(f"Arguments after deserialization: args={args}, kwargs={kwargs}")

            if callable(attr):
                result = attr(*args, **kwargs)
            else:
                result = attr

            debug(f"Execution result: {result}")

            def serialize_result(res: Any) -> dict:  # noqa: ANN401
                import numpy as np
                import base64

                if isinstance(res, (int, float, str, bool)):
                    debug(f"Serializing primitive: {res}")
                    return {"type": "primitive", "value": res}
                elif isinstance(res, (np.integer, np.floating)):
                    debug(f"Serializing NumPy scalar: {res}")
                    return {"type": "primitive", "value": res.item()}
                elif isinstance(res, (list, dict, tuple)):
                    debug(f"Serializing JSON serializable object: {res}")
                    return {"type": "json", "value": res}
                elif isinstance(res, np.ndarray):
                    debug(
                        f"Serializing ndarray with dtype: {res.dtype}, shape: {res.shape}"
                    )
                    if res.dtype.kind == "O":
                        debug(
                            "Array has dtype 'object'; converting to list with 'ndarray_list' type."
                        )
                        return {"type": "ndarray_list", "value": res.tolist()}
                    else:
                        data_bytes = res.tobytes()
                        data_b64 = base64.b64encode(data_bytes).decode("utf-8")
                        return {
                            "type": "ndarray",
                            "data": data_b64,
                            "dtype": str(res.dtype),
                            "shape": res.shape,
                        }
                else:
                    debug(f"Serializing object instance: {res}")
                    obj_id = object_registry.add(res)
                    return {"type": "object", "obj_id": obj_id}

            serialized_result = serialize_result(result)
            response = module_service_pb2.MethodResponse(  # type: ignore[attr-defined]
                result=json.dumps(serialized_result), is_callable=callable(result)
            )
            debug(f"Returning serialized result: {response}")
            return response
        except Exception as e:
            error_msg = f"Error during method execution: {str(e)}"
            error(error_msg)
            traceback.print_exc()
            context.set_details(error_msg)
            context.set_code(grpc.StatusCode.INTERNAL)
            return module_service_pb2.MethodResponse()  # type: ignore[attr-defined]


def run() -> None:
    """Run server."""
    if len(sys.argv) < 2:
        print("Usage: python server.py <module_name>")
        sys.exit(1)

    module_name = sys.argv[-1]

    info(f"Starting gRPC server for module '{module_name}'")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    module_service_pb2_grpc.add_ModuleServiceServicer_to_server(
        ModuleService(module_name), server
    )

    health_servicer = health.HealthServicer()
    health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server)

    health_servicer.set(
        service="ModuleService",
        status=health_pb2.HealthCheckResponse.SERVING,
    )
    server.add_insecure_port("[::]:50051")
    server.start()
    info("gRPC server started and listening on port 50051")
    server.wait_for_termination()
