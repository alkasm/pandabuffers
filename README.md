# pandabuffers

Create pandas DataFrames from protobufs.

* Similar semantics to `pd.json_normalize()` and `df.explode()` but crafted specifically for protobufs
* Powerful conventions for dealing with nested messages, enums, and repeated fields
* Any form of proto input
  * protobuf message instances
  * dicts (any form that `google.protobuf.json_format.ParseDict()` can parse)
  * binary serialized protos
* Any convention for output
  * include or exclude repeated fields
  * include or exclude default values for unset fields
  * proto or camelcase field names
  * enums as integers or strings
* Sensible defaults:
  * `including_repeated_fields=False` to remove ambiguity and explode only the necessary rows
  * `including_default_value_fields=True` for better compatibility with other constructed dataframes
  * `preserving_proto_field_name=True` to un-camelCase JSON names for uniformity with protobuf instances
  * `use_integers_for_enums=True` to save memory
* Named indexes for nested repeated fields for trivial joining

Todos:
- [ ] Basic `proto_normalize()` implementation using `MessageToDict(ParseDict(d), **options)`
- [ ] Basic `proto_explode()` with named indexes (first index as `""`?)
- [ ] Decide how to handle nested message detection (e.g. `wrappers.proto`)
- [ ] Decide how to handle oneofs
- [ ] Handle binary messages
- [ ] Remove the proto hop with dict inputs

### Examples

```protobuf
message Person {
  string first_name = 1;
  int32 id = 2;
  repeated string emails = 3;
  PhoneNumber phone = 4;
}

message PhoneNumber {
  enum PhoneType {
    UNKNOWN = 0;
    MOBILE = 1;
    HOME = 2;
  }
  string digits = 1;
  PhoneType type = 2;
}
```

Create a dataframe from a list of message instances (repeated fields are ignored by default):

```python
>>> import pandabuffers as pdbuf
>>> people = [
...     Person(first_name="Alice", id=0, emails=["alice@www.com"], phone=PhoneNumber(digits="555-314-1592", type=1)),
...     Person(first_name="Bob", id=1, emails=["bob@python.com", "bob@hotmail.com"]),
...     Person(first_name="Carol", id=3, emails=["carol@linux.net"], phone=PhoneNumber(digits="555-271-8281", type=2)),
... ]
>>> pdbuf.proto_normalize(people)
  first_name  id  phone.digits  phone.type
0      Alice   0  555-314-1592           1
1        Bob   1                         0
2      Carol   3  555-271-8281           2
```

Explode the repeated field into rows:

```python
>>> pdbuf.proto_explode(people, "emails")
            emails
0    alice@www.com
1   bob@python.net
1  bob@hotmail.com
2  carol@linux.net
```

Join the repeated field back to the root:

```python
>>> df = pdbuf.proto_normalize(people)
>>> emails = pdbuf.proto_explode(people, "emails")
>>> df.join(emails)
  first_name  id  phone.digits  phone.type           emails
0      Alice   0  555-314-1592           1    alice@www.com
1        Bob   1                         0   bob@python.net
1        Bob   1                         0  bob@hotmail.com
2      Carol   3  555-271-8281           2  carol@linux.net
```

Create a dataframe from a list of dicts (containing camelcase field names):

```python
>>> people = [
...     {"firstName": "Alice", "id": 0, "emails": ["alice@www.com"]},
...     {"firstName": "Bob", "id": 1, "emails": ["bob@python.com", "bob@hotmail.com"]},
...     {"firstName": "Carol", "id": 3, "emails": ["carol@linux.net"]},
... ]
>>> pdbuf.proto_normalize(people, type=Person, including_default_field_names=False)
  first_name  id
0      Alice   0
1        Bob   1
2      Carol   3
```

Nested repeated fields keep an index name for recursive joins:

```protobuf
message Shift {
  repeated Person workers = 1;
  google.protobuf.Timestamp start_time = 2;
}
```

```python
>>> shifts = [
...     {"workers": [
...         {"firstName": "alice", "emails": ["alice@www.com"]},
...         {"firstName": "bob", "emails": ["bob@python.com", "bob@www.com"]},
...     ], "startTime": "2022-07-11T13:00:00.000000Z"},
...     {"workers": [
...         {"firstName": "eve", "emails": ["eve@www.com"]},
...         {"firstName": "fred", "emails": []},
...     ], "startTime": "2022-07-11T21:00:00.000000Z"},
... ]
>>> df = pdbuf.proto_normalize(shifts)
>>> workers = pdbuf.proto_explode(shifts, "workers")
>>> emails = pdbuf.proto_explode(shifts, "workers.emails")
>>> df.join(workers).join(emails)
                   start_time first_name          emails
  workers
0 0       2022-07-11 13:00:00      alice   alice@www.com
  1       2022-07-11 13:00:00        bob  bob@python.com
  1       2022-07-11 13:00:00        bob     bob@www.com
1 2       2022-07-11 21:00:00        eve     eve@www.com
  3       2022-07-11 21:00:00       fred            None
```


shifts = [
    {"workers": [
        {"first_name": "alice", "emails": ["alice@www.com"]},
        {"first_name": "bob", "emails": ["bob@python.com", "bob@www.com"]},
    ], "start_time": "2022-07-11T13:00:00.000000Z"},
    {"workers": [
        {"first_name": "eve", "emails": ["eve@www.com"]},
        {"first_name": "fred", "emails": []},
    ], "start_time": "2022-07-11T21:00:00.000000Z"},
]
