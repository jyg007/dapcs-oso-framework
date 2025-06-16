# Offline Signing Orchestrator Framework Contract Support

This document provides the necessary steps and examples to onboard the custom plugin and frontend/backend workloads
through the use of IBM HPVS contracts using terraform.

## Prerequisites

- OpenTofu
- Required terraform providers (hpcr, tls and local)

## frontend

The `frontend` directory contains the supporting files for HPVS contract generation which can be used within the Offline
Signing Orchestrator during the cold signing process. At a minimum, the `frontend-plugin` workload is required. In a
typical use case, the frontend plugin can communicate externally over the internet to obtain documents to sign and to
send signed documents back to the frontend. The frontend plugin should not be expected to be communicated to from
external sources. Additional container workloads can be added to the podman play if required to help faciliate the
operations required from the frontend plugin. The example provided here demonstrates a single frontend plugin workload.

### Update procedure

1. Update the `variables.tf` to include any additional required variables (if applicable)
1. Update the `terraform.tfvars.template` to include any additional required variables
1. Update the `user_data_frontend.tf` to include any additional usage of newly added variables for templating
1. Update the `frontend.yml.tftpl` to utilize additional variables or modifications to the podman play

### Testing

1. Copy the `terraform.tfvars.template` to `terraform.tfvars`
1. Update the `terraform.tfvars` with acceptable test values
1. Create the contract by running the `create-frontend.sh` script
1. If successful, the encrypted workload for the HPVS contract will appear under `output/frontend`

## grep11

If the backend service requires a grep11 service for signing operations, such as in the provided example here, a grep11
service can be started alongside the backend HPVS instance. The `grep11` directory contains the supporting files for HPVS
contract generation which can be used within the Offline Signing Orchestrator during the cold signing process.

The grep11 terraform will generate new client and server certificates required for m/TLS communication from the backend
service. The output of the terraform resides under the `backend/certs` directory. The contents of the public certificate
of the CA including the client certificate with client private key will go into the `terraform.tfvars` of the backend
service (documented below).


### Update procedure No changes are required here and can be used directly by the customer.

### Testing

1. Copy the `terraform.tfvars.template` to `terraform.tfvars`
1. Update the `terraform.tfvars` with acceptable test values
1. Create the contract by running the `create-grep11.sh` script
1. If successful, the encrypted workload for the HPVS contract will appear under `output/grep11`
1. Obtain the public CA certificate, client certificate and client key to be used in the next section from `certs/`

## backend

The `backend` directory contains the supporting files for HPVS contract generation which can be used within the Offline
Signing Orchestrator during the cold signing process. At a minimium, the `backend-plugin` workload is required. In a
typical use case, there is also an additional container for the signing service which also acts as the keystore. In the
example provided here, the [signing-server](https://github.com/IBM/signingserver) is used as this service which can
communicate with the grep11-c16 service (see below). If an onboarding ISV wants to utilize a their own signing service
or keystore, the example can be modified as such.

In this example, the signing-service container workload within the HPVS instance will be attached to an encrypted data
volume attached to the virtual machine, where the encryption is already provided by HPVS.

### Update procedure

1. Update the `variables.tf` to include any additional required variables (if applicable)
1. Update the `terraform.tfvars.template` to include any additional required variables
1. Update the `user_data_backend.tf` to include any additional usage of newly added variables for templating
1. Update the `backend.yml.tftpl` to utilize additional variables or modifications to the podman play

### Testing

1. Copy the `terraform.tfvars.template` to `terraform.tfvars`
1. Update the `terraform.tfvars` with acceptable test values (including the contents of the grep11 certs above)
1. Create the contract by running the `create-backend.sh` script
1. If successful, the encrypted workload for the HPVS contract will appear under `output/backend`

## Client procedures

Once tooling is provided to a client, the client can update the necessary terraform variables specific to their
environment and generate the encrypted workloads via the provided scripts:

- `./create-frontend.sh`
- `./create-grep11.sh`
- `./create-backend.sh`

Lastly, the client can obtain the encrypted workloads section required for Offline Signing Orchestrator:

`./get_workloads.sh`
