#
# (c) Copyright IBM Corp. 2025
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""OSO Datatypes."""

import json

from pydantic import BaseModel, ConfigDict, Field, field_validator


class V1_3:
    """Version 1.3."""

    class Document(BaseModel):
        """Document.

        Attributes
        ----------
        id : str
            Document ID.

        content : str
            Document content.

        metadata : str | None, default=None
            Document metadata.
        """

        id: str
        content: str
        metadata: str | None = None

        @field_validator(
            "metadata",
            mode="before",
        )
        @classmethod
        def validate_metadata(cls, metadata: str | None) -> str:
            """Fill metadata with empty string, if empty."""
            if metadata is None:
                return ""
            if isinstance(metadata, dict):
                return json.dumps(metadata)
            return metadata

    class DocumentList(BaseModel):
        """Document List.

        Attributes
        ----------
        documents : list[`.Document`], default=[]
            A list of `.Document`s.

        count : int
            A count of documents.
        """

        documents: list["Document"] = Field(default_factory=list)
        count: int

    class Error(BaseModel):
        """Error.

        Attributes
        ----------
        code : str
            A searchable code of the error.

        message : str
            A human readable message about the error.
        """

        code: str
        message: str

    class ComponentStatus(BaseModel):
        """Component Status.

        Attributes
        ----------
        status_code : int
            A HTTP status code.

        status : str
            A human readable message about the status.

        errors : list[`.Error`], default=[]
            A list of errors
        """

        status_code: int
        status: str
        errors: list["Error"] = Field(default_factory=list)
        model_config = ConfigDict(extra="allow")


# Define latest
Document = V1_3.Document
DocumentList = V1_3.DocumentList
Error = V1_3.Error
ComponentStatus = V1_3.ComponentStatus
