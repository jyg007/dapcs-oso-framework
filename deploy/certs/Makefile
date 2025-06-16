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


.PRECIOUS: %.key %.csr %.fp
%.key:
	openssl genrsa -out $@ 4096
	chmod 0600 $@

%.csr: %.key
	openssl req -key $< -new -out $@ -nodes -subj '/C=US/O=IBM OSO/CN=$*/'

%.fp: %.key
	ssh-keygen -lf $< | awk 'BEGIN {ORS=""} {print $$2}' > $@

ca.crt: ca.csr
	openssl x509 -req -in $< \
		-signkey ca.key \
		-CAcreateserial -out $@ -days 365 \
		-extensions v3_ca -extfile ext

%.crt: %.csr ca.key ca.crt %.fp
	openssl x509 -req -in $< \
		-CAkey $(word 2,$^) -CA $(word 3,$^) \
		-CAcreateserial -out $@ -days 365 \
		-extensions v3_ca -extfile ext

.PHONY: clean
clean:
	rm *.{key,csr,crt,fp}
