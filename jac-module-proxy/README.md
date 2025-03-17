# **Setup**
### **LOCAL PREREQUISITE**
> pre-commit install

### **DEV**
> poetry install\
> pip install numpy\
> python -m grpc_tools.protoc -I./server/grpc_local --python_out=./server/grpc_local --grpc_python_out=./server/grpc_local ./server/grpc_local/module_service.proto
> PYTHONPATH=/home/boyong/jaseci/jac-module-proxy/server/grpc_local && poetry run deploy "numpy"

### **PROD**
> poetry install --without dev\
> pip install numpy\
> python -m grpc_tools.protoc -I./server/grpc_local --python_out=./server/grpc_local --grpc_python_out=./server/grpc_local ./server/grpc_local/module_service.proto\
> PYTHONPATH=/home/boyong/jaseci/jac-module-proxy/server/grpc_local && poetry run deploy "numpy"