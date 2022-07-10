from __future__ import annotations

from typing import Sequence, Optional, Type, Any

from google.protobuf.message import Message

import pandas as pd


def proto_normalize(
    protos: Sequence[dict[str, Any]] | Sequence[Message],
    type: Optional[Type[Message]] = None,
    including_repeated_fields: bool = False,
    including_default_value_fields: bool = True,
    preserving_proto_field_name: bool = True,
    use_integers_for_enums: bool = True,
) -> pd.DataFrame:
    pass


def proto_explode(
    protos: Sequence[dict[str, Any]] | Sequence[Message],
    path: str,
    type: Optional[Type[Message]] = None,
    including_repeated_fields: bool = False,
    including_default_value_fields: bool = True,
    preserving_proto_field_name: bool = True,
    use_integers_for_enums: bool = True,
) -> pd.DataFrame:
    pass
