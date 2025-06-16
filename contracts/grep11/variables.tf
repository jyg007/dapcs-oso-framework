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


variable "PREFIX" {
  type        = string
}

variable "IMAGE" {
  type        = string
  description = "GREP11 image name with registry"
}

variable "PORT" {
  type        = string
  description = "GREP11 port number"
  default     = "9876"
}

variable "HPCR_CERT" {
  type        = string
  description = "Public HPCR certificate for contract encryption"
  nullable    = true
  default     = null
}

variable "DEBUG" {
  type        = bool
  description = "Create debug contracts, plaintext"
  default     = false
}

variable "DOMAIN" {
  type        =  string
  description = "Crypto appliance domain"
}

variable "C16_CLIENT_HOST" {
  type        = string
  default     = "192.168.7.4"
  description = "Crypto appliance host endpoint"
}

variable "C16_CLIENT_PORT" {
  type       = string
  default    = "9001"
}

variable "C16_CLIENT_LOGLEVEL" {
  type        = string
  default     = "debug"
  validation {
    condition     = contains(["trace", "debug", "info", "warn", "err", "error", "critical", "off"], var.C16_CLIENT_LOGLEVEL)
    error_message = "Valid values for var: C16_CLIENT_LOGLEVEL are (trace, debug, info, warn, err, error, critical, off)."
  }
}

variable "C16_CLIENT_KEY" {
  type        = string
  description = "Crypto appliance client key"
}

variable "C16_CLIENT_CERT" {
  type        = string
  description = "Crypto appliance client certificate"
}

variable "C16_CA_CERT" {
  type        = string
  description = "Crypto appliance CA certificate"
}

variable "CERT_VALIDITY_PERIOD" {
  type = string
  description = "Length of time in hours that the conductor certificates are valid. After this point the conductor will need to be redeployed."
  default = "720"
}
