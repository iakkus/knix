#   Copyright 2020 The KNIX Authors
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import json

def handle(value, sapi):
    assert isinstance(value, dict)
    data = value

    response = {}
    response_data = {}

    success = False

    email = data["email"]
    storage_userid = data["storage_userid"]

    if "function" in data:
        function = data["function"]

        sapi.log(json.dumps(function))

        if "id" in function:
            functions = sapi.get(email + "_list_grains", True)
            if functions is not None and functions != "":
                functions = json.loads(functions)
                if function["id"] in functions.values():
                    #functionEnvironmentVariables = sapi.get(email + "_grain_environment_variables_" + function["id"], True)

                    dlc = sapi.get_privileged_data_layer_client(storage_userid)
                    functionEnvironmentVariables = dlc.get("grain_environment_variables_" + function["id"])
                    dlc.shutdown()

                    if functionEnvironmentVariables is None:
                        functionEnvironmentVariables = ""

                    f = {}
                    f["environment_variables"] = functionEnvironmentVariables

                    response_data["function"] = f
                    response_data["message"] = "Retrieved environment variables for function " + function["id"] + "."

                    success = True

                else:
                    response_data["message"] = "Couldn't retrieve function environment variables; no such function."
            else:
                response_data["message"] = "Couldn't retrieve function environment variables; no such function."
        else:
            response_data["message"] = "Couldn't retrieve function environment variables; malformed input."
    else:
        response_data["message"] = "Couldn't retrieve function environment variables; malformed input."

    if success:
        response["status"] = "success"
    else:
        response["status"] = "failure"

    response["data"] = response_data

    sapi.log(json.dumps(response))

    return response

