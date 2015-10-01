from flask import Flask, jsonify, request
from flasgger import Swagger

app = Flask(__name__)

Swagger(app)


@app.route("/recs", methods=['GET'])
def recs():
    """
    A simple test API
    This ednpoint does nothing
    Only returs "test"
    ---
    tags:
      - recsapi
    parameters:
      - name: size
        in: query
        type: string
        description: size of elements
    responses:
      200:
        description: A single user item
        schema:
          id: return_test
          properties:
            result:
              type: string
              description: The test
              default: 'test'
    """
    size = int(request.args.get('size', 1))
    return jsonify({"result": "test" * size})


@app.route("/test/<string:param_name>", methods=['GET'])
def test(param_name):
    """
    This single line goes in the header field and should contain a brief description of this function
    The following lines up to the 3 dashes goes in the "Implementation Notes" section
    for the function. This section can have any number of lines of text.
    ---
    tags:
      - function-name/title
    parameters:
      - name: param-name
        in: path
        type: string
        required: false
        description: description for this param; (in) type of param; (type) type on input data
    responses:
      200:
        description: description of this http response
        schema:
          id: return_string
          properties:
            result:
              type: string
              description: description of this property
              default: 'Default Value'
    """
    name = str(request.args.get('param_name', 1))
    print "name: %s" % name
    return jsonify({"result": "Default Value"})

app.run(debug=True)
#app.run(host="192.168.10.46", port=6969, debug=True)
