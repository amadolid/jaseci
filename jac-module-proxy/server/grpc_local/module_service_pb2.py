# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: module_service.proto
# Protobuf Python Version: 5.29.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC, 5, 29, 0, "", "module_service.proto"
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x14module_service.proto"\x9d\x01\n\rMethodRequest\x12\x0e\n\x06obj_id\x18\x01 \x01(\t\x12\x13\n\x0bmethod_name\x18\x02 \x01(\t\x12\x0c\n\x04\x61rgs\x18\x03 \x03(\t\x12*\n\x06kwargs\x18\x04 \x03(\x0b\x32\x1a.MethodRequest.KwargsEntry\x1a-\n\x0bKwargsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01"E\n\x0eMethodResponse\x12\x0e\n\x06result\x18\x01 \x01(\t\x12\x0e\n\x06obj_id\x18\x02 \x01(\t\x12\x13\n\x0bis_callable\x18\x03 \x01(\x08\x32=\n\rModuleService\x12,\n\x07\x65xecute\x12\x0e.MethodRequest\x1a\x0f.MethodResponse"\x00\x62\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, "module_service_pb2", _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals["_METHODREQUEST_KWARGSENTRY"]._loaded_options = None
    _globals["_METHODREQUEST_KWARGSENTRY"]._serialized_options = b"8\001"
    _globals["_METHODREQUEST"]._serialized_start = 25
    _globals["_METHODREQUEST"]._serialized_end = 182
    _globals["_METHODREQUEST_KWARGSENTRY"]._serialized_start = 137
    _globals["_METHODREQUEST_KWARGSENTRY"]._serialized_end = 182
    _globals["_METHODRESPONSE"]._serialized_start = 184
    _globals["_METHODRESPONSE"]._serialized_end = 253
    _globals["_MODULESERVICE"]._serialized_start = 255
    _globals["_MODULESERVICE"]._serialized_end = 316
# @@protoc_insertion_point(module_scope)
