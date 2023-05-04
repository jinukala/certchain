import json
from typing import Dict,Tuple
from datetime import datetime
import re
from schema import Certificate

def validate(certData: Certificate):
    for key, value in certData.items():
        if key == 'issuedDate':
            try:
                date_format = "%d/%m/%Y"
                assert datetime.strptime(value, date_format)
            except ValueError:
                print("Validation Failed", key, ValueError)
        else:
            try:
                assert 0 < len(value) < 100
                assert re.match(r"[\s\w]+$", value)
            except ValueError:
                print("Validation Failed - ", key, ValueError)


class Certificate:
    def __init__(self, data: Certificate):
        validate(data)
        self._name = data["name"].upper()
        self._parentName = data["parentName"].upper()
        self._registeredNumber = data["registeredNumber"]
        self._issuedDate = data["issuedDate"]
        self._stream = data["stream"].upper()
        self._degree = data["degree"].upper()
        self._institution = data["institution"].upper()

    @property
    def name(self):
        return self._name

    @property
    def parentName(self):
        return self._parentName

    @property
    def registeredNumber(self):
        return self._registeredNumber

    @property
    def issuedDate(self):
        return self._issuedDate

    @property
    def stream(self):
        return self._stream

    @property
    def degree(self):
        return self._degree

    @property
    def institution(self):
        return self._institution

    def __repr__(self):
        out: Certificate = {
            "name": self._name,
            "parentName": self._parentName,
            "registeredNumber": self._registeredNumber,
            "issuedDate": self._issuedDate,
            "stream": self._stream,
            "degree": self._degree,
            "institution": self._institution
        }
        return out

    def __str__(self):
        return json.dumps(self.__repr__())