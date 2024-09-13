import torch
from .. import BaseOperator
from utils.common import BenchmarkConfig

H = 4096
V = 128256
# Each file defines an operator variant
valid_operator_files = ["baseline.py", "custom.py"]


# Reference: https://github.com/linkedin/Liger-Kernel/blob/3d0653b035222cbb845435a1994854e4fd219107/benchmark/scripts/benchmark_fused_linear_cross_entropy.py

class FusedLinearCrossEntropyOperator(BaseOperator):
    name = "FusedLinearCrossEntropy"
    variant = None
    example_inputs_list = []

    def __init__(self, benchmark_config: BenchmarkConfig):
        super().__init__(benchmark_config)

    @classmethod
    def get_inputs(cls, ):
        if not cls.example_inputs_list:
            cls.generate_inputs(cls.benchmark_config)
        return cls.example_inputs_list

    @classmethod
    def generate_inputs(cls, benchmark_config: BenchmarkConfig):
        # Need OOM check
        # for BT in [2**i for i in range(12, 16)]:
        for BT in [2**12]:
            _input = torch.randn(BT, H, requires_grad=True, dtype=benchmark_config.dtype, device=benchmark_config.device.value)
            target = torch.randint(V, (BT, 1), dtype=torch.long, device=benchmark_config.device.value).squeeze(1)
            cls.example_inputs_list.append((_input, target))

    def forward(self, *input):
        return self.operator(*input)

    def backward(self, *input):
        y = self.forward(*input)
        return lambda: y.backward(retain_graph=True)

    def full(self, *input):
        def f():
            y = self.forward(*input)
            y.backward(retain_graph=True)
        return f

    def single_run(self, fn, *inputs):
        fn(*inputs)

