from dataclasses import dataclass, field


def field2(val: dict) -> dict:
    return field(default_factory=lambda: val)


@dataclass
class Test:
    a: dict = field2({})


print(Test().a == Test().a)
