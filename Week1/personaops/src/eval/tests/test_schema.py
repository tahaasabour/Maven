import jsonschema as js

SCHEMA = {
  "type":"object",
  "required":["title","body","style","citations"],
  "properties":{
    "title":{"type":"string"},
    "body":{"type":"string"},
    "style":{"type":"string"},
    "citations":{"type":"array","items":{"type":"string"}}
  }
}

def test_valid_shape(sample_output):
    js.validate(sample_output, SCHEMA)