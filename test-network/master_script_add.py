
import os
import shutil

def add_orgs_to_channel_script(num_orgs, file_path = "scripts/createChannel.sh"):
    # Read the original file content
    with open(file_path, 'r') as file:
        lines = file.readlines()
    # Save a Backup 
    with open(file_path + ".bak", 'w') as file:
        file.writelines(lines)

    # Find the positions to insert the new lines
    join_position = None
    anchor_position = None

    for i, line in enumerate(lines):
        if "joinChannel 2" in line:
            join_position = i + 1  # Insert after the last org2 join
        if "setAnchorPeer 2" in line:
            anchor_position = i + 1  # Insert after the last org2 anchor

    if join_position is None or anchor_position is None:
        print("Could not find the expected positions in the file.")
        return

    # Generate new lines for organizations from 3 to num_orgs
    join_lines = []
    anchor_lines = []
    
    for org_num in range(3, num_orgs + 3):
        join_lines.append(f'infoln "Joining org{org_num} peer to the channel..."\n')
        join_lines.append(f"joinChannel {org_num}\n")
        
        anchor_lines.append(f'infoln "Setting anchor peer for org{org_num}..."\n')
        anchor_lines.append(f"setAnchorPeer {org_num}\n")

    # Insert the new lines in the appropriate positions
    updated_lines = (
        lines[:join_position] + join_lines + lines[join_position:anchor_position] + anchor_lines + lines[anchor_position:]
    )

    # Write the updated content back to the file
    with open(file_path, 'w') as file:
        file.writelines(updated_lines)

    print(f"Successfully added configurations for organizations 3 to {num_orgs}.")



def add_orgs_to_ccp_generate(num_orgs, file_path = "organizations/ccp-generate.sh"):
    # Save a Backup 
    with open(file_path, 'r') as file:
        lines = file.readlines()
    with open(file_path + ".bak", 'w') as file:
        file.writelines(lines)

    # Open the ccp-generate.sh file for appending
    with open(file_path, 'a') as file:
        for org_num in range(3, num_orgs + 3):
            # Calculate P0PORT and CAPORT for the organization
            p0port = 7051 + (org_num - 1) * 2000
            caport = 7054 + (org_num - 1) * 1000

            # Define the file paths for PEERPEM and CAPEM
            peerpem = f"organizations/peerOrganizations/org{org_num}.example.com/tlsca/tlsca.org{org_num}.example.com-cert.pem"
            capem = f"organizations/peerOrganizations/org{org_num}.example.com/ca/ca.org{org_num}.example.com-cert.pem"

            # Create the entire configuration as a big f-string
            org_config = f"""
ORG={org_num}
P0PORT={p0port}
CAPORT={caport}
PEERPEM={peerpem}
CAPEM={capem}

echo "$(json_ccp $ORG $P0PORT $CAPORT $PEERPEM $CAPEM)" > organizations/peerOrganizations/org{org_num}.example.com/connection-org{org_num}.json
echo "$(yaml_ccp $ORG $P0PORT $CAPORT $PEERPEM $CAPEM)" > organizations/peerOrganizations/org{org_num}.example.com/connection-org{org_num}.yaml
"""

            # Write the organization-specific configuration to the file
            file.write(org_config)
    
    print(f"Successfully added organizations Org3 to Org{num_orgs} to {file_path}")



def add_organizations_after_existing(num_orgs, file_path = "./configtx/configtx.yaml"):
    
    # Read the existing file
    with open(file_path, 'r') as file:
        lines = file.readlines()
    # Save a Backup 
    with open(file_path + ".bak", 'w') as file:
        file.writelines(lines)

    # Determine where to insert the new organizations
    org2_block_end = None
    profiles_block_end = None
    for i, line in enumerate(lines):
        # print(line)
        if line.strip().startswith(f"Rule: \"OR('Org2MSP.peer')\""):
            # Find the end of the &Org2 block
            org2_block_end = i
        if line.strip().startswith("- *Org2"):
            # Find the end of the Profiles block
            profiles_block_end = i

    # Create new organizations configurations
    new_orgs = []
    new_orgs_in_channel = []
    for org_num in range(3, num_orgs + 3):

        new_orgs_in_channel
        org_config = (
            f"  - &Org{org_num}\n"
            f"    # DefaultOrg defines the organization which is used in the sampleconfig\n"
            f"    # of the fabric.git development environment\n"
            f"    Name: Org{org_num}MSP\n"
            f"    # ID to load the MSP definition as\n"
            f"    ID: Org{org_num}MSP\n"
            f"    MSPDir: ../organizations/peerOrganizations/org{org_num}.example.com/msp\n"
            f"    # Policies defines the set of policies at this level of the config tree\n"
            f"    # For organization policies, their canonical path is usually\n"
            f"    #   /Channel/<Application|Orderer>/<OrgName>/<PolicyName>\n"
            f"    Policies:\n"
            f"      Readers:\n"
            f"        Type: Signature\n"
            f"        Rule: \"OR('Org{org_num}MSP.admin', 'Org{org_num}MSP.peer', 'Org{org_num}MSP.client')\"\n"
            f"      Writers:\n"
            f"        Type: Signature\n"
            f"        Rule: \"OR('Org{org_num}MSP.admin', 'Org{org_num}MSP.client')\"\n"
            f"      Admins:\n"
            f"        Type: Signature\n"
            f"        Rule: \"OR('Org{org_num}MSP.admin')\"\n"
            f"      Endorsement:\n"
            f"        Type: Signature\n"
            f"        Rule: \"OR('Org{org_num}MSP.peer')\"\n"
        )

        new_orgs.append(org_config)

    # Insert new organizations configurations into the file
    with open(file_path, 'w') as file:
        for i, line in enumerate(lines):
            file.write(line)
            if i == org2_block_end:
                file.write('\n'.join(new_orgs) + '\n')
            if i == profiles_block_end:
                for org_num in range(3, num_orgs + 3):
                    file.write(f"        - *Org{org_num}\n")



def create_crypto_config_files(num_orgs, base_dir = "./organizations/cryptogen/"):
    # Ensure the base directory exists
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    # Loop through organization numbers (starting from 3 to num_orgs)
    for org_num in range(3, num_orgs + 3):
        # Define the file name and path
        file_name = f"crypto-config-org{org_num}.yaml"
        file_path = os.path.join(base_dir, file_name)
        
        # Define the content for each file
        content = f"""# Copyright IBM Corp. All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0
#

# ---------------------------------------------------------------------------
# "PeerOrgs" - Definition of organizations managing peer nodes
# ---------------------------------------------------------------------------
PeerOrgs:
  # ---------------------------------------------------------------------------
  # Org{org_num}
  # ---------------------------------------------------------------------------
  - Name: Org{org_num}
    Domain: org{org_num}.example.com
    EnableNodeOUs: true
    # ---------------------------------------------------------------------------
    # "Specs"
    # ---------------------------------------------------------------------------
    # Uncomment this section to enable the explicit definition of hosts in your
    # configuration.  Most users will want to use Template, below
    #
    # Specs is an array of Spec entries.  Each Spec entry consists of two fields:
    #   - Hostname:   (Required) The desired hostname, sans the domain.
    #   - CommonName: (Optional) Specifies the template or explicit override for
    #                 the CN.  By default, this is the template:
    #
    #                              "{{{{.Hostname}}}}.{{{{.Domain}}}}"
    #
    #                 which obtains its values from the Spec.Hostname and
    #                 Org.Domain, respectively.
    # ---------------------------------------------------------------------------
    #   - Hostname: foo # implicitly "foo.org{org_num}.example.com"
    #     CommonName: foo27.org{org_num}.example.com # overrides Hostname-based FQDN set above
    #   - Hostname: bar
    #   - Hostname: baz
    # ---------------------------------------------------------------------------
    # "Template"
    # ---------------------------------------------------------------------------
    # Allows for the definition of 1 or more hosts that are created sequentially
    # from a template. By default, this looks like "peer%d" from 0 to Count-1.
    # You may override the number of nodes (Count), the starting index (Start)
    # or the template used to construct the name (Hostname).
    #
    # Note: Template and Specs are not mutually exclusive.  You may define both
    # sections and the aggregate nodes will be created for you.  Take care with
    # name collisions
    # ---------------------------------------------------------------------------
    Template:
      Count: 1
      SANS:
        - localhost
      # Start: 5
      # Hostname: {{{{.Prefix}}}}{{{{.Index}}}} # default
    # ---------------------------------------------------------------------------
    # "Users"
    # ---------------------------------------------------------------------------
    # Count: The number of user accounts _in addition_ to Admin
    # ---------------------------------------------------------------------------
    Users:
      Count: 1
"""

        # Write the content to the file
        with open(file_path, 'w') as file:
            file.write(content)

    print(f"{num_orgs} organization config files created in {base_dir}.")


def add_orgs_to_setGlobals(num_orgs, file_path = "./scripts/envVar.sh"):
    # Read the existing file
    with open(file_path, 'r') as file:
        lines = file.readlines()
    # Save a Backup 
    with open(file_path + ".bak", 'w') as file:
        file.writelines(lines)

    # Find the position of the line where we should insert the new lines
    insert_position = None
    peerPositon = None
    for i, line in enumerate(lines):
        if "export CORE_PEER_ADDRESS=localhost:11051" in line:
            insert_position = i + 1  # Insert after this line
            break
    for i, line in enumerate(lines):
        if "export PEER0_ORG3_CA=${TEST_NETWORK_HOME}/organizations/peerOrganizations/org3.example.com/tlsca/tlsca.org3.example.com-cert.pem" in line:
            peerPositon = i + 1  # Insert after this line
            break


    if insert_position is None or peerPositon is None:
        print("Could not find the line 'export CORE_PEER_ADDRESS=localhost:11051' in the file.")
        return

    # Generate new lines for organizations from 4 to num_orgs
    new_lines = []
    for org_num in range(4, num_orgs + 3):
        new_lines.append(f"  elif [ $USING_ORG -eq {org_num} ]; then\n")
        new_lines.append(f"    export CORE_PEER_LOCALMSPID=Org{org_num}MSP\n")
        new_lines.append(f"    export CORE_PEER_TLS_ROOTCERT_FILE=$PEER0_ORG{org_num}_CA\n")
        new_lines.append(f"    export CORE_PEER_MSPCONFIGPATH=${{TEST_NETWORK_HOME}}/organizations/peerOrganizations/org{org_num}.example.com/users/Admin@org{org_num}.example.com/msp\n")
        new_lines.append(f"    export CORE_PEER_ADDRESS=localhost:{7051 + (org_num - 1) * 2000}\n")

    peer_new_lines = []
    for org_num in range(4, num_orgs + 3):
        peer_new_lines.append(f"export PEER0_ORG{org_num}_CA=${{TEST_NETWORK_HOME}}/organizations/peerOrganizations/org{org_num}.example.com/tlsca/tlsca.org{org_num}.example.com-cert.pem\n")

    # Insert the new lines immediately after the identified position
    updated_lines = lines[:insert_position] + new_lines + lines[insert_position:]
    peer_updated_lines = updated_lines[:peerPositon] + peer_new_lines + updated_lines[peerPositon:]
    # Write the updated content back to the file
    with open(file_path, 'w') as file:
        file.writelines(peer_updated_lines)

    print(f"Successfully added configurations for organizations 4 to {num_orgs + 3} after the address line for Org3.")



def add_orgs_to_network_sh(num_orgs, file_path = "./network.sh"):
    # Read the existing file
    with open(file_path, 'r') as file:
        lines = file.readlines()
    # Save a Backup 
    with open(file_path + ".bak", 'w') as file:
        file.writelines(lines)

    # Find the index where Org2 identities are created
    Org_2_index = None
    insert_index = None
    ca_insert_index = None
    down_index = None
    test_net_index = None

    for i, line in enumerate(lines):
        if "infoln \"Creating Org2 Identities\"" in line:
            Org_2_index = i + 1
        if Org_2_index is not None and "infoln \"Creating Orderer Org Identities\"" in line:
            print(line)
            insert_index = i - 1
            break

    for i, line in enumerate(lines):
        if "createOrg2" in line:
            ca_insert_index = i + 1
            break

    for i, line in enumerate(lines): 
        if "organizations/fabric-ca/org2/fabric-ca-server.db'" in line:
            down_index = i + 1
            break

    line_to_insert = "  COMPOSE_FILE_BASE=compose-test-net.yaml\n"
    for i, line in enumerate(lines): 
        if "COMPOSE_BASE_FILES=" in line:
            test_net_index = i
            break


    # Create the lines to add for the new organizations (Org3 to OrgN)
    new_org_lines = []
    for org_num in range(3, num_orgs + 3):
        org_block = (
            f'\n    infoln "Creating Org{org_num} Identities"\n'
            f'    set -x\n'
            f'    cryptogen generate --config=./organizations/cryptogen/crypto-config-org{org_num}.yaml --output="organizations"\n'
            f'    res=$?\n'
            f'    {{ set +x; }} 2>/dev/null\n'
            f'    if [ $res -ne 0 ]; then\n'
            f'      fatalln "Failed to generate certificates..."\n'
            f'    fi\n'
        )
        new_org_lines.append(org_block)

    # Generate the new lines for organizations
    new_lines = []
    for i in range(3, num_orgs + 3):
        new_lines.append(f"\n    infoln \"Creating Org{i} Identities\"\n\n")
        new_lines.append(f"    createOrg{i}\n")

    new_down_lines = []
    for org_num in range(3, num_orgs + 3):  # Start from org3
        new_line = f"    ${{CONTAINER_CLI}} run --rm -v \"$(pwd):/data\" busybox sh -c 'cd /data && rm -rf organizations/fabric-ca/org{org_num}/msp organizations/fabric-ca/org{org_num}/tls-cert.pem organizations/fabric-ca/org{org_num}/ca-cert.pem organizations/fabric-ca/org{org_num}/IssuerPublicKey organizations/fabric-ca/org{org_num}/IssuerRevocationPublicKey organizations/fabric-ca/org{org_num}/fabric-ca-server.db'\n"
        new_down_lines.append(new_line)
    # Insert the new org lines after the Org2 block
    if ca_insert_index is not None and insert_index is not None and down_index is not None and test_net_index is not None:
        lines = lines[:down_index] + new_down_lines + lines[down_index:]
        lines.insert(test_net_index, line_to_insert)
        lines = lines[:ca_insert_index] + new_lines + lines[ca_insert_index:]
        lines = lines[:insert_index] + new_org_lines + lines[insert_index:]
        # Write the updated content back to the file
        with open(file_path, 'w') as file:
            file.writelines(lines)

        print(f"Successfully added {num_orgs} organizations to {file_path}.")
    else:
        print("Could not find the position to insert the new organizations.")


def add_anchor_peer_update_blocks(num_orgs, file_path = "scripts/setAnchorPeer.sh"):
    # Read the existing file
    with open(file_path, 'r') as file:
        lines = file.readlines()
    # Save a Backup 
    with open(file_path + ".bak", 'w') as file:
        file.writelines(lines)

    # Find the position to insert the new lines
    insert_position = None
    for i, line in enumerate(lines):
        if "PORT=11051" in line:
            insert_position = i + 1  # Insert after the elif block for Org 3
            break

    if insert_position is None:
        print("Could not find the expected position in the file.")
        return

    # Generate new elif blocks for organizations from 4 to num_orgs
    new_blocks = []
    port = 13051
    for org_num in range(4, num_orgs + 3):
        new_blocks.append(f"  elif [ $ORG -eq {org_num} ]; then\n")
        new_blocks.append(f'    HOST="peer0.org{org_num}.example.com"\n')
        new_blocks.append(f"    PORT={port}\n")
        port += 2000

    # Insert the new lines in the appropriate position
    updated_lines = lines[:insert_position] + new_blocks + lines[insert_position:]

    # Write the updated content back to the file
    with open(file_path, 'w') as file:
        file.writelines(updated_lines)

    print(f"Successfully added anchor peer update blocks for organizations 4 to {num_orgs + 4}.")


def add_organizations(num_orgs, file_path = './compose/compose-test-net.yaml'):
    # Read the existing file
    with open(file_path, 'r') as file:
        lines = file.readlines()
    # Save a Backup 
    with open(file_path + ".bak", 'w') as file:
        file.writelines(lines)
    
    new_volumes = []
    new_services = []

    # Generate new volumes and services
    for org_num in range(3, num_orgs + 3):
        # Generate volumes
        new_volumes.append(f"  peer0.org{org_num}.example.com:\n")
        
        # Generate services
        peer_template = [
            "\n",
            f"  peer0.org{org_num}.example.com:\n",
            f"    container_name: peer0.org{org_num}.example.com\n",
            "    image: hyperledger/fabric-peer:latest\n",
            "    labels:\n",
            "      service: hyperledger-fabric\n",
            "    environment:\n",
            "      - FABRIC_CFG_PATH=/etc/hyperledger/peercfg\n",
            "      - FABRIC_LOGGING_SPEC=INFO\n",
            "      - CORE_PEER_TLS_ENABLED=true\n",
            "      - CORE_PEER_PROFILE_ENABLED=false\n",
            "      - CORE_PEER_TLS_CERT_FILE=/etc/hyperledger/fabric/tls/server.crt\n",
            "      - CORE_PEER_TLS_KEY_FILE=/etc/hyperledger/fabric/tls/server.key\n",
            "      - CORE_PEER_TLS_ROOTCERT_FILE=/etc/hyperledger/fabric/tls/ca.crt\n",
            f"      - CORE_PEER_ID=peer0.org{org_num}.example.com\n",
            f"      - CORE_PEER_ADDRESS=peer0.org{org_num}.example.com:{7051 + (org_num-1) * 2000}\n",
            f"      - CORE_PEER_LISTENADDRESS=0.0.0.0:{7051 + (org_num-1) * 2000}\n",
            f"      - CORE_PEER_CHAINCODEADDRESS=peer0.org{org_num}.example.com:{7052 + (org_num-1) * 2000}\n",
            f"      - CORE_PEER_CHAINCODELISTENADDRESS=0.0.0.0:{7052 + (org_num-1) * 2000}\n",
            f"      - CORE_PEER_GOSSIP_EXTERNALENDPOINT=peer0.org{org_num}.example.com:{7051 + (org_num-1) * 2000}\n",
            f"      - CORE_PEER_GOSSIP_BOOTSTRAP=peer0.org{org_num}.example.com:{7051 + (org_num-1) * 2000}\n",
            f"      - CORE_PEER_LOCALMSPID=Org{org_num}MSP\n",
            "      - CORE_PEER_MSPCONFIGPATH=/etc/hyperledger/fabric/msp\n",
            f"      - CORE_OPERATIONS_LISTENADDRESS=peer0.org{org_num}.example.com:{9443 + org_num}\n",
            "      - CORE_METRICS_PROVIDER=prometheus\n",
            f"      - CHAINCODE_AS_A_SERVICE_BUILDER_CONFIG={{\"peername\":\"peer0org{org_num}\"}}\n",
            "      - CORE_CHAINCODE_EXECUTETIMEOUT=300s\n",
            "    volumes:\n",
            f"      - ../organizations/peerOrganizations/org{org_num}.example.com/peers/peer0.org{org_num}.example.com:/etc/hyperledger/fabric\n",
            f"      - peer0.org{org_num}.example.com:/var/hyperledger/production\n",
            "    working_dir: /root\n",
            "    command: peer node start\n",
            f"    ports:\n",
            f"      - {7051 + (org_num-1) * 2000}:{7051 + (org_num-1) * 2000}\n",
            f"      - {9443 + org_num}:{9443 + org_num}\n",
            "    networks:\n",
            "      - test\n"
        ]
        
        new_services.extend(peer_template)
    
   # Find the insertion points
    insert_volumes_index = lines.index('volumes:\n') + 1

    # Insert volumes
    for i in range(insert_volumes_index, len(lines)):
        if lines[i].startswith('  peer0.org2.example.com:'):
            insert_volumes_index = i + 1
            break
    lines.insert(insert_volumes_index, ''.join(new_volumes))

    # Append services at the end
    lines.append(''.join(new_services))

    # Write the changes to the file
    with open(file_path, 'w') as file:
        file.writelines(lines)


def add_peers_to_docker_compose(num_orgs, file_path = './compose/docker/docker-compose-test-net.yaml'):
    # Read the existing file
    with open(file_path, 'r') as file:
        lines = file.readlines()
    # Save a Backup 
    with open(file_path + ".bak", 'w') as file:
        file.writelines(lines)

    # Add new peer configurations
    new_peers = []
    for org_num in range(3, num_orgs + 3):
        peer_config = (
             "\n"
            f"  peer0.org{org_num}.example.com:\n"
            f"    container_name: peer0.org{org_num}.example.com\n"
            f"    image: hyperledger/fabric-peer:latest\n"
            f"    labels:\n"
            f"      service: hyperledger-fabric\n"
            f"    environment:\n"
            f"      #Generic peer variables\n"
            f"      - CORE_VM_ENDPOINT=unix:///host/var/run/docker.sock\n"
            f"      - CORE_VM_DOCKER_HOSTCONFIG_NETWORKMODE=fabric_test\n"
            f"    volumes:\n"
            f"      - ./docker/peercfg:/etc/hyperledger/peercfg\n"
             "      - ${DOCKER_SOCK}:/host/var/run/docker.sock\n"
        )
        new_peers.extend(peer_config)

    # Append services at the end
    lines.append(''.join(new_peers))

    # Write the changes to the file
    with open(file_path, 'w') as file:
        file.writelines(lines)

def add_org_to_setOrgEnv(num_orgs, file_path="setOrgEnv.sh"):
    # Create a backup of the original file
    backup_file = file_path + ".bak"
    with open(file_path, "r") as original:
        original_content = original.readlines()
    with open(backup_file, "w") as backup:
        backup.writelines(original_content)

    # Modify the original file
    with open(file_path, "w") as f:
        for line in original_content:
            # Write the existing line
            f.write(line)
            
            # Add new CA definitions if the ORDERER_CA line is encountered
            if "PEER0_ORG3_CA=${DIR}/test-network/organizations/peerOrganizations/org3.example.com/tlsca/tlsca.org3.example.com-cert.pem" in line:
                for i in range(4, num_orgs + 3):
                    f.write(f"PEER0_ORG{i}_CA=${{DIR}}/test-network/organizations/peerOrganizations/org{i}.example.com/tlsca/tlsca.org{i}.example.com-cert.pem\n")

            # Add new organization conditions after the "elif" for Org2
            if '   CORE_PEER_TLS_ROOTCERT_FILE=${DIR}/test-network/organizations/peerOrganizations/org2.example.com/tlsca/tlsca.org2.example.com-cert.pem' in line:
                for i in range(3, num_orgs + 3):
                    f.write(f"""
elif [[ ${{ORG,,}} == "org{i}" || ${{ORG,,}} == "magnetocorp" ]]; then

   CORE_PEER_LOCALMSPID=Org{i}MSP
   CORE_PEER_MSPCONFIGPATH=${{DIR}}/test-network/organizations/peerOrganizations/org{i}.example.com/users/Admin@org{i}.example.com/msp
   CORE_PEER_ADDRESS=localhost:{7051 + (i - 1) * 2000}
   CORE_PEER_TLS_ROOTCERT_FILE=${{DIR}}/test-network/organizations/peerOrganizations/org{i}.example.com/tlsca/tlsca.org{i}.example.com-cert.pem
""")

            # Add new CA echo statements at the output section
            if 'echo "PEER0_ORG3_CA=${PEER0_ORG3_CA}"' in line:
                for i in range(4, num_orgs + 3):
                    f.write(f"echo \"PEER0_ORG{i}_CA=${{PEER0_ORG{i}_CA}}\"\n")

    print(f"Backup created at {backup_file} and changes made to {file_path}")

def add_orgs_to_registerEnroll(num_orgs):
    filename = "./organizations/fabric-ca/registerEnroll.sh"
    # Create a backup before modifying the script
    backup_filename = filename + ".bak"
    if os.path.exists(filename):
        shutil.copy2(filename, backup_filename)
        print(f"Backup created: {backup_filename}")

    TEMPLATE = """function createOrg{org_number}() {{
  infoln "Enrolling the CA admin"
  mkdir -p organizations/peerOrganizations/org{org_number}.example.com/

  export FABRIC_CA_CLIENT_HOME=${{PWD}}/organizations/peerOrganizations/org{org_number}.example.com/

  set -x
  fabric-ca-client enroll -u https://admin:adminpw@localhost:{ca_port} --caname ca-org{org_number} --tls.certfiles "${{PWD}}/organizations/fabric-ca/org{org_number}/ca-cert.pem"
  {{ set +x; }} 2>/dev/null

  echo 'NodeOUs:
  Enable: true
  ClientOUIdentifier:
    Certificate: cacerts/localhost-{ca_port}-ca-org{org_number}.pem
    OrganizationalUnitIdentifier: client
  PeerOUIdentifier:
    Certificate: cacerts/localhost-{ca_port}-ca-org{org_number}.pem
    OrganizationalUnitIdentifier: peer
  AdminOUIdentifier:
    Certificate: cacerts/localhost-{ca_port}-ca-org{org_number}.pem
    OrganizationalUnitIdentifier: admin
  OrdererOUIdentifier:
    Certificate: cacerts/localhost-{ca_port}-ca-org{org_number}.pem
    OrganizationalUnitIdentifier: orderer' > "${{PWD}}/organizations/peerOrganizations/org{org_number}.example.com/msp/config.yaml"

  # Since the CA serves as both the organization CA and TLS CA, copy the org's root cert that was generated by CA startup into the org level ca and tlsca directories

  # Copy org{org_number}'s CA cert to org1's /msp/tlscacerts directory (for use in the channel MSP definition)
  mkdir -p "${{PWD}}/organizations/peerOrganizations/org{org_number}.example.com/msp/tlscacerts"
  cp "${{PWD}}/organizations/fabric-ca/org{org_number}/ca-cert.pem" "${{PWD}}/organizations/peerOrganizations/org{org_number}.example.com/msp/tlscacerts/ca.crt"

  # Copy org{org_number}'s CA cert to org1's /tlsca directory (for use by clients)
  mkdir -p "${{PWD}}/organizations/peerOrganizations/org{org_number}.example.com/tlsca"
  cp "${{PWD}}/organizations/fabric-ca/org{org_number}/ca-cert.pem" "${{PWD}}/organizations/peerOrganizations/org{org_number}.example.com/tlsca/tlsca.org{org_number}.example.com-cert.pem"

  # Copy org{org_number}'s CA cert to org1's /ca directory (for use by clients)
  mkdir -p "${{PWD}}/organizations/peerOrganizations/org{org_number}.example.com/ca"
  cp "${{PWD}}/organizations/fabric-ca/org{org_number}/ca-cert.pem" "${{PWD}}/organizations/peerOrganizations/org{org_number}.example.com/ca/ca.org{org_number}.example.com-cert.pem"

  infoln "Registering peer0"
  set -x
  fabric-ca-client register --caname ca-org{org_number} --id.name peer0 --id.secret peer0pw --id.type peer --tls.certfiles "${{PWD}}/organizations/fabric-ca/org{org_number}/ca-cert.pem"
  {{ set +x; }} 2>/dev/null

  infoln "Registering user"
  set -x
  fabric-ca-client register --caname ca-org{org_number} --id.name user1 --id.secret user1pw --id.type client --tls.certfiles "${{PWD}}/organizations/fabric-ca/org{org_number}/ca-cert.pem"
  {{ set +x; }} 2>/dev/null

  infoln "Registering the org admin"
  set -x
  fabric-ca-client register --caname ca-org{org_number} --id.name org{org_number}admin --id.secret org{org_number}adminpw --id.type admin --tls.certfiles "${{PWD}}/organizations/fabric-ca/org{org_number}/ca-cert.pem"
  {{ set +x; }} 2>/dev/null

  infoln "Generating the peer0 msp"
  set -x
  fabric-ca-client enroll -u https://peer0:peer0pw@localhost:{ca_port} --caname ca-org{org_number} -M "${{PWD}}/organizations/peerOrganizations/org{org_number}.example.com/peers/peer0.org{org_number}.example.com/msp" --tls.certfiles "${{PWD}}/organizations/fabric-ca/org{org_number}/ca-cert.pem"
  {{ set +x; }} 2>/dev/null

  cp "${{PWD}}/organizations/peerOrganizations/org{org_number}.example.com/msp/config.yaml" "${{PWD}}/organizations/peerOrganizations/org{org_number}.example.com/peers/peer0.org{org_number}.example.com/msp/config.yaml"

  infoln "Generating the peer0-tls certificates"
  set -x
  fabric-ca-client enroll -u https://peer0:peer0pw@localhost:{ca_port} --caname ca-org{org_number} -M "${{PWD}}/organizations/peerOrganizations/org{org_number}.example.com/peers/peer0.org{org_number}.example.com/tls" --enrollment.profile tls --csr.hosts peer0.org{org_number}.example.com --csr.hosts localhost --tls.certfiles "${{PWD}}/organizations/fabric-ca/org{org_number}/ca-cert.pem"
  {{ set +x; }} 2>/dev/null

  # Copy the tls CA cert, server cert, server keystore to well known file names in the peer's tls directory that are referenced by peer startup config
  cp "${{PWD}}/organizations/peerOrganizations/org{org_number}.example.com/peers/peer0.org{org_number}.example.com/tls/tlscacerts/"* "${{PWD}}/organizations/peerOrganizations/org{org_number}.example.com/peers/peer0.org{org_number}.example.com/tls/ca.crt"
  cp "${{PWD}}/organizations/peerOrganizations/org{org_number}.example.com/peers/peer0.org{org_number}.example.com/tls/signcerts/"* "${{PWD}}/organizations/peerOrganizations/org{org_number}.example.com/peers/peer0.org{org_number}.example.com/tls/server.crt"
  cp "${{PWD}}/organizations/peerOrganizations/org{org_number}.example.com/peers/peer0.org{org_number}.example.com/tls/keystore/"* "${{PWD}}/organizations/peerOrganizations/org{org_number}.example.com/peers/peer0.org{org_number}.example.com/tls/server.key"

  infoln "Generating the user msp"
  set -x
  fabric-ca-client enroll -u https://user1:user1pw@localhost:{ca_port} --caname ca-org{org_number} -M "${{PWD}}/organizations/peerOrganizations/org{org_number}.example.com/users/User1@org{org_number}.example.com/msp" --tls.certfiles "${{PWD}}/organizations/fabric-ca/org{org_number}/ca-cert.pem"
  {{ set +x; }} 2>/dev/null

  cp "${{PWD}}/organizations/peerOrganizations/org{org_number}.example.com/msp/config.yaml" "${{PWD}}/organizations/peerOrganizations/org{org_number}.example.com/users/User1@org{org_number}.example.com/msp/config.yaml"

  infoln "Generating the org admin msp"
  set -x
  fabric-ca-client enroll -u https://org{org_number}admin:org{org_number}adminpw@localhost:{ca_port} --caname ca-org{org_number} -M "${{PWD}}/organizations/peerOrganizations/org{org_number}.example.com/users/Admin@org{org_number}.example.com/msp" --tls.certfiles "${{PWD}}/organizations/fabric-ca/org{org_number}/ca-cert.pem"
  {{ set +x; }} 2>/dev/null

  cp "${{PWD}}/organizations/peerOrganizations/org{org_number}.example.com/msp/config.yaml" "${{PWD}}/organizations/peerOrganizations/org{org_number}.example.com/users/Admin@org{org_number}.example.com/msp/config.yaml"
}}"""
    with open(filename, "a") as f:
        start_org = 3  # Organizations start from org3
        for i in range(start_org, start_org + num_orgs):
            ca_port = 7054 + (i - 1) * 1000  # Increment CA port by 2000 per org
            org_config = TEMPLATE.format(org_number=i, ca_port=ca_port)
            f.write("\n" + org_config + "\n")

    print(f"Added {num_orgs} organizations to {filename}.")

def add_org_to_fabricca(num_orgs):
    base_dir = "./organizations/fabric-ca/"
    # Loop through organization numbers (starting from 3 to num_orgs+3)
    for org_num in range(3, num_orgs + 3):
        org_name = f"org{org_num}"
        org_dir = os.path.join(base_dir, org_name)  # Directory for each org
        file_path = os.path.join(org_dir, "fabric-ca-server-config.yaml")

        # Ensure the organization-specific directory exists
        os.makedirs(org_dir, exist_ok=True)

        # Define the content for each file
        content = f"""#############################################################################
#   This is a configuration file for the fabric-ca-server command.
#
#   COMMAND LINE ARGUMENTS AND ENVIRONMENT VARIABLES
#   ------------------------------------------------
#   Each configuration element can be overridden via command line
#   arguments or environment variables.  The precedence for determining
#   the value of each element is as follows:
#   1) command line argument
#      Examples:
#      a) --port 443
#         To set the listening port
#      b) --ca.keyfile ../mykey.pem
#         To set the "keyfile" element in the "ca" section below;
#         note the '.' separator character.
#   2) environment variable
#      Examples:
#      a) FABRIC_CA_SERVER_PORT=443
#         To set the listening port
#      b) FABRIC_CA_SERVER_CA_KEYFILE="../mykey.pem"
#         To set the "keyfile" element in the "ca" section below;
#         note the '_' separator character.
#   3) configuration file
#   4) default value (if there is one)
#      All default values are shown beside each element below.
#
#   FILE NAME ELEMENTS
#   ------------------
#   The value of all fields whose name ends with "file" or "files" are
#   name or names of other files.
#   For example, see "tls.certfile" and "tls.clientauth.certfiles".
#   The value of each of these fields can be a simple filename, a
#   relative path, or an absolute path.  If the value is not an
#   absolute path, it is interpretted as being relative to the location
#   of this configuration file.
#
#############################################################################

# Version of config file
version: 1.2.0

# Server's listening port (default: 7054)
port: 7054

# Enables debug logging (default: false)
debug: false

# Size limit of an acceptable CRL in bytes (default: 512000)
crlsizelimit: 512000

#############################################################################
#  TLS section for the server's listening port
#
#  The following types are supported for client authentication: NoClientCert,
#  RequestClientCert, RequireAnyClientCert, VerifyClientCertIfGiven,
#  and RequireAndVerifyClientCert.
#
#  Certfiles is a list of root certificate authorities that the server uses
#  when verifying client certificates.
#############################################################################
tls:
  # Enable TLS (default: false)
  enabled: true
  # TLS for the server's listening port
  certfile:
  keyfile:
  clientauth:
    type: noclientcert
    certfiles:

#############################################################################
#  The CA section contains information related to the Certificate Authority
#  including the name of the CA, which should be unique for all members
#  of a blockchain network.  It also includes the key and certificate files
#  used when issuing enrollment certificates (ECerts) and transaction
#  certificates (TCerts).
#  The chainfile (if it exists) contains the certificate chain which
#  should be trusted for this CA, where the 1st in the chain is always the
#  root CA certificate.
#############################################################################
ca:
  # Name of this CA
  name: {org_name.capitalize()}CA
  # Key file (is only used to import a private key into BCCSP)
  keyfile:
  # Certificate file (default: ca-cert.pem)
  certfile:
  # Chain file
  chainfile:

#############################################################################
#  The gencrl REST endpoint is used to generate a CRL that contains revoked
#  certificates. This section contains configuration options that are used
#  during gencrl request processing.
#############################################################################
crl:
  # Specifies expiration for the generated CRL. The number of hours
  # specified by this property is added to the UTC time, the resulting time
  # is used to set the 'Next Update' date of the CRL.
  expiry: 24h

#############################################################################
#  The registry section controls how the fabric-ca-server does two things:
#  1) authenticates enrollment requests which contain a username and password
#     (also known as an enrollment ID and secret).
#  2) once authenticated, retrieves the identity's attribute names and
#     values which the fabric-ca-server optionally puts into TCerts
#     which it issues for transacting on the Hyperledger Fabric blockchain.
#     These attributes are useful for making access control decisions in
#     chaincode.
#  There are two main configuration options:
#  1) The fabric-ca-server is the registry.
#     This is true if "ldap.enabled" in the ldap section below is false.
#  2) An LDAP server is the registry, in which case the fabric-ca-server
#     calls the LDAP server to perform these tasks.
#     This is true if "ldap.enabled" in the ldap section below is true,
#     which means this "registry" section is ignored.
#############################################################################
registry:
  # Maximum number of times a password/secret can be reused for enrollment
  # (default: -1, which means there is no limit)
  maxenrollments: -1

  # Contains identity information which is used when LDAP is disabled
  identities:
     - name: admin
       pass: adminpw
       type: client
       affiliation: ""
       attrs:
          hf.Registrar.Roles: "*"
          hf.Registrar.DelegateRoles: "*"
          hf.Revoker: true
          hf.IntermediateCA: true
          hf.GenCRL: true
          hf.Registrar.Attributes: "*"
          hf.AffiliationMgr: true

#############################################################################
#  Database section
#  Supported types are: "sqlite3", "postgres", and "mysql".
#  The datasource value depends on the type.
#  If the type is "sqlite3", the datasource value is a file name to use
#  as the database store.  Since "sqlite3" is an embedded database, it
#  may not be used if you want to run the fabric-ca-server in a cluster.
#  To run the fabric-ca-server in a cluster, you must choose "postgres"
#  or "mysql".
#############################################################################
db:
  type: sqlite3
  datasource: fabric-ca-server.db
  tls:
      enabled: false
      certfiles:
      client:
        certfile:
        keyfile:

#############################################################################
#  LDAP section
#  If LDAP is enabled, the fabric-ca-server calls LDAP to:
#  1) authenticate enrollment ID and secret (i.e. username and password)
#     for enrollment requests;
#  2) To retrieve identity attributes
#############################################################################
ldap:
   # Enables or disables the LDAP client (default: false)
   # If this is set to true, the "registry" section is ignored.
   enabled: false
   # The URL of the LDAP server
   url: ldap://<adminDN>:<adminPassword>@<host>:<port>/<base>
   # TLS configuration for the client connection to the LDAP server
   tls:
      certfiles:
      client:
         certfile:
         keyfile:
   # Attribute related configuration for mapping from LDAP entries to Fabric CA attributes
   attribute:
      # 'names' is an array of strings containing the LDAP attribute names which are
      # requested from the LDAP server for an LDAP identity's entry
      names: ['uid','member']
      # The 'converters' section is used to convert an LDAP entry to the value of
      # a fabric CA attribute.
      # For example, the following converts an LDAP 'uid' attribute
      # whose value begins with 'revoker' to a fabric CA attribute
      # named "hf.Revoker" with a value of "true" (because the boolean expression
      # evaluates to true).
      #    converters:
      #       - name: hf.Revoker
      #         value: attr("uid") =~ "revoker*"
      converters:
         - name:
           value:
      # The 'maps' section contains named maps which may be referenced by the 'map'
      # function in the 'converters' section to map LDAP responses to arbitrary values.
      # For example, assume a user has an LDAP attribute named 'member' which has multiple
      # values which are each a distinguished name (i.e. a DN). For simplicity, assume the
      # values of the 'member' attribute are 'dn1', 'dn2', and 'dn3'.
      # Further assume the following configuration.
      #    converters:
      #       - name: hf.Registrar.Roles
      #         value: map(attr("member"),"groups")
      #    maps:
      #       groups:
      #          - name: dn1
      #            value: peer
      #          - name: dn2
      #            value: client
      # The value of the user's 'hf.Registrar.Roles' attribute is then computed to be
      # "peer,client,dn3".  This is because the value of 'attr("member")' is
      # "dn1,dn2,dn3", and the call to 'map' with a 2nd argument of
      # "group" replaces "dn1" with "peer" and "dn2" with "client".
      maps:
         groups:
            - name:
              value:

#############################################################################
# Affiliations section. Fabric CA server can be bootstrapped with the
# affiliations specified in this section. Affiliations are specified as maps.
# For example:
#   businessunit1:
#     department1:
#       - team1
#   businessunit2:
#     - department2
#     - department3
#
# Affiliations are hierarchical in nature. In the above example,
# department1 (used as businessunit1.department1) is the child of businessunit1.
# team1 (used as businessunit1.department1.team1) is the child of department1.
# department2 (used as businessunit2.department2) and department3 (businessunit2.department3)
# are children of businessunit2.
# Note: Affiliations are case sensitive except for the non-leaf affiliations
# (like businessunit1, department1, businessunit2) that are specified in the configuration file,
# which are always stored in lower case.
#############################################################################
affiliations:
   org1:
      - department1
      - department2
   org2:
      - department1

#############################################################################
#  Signing section
#
#  The "default" subsection is used to sign enrollment certificates;
#  the default expiration ("expiry" field) is "8760h", which is 1 year in hours.
#
#  The "ca" profile subsection is used to sign intermediate CA certificates;
#  the default expiration ("expiry" field) is "43800h" which is 5 years in hours.
#  Note that "isca" is true, meaning that it issues a CA certificate.
#  A maxpathlen of 0 means that the intermediate CA cannot issue other
#  intermediate CA certificates, though it can still issue end entity certificates.
#  (See RFC 5280, section 4.2.1.9)
#
#  The "tls" profile subsection is used to sign TLS certificate requests;
#  the default expiration ("expiry" field) is "8760h", which is 1 year in hours.
#############################################################################
signing:
    default:
      usage:
        - digital signature
      expiry: 8760h
    profiles:
      ca:
         usage:
           - cert sign
           - crl sign
         expiry: 43800h
         caconstraint:
           isca: true
           maxpathlen: 0
      tls:
         usage:
            - signing
            - key encipherment
            - server auth
            - client auth
            - key agreement
         expiry: 8760h

###########################################################################
#  Certificate Signing Request (CSR) section.
#  This controls the creation of the root CA certificate.
#  The expiration for the root CA certificate is configured with the
#  "ca.expiry" field below, whose default value is "131400h" which is
#  15 years in hours.
#  The pathlength field is used to limit CA certificate hierarchy as described
#  in section 4.2.1.9 of RFC 5280.
#  Examples:
#  1) No pathlength value means no limit is requested.
#  2) pathlength == 1 means a limit of 1 is requested which is the default for
#     a root CA.  This means the root CA can issue intermediate CA certificates,
#     but these intermediate CAs may not in turn issue other CA certificates
#     though they can still issue end entity certificates.
#  3) pathlength == 0 means a limit of 0 is requested;
#     this is the default for an intermediate CA, which means it can not issue
#     CA certificates though it can still issue end entity certificates.
###########################################################################
csr:
   cn: ca.{org_name}.example.com
   names:
      - C: UK
        ST: "Hampshire"
        L: "Hursley"
        O: {org_name}.example.com
        OU:
   hosts:
     - localhost
     - {org_name}.example.com
   ca:
      expiry: 131400h
      pathlength: 1

#############################################################################
# BCCSP (BlockChain Crypto Service Provider) section is used to select which
# crypto library implementation to use
#############################################################################
bccsp:
    default: SW
    sw:
        hash: SHA2
        security: 256
        filekeystore:
            # The directory used for the software file-based keystore
            keystore: msp/keystore

#############################################################################
# Multi CA section
#
# Each Fabric CA server contains one CA by default.  This section is used
# to configure multiple CAs in a single server.
#
# 1) --cacount <number-of-CAs>
# Automatically generate <number-of-CAs> non-default CAs.  The names of these
# additional CAs are "ca1", "ca2", ... "caN", where "N" is <number-of-CAs>
# This is particularly useful in a development environment to quickly set up
# multiple CAs. Note that, this config option is not applicable to intermediate CA server
# i.e., Fabric CA server that is started with intermediate.parentserver.url config
# option (-u command line option)
#
# 2) --cafiles <CA-config-files>
# For each CA config file in the list, generate a separate signing CA.  Each CA
# config file in this list MAY contain all of the same elements as are found in
# the server config file except port, debug, and tls sections.
#
# Examples:
# fabric-ca-server start -b admin:adminpw --cacount 2
#
# fabric-ca-server start -b admin:adminpw --cafiles ca/ca1/fabric-ca-server-config.yaml
# --cafiles ca/ca2/fabric-ca-server-config.yaml
#
#############################################################################

cacount:

cafiles:

#############################################################################
# Intermediate CA section
#
# The relationship between servers and CAs is as follows:
#   1) A single server process may contain or function as one or more CAs.
#      This is configured by the "Multi CA section" above.
#   2) Each CA is either a root CA or an intermediate CA.
#   3) Each intermediate CA has a parent CA which is either a root CA or another intermediate CA.
#
# This section pertains to configuration of #2 and #3.
# If the "intermediate.parentserver.url" property is set,
# then this is an intermediate CA with the specified parent
# CA.
#
# parentserver section
#    url - The URL of the parent server
#    caname - Name of the CA to enroll within the server
#
# enrollment section used to enroll intermediate CA with parent CA
#    profile - Name of the signing profile to use in issuing the certificate
#    label - Label to use in HSM operations
#
# tls section for secure socket connection
#   certfiles - PEM-encoded list of trusted root certificate files
#   client:
#     certfile - PEM-encoded certificate file for when client authentication
#     is enabled on server
#     keyfile - PEM-encoded key file for when client authentication
#     is enabled on server
#############################################################################
intermediate:
  parentserver:
    url:
    caname:

  enrollment:
    hosts:
    profile:
    label:

  tls:
    certfiles:
    client:
      certfile:
      keyfile:
"""

        # Write the content to the file
        with open(file_path, 'w') as file:
            file.write(content)

    print(f"{num_orgs} CA configuration files created in {base_dir}.")

# File path for compose file
def add_org_to_composeca(num_orgs):
    COMPOSE_FILE_PATH = "./compose/compose-ca.yaml"
    # Template for new organization CA service
    ORG_CA_TEMPLATE = """
  ca_org{org_num}:
    image: hyperledger/fabric-ca:latest
    labels:
      service: hyperledger-fabric
    environment:
      - FABRIC_CA_HOME=/etc/hyperledger/fabric-ca-server
      - FABRIC_CA_SERVER_CA_NAME=ca-org{org_num}
      - FABRIC_CA_SERVER_TLS_ENABLED=true
      - FABRIC_CA_SERVER_PORT={port1}
      - FABRIC_CA_SERVER_OPERATIONS_LISTENADDRESS=0.0.0.0:{port2}
    ports:
      - "{port1}:{port1}"
      - "{port2}:{port2}"
    command: sh -c 'fabric-ca-server start -b admin:adminpw -d'
    volumes:
      - ../organizations/fabric-ca/org{org_num}:/etc/hyperledger/fabric-ca-server
    container_name: ca_org{org_num}
    networks:
      - test
"""

    if not os.path.exists(COMPOSE_FILE_PATH):
        print(f"Error: {COMPOSE_FILE_PATH} not found.")
        return

    # Backup original file
    backup_path = COMPOSE_FILE_PATH + ".bak"
    shutil.copy2(COMPOSE_FILE_PATH, backup_path)
    print(f"Backup created: {backup_path}")

    # Read existing content
    with open(COMPOSE_FILE_PATH, "r") as file:
        lines = file.readlines()

    # Find the index of ca_orderer service
    insert_index = -1
    for i, line in enumerate(lines):
        if "ca_orderer:" in line:
            insert_index = i-1
            break

    if insert_index == -1:
        print(f"Error: Could not find 'ca_orderer' section in {COMPOSE_FILE_PATH}.")
        return

    # Generate new organization CA entries
    new_entries = []
    base_port = 8054  # Starting from 10054 for new orgs
    for org_num in range(3, num_orgs + 3):
        port1 = base_port + (org_num - 2) * 1000
        port2 = port1 + 10001
        new_entries.append(ORG_CA_TEMPLATE.format(org_num=org_num, port1=port1, port2=port2))

    # Insert new entries before ca_orderer
    updated_lines = lines[:insert_index] + new_entries + lines[insert_index:]

    # Write back to file
    with open(COMPOSE_FILE_PATH, "w") as file:
        file.writelines(updated_lines)

    print(f"Successfully added {num_orgs} organizations to {COMPOSE_FILE_PATH}")

def add_org_to_ccutils(num_orgs):
    filename = "./scripts/ccutils.sh"
    # Create a backup of the original file
    backup_filename = filename + ".bak"
    shutil.copy2(filename, backup_filename)
    print(f"Backup created: {backup_filename}")

    with open(filename, 'r') as file:
        content = file.readlines()

    # Find the chaincodeInvoke function
    start_index = None
    end_index = None
    invoke_line_index = None
    for i, line in enumerate(content):
        if line.strip().startswith("chaincodeInvoke()"):
            start_index = i
        elif start_index is not None and line.strip() == "}":
            end_index = i
            break
        elif start_index is not None and "peer chaincode invoke" in line:
            invoke_line_index = i

    if start_index is None or end_index is None or invoke_line_index is None:
        print("Error: Could not find the chaincodeInvoke function or the invoke line.")
        return

    # Construct the new invoke line
    new_invoke_line = 'peer chaincode invoke -o localhost:7050 -C $CHANNEL_NAME -n ${CC_NAME} -c ${CC_INVOKE_CONSTRUCTOR} --tls --cafile $ORDERER_CA '
    for org in range(1, num_orgs + 3):
        port = 7051 if org == 1 else 9051 if org == 2 else 11051 + (org - 3) * 2000
        new_invoke_line += f'--peerAddresses localhost:{port} --tlsRootCertFiles $PEER0_ORG{org}_CA '
    new_invoke_line += '>&log.txt\n'

    # Replace the old invoke line with the new one
    content[invoke_line_index] = f"    {new_invoke_line}"

    # Write the updated content back to the file
    with open(filename, 'w') as file:
        file.writelines(content)

    print(f"Updated chaincodeInvoke function in {filename} to support {num_orgs} organizations.")

def add_org_to_deploycc(num_orgs):

    file_path = "./scripts/deployCC.sh"
    # Read the original file content
    
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    # Save a Backup 
    with open(file_path + ".bak", 'w') as file:
        file.writelines(lines)
    
    with open(file_path, "w") as f:
        # Write the original static content up to the dynamic sections
        f.write("""#!/bin/bash

source scripts/utils.sh

CHANNEL_NAME=${1:-"mychannel"}
CC_NAME=${2}
CC_SRC_PATH=${3}
CC_SRC_LANGUAGE=${4}
CC_VERSION=${5:-"1.0"}
CC_SEQUENCE=${6:-"1"}
CC_INIT_FCN=${7:-"NA"}
CC_END_POLICY=${8:-"NA"}
CC_COLL_CONFIG=${9:-"NA"}
DELAY=${10:-"3"}
MAX_RETRY=${11:-"5"}
VERBOSE=${12:-"false"}

println "executing with the following"
println "- CHANNEL_NAME: ${C_GREEN}${CHANNEL_NAME}${C_RESET}"
println "- CC_NAME: ${C_GREEN}${CC_NAME}${C_RESET}"
println "- CC_SRC_PATH: ${C_GREEN}${CC_SRC_PATH}${C_RESET}"
println "- CC_SRC_LANGUAGE: ${C_GREEN}${CC_SRC_LANGUAGE}${C_RESET}"
println "- CC_VERSION: ${C_GREEN}${CC_VERSION}${C_RESET}"
println "- CC_SEQUENCE: ${C_GREEN}${CC_SEQUENCE}${C_RESET}"
println "- CC_END_POLICY: ${C_GREEN}${CC_END_POLICY}${C_RESET}"
println "- CC_COLL_CONFIG: ${C_GREEN}${CC_COLL_CONFIG}${C_RESET}"
println "- CC_INIT_FCN: ${C_GREEN}${CC_INIT_FCN}${C_RESET}"
println "- DELAY: ${C_GREEN}${DELAY}${C_RESET}"
println "- MAX_RETRY: ${C_GREEN}${MAX_RETRY}${C_RESET}"
println "- VERBOSE: ${C_GREEN}${VERBOSE}${C_RESET}"

INIT_REQUIRED="--init-required"
# check if the init fcn should be called
if [ "$CC_INIT_FCN" = "NA" ]; then
  INIT_REQUIRED=""
fi

if [ "$CC_END_POLICY" = "NA" ]; then
  CC_END_POLICY=""
else
  CC_END_POLICY="--signature-policy $CC_END_POLICY"
fi

if [ "$CC_COLL_CONFIG" = "NA" ]; then
  CC_COLL_CONFIG=""
else
  CC_COLL_CONFIG="--collections-config $CC_COLL_CONFIG"
fi

FABRIC_CFG_PATH=$PWD/../config/

# import utils
. scripts/envVar.sh
. scripts/ccutils.sh

function checkPrereqs() {
  jq --version > /dev/null 2>&1

  if [[ $? -ne 0 ]]; then
    errorln "jq command not found..."
    errorln
    errorln "Follow the instructions in the Fabric docs to install the prereqs"
    errorln "https://hyperledger-fabric.readthedocs.io/en/latest/prereqs.html"
    exit 1
  fi
}

#check for prerequisites
checkPrereqs

## package the chaincode
./scripts/packageCC.sh $CC_NAME $CC_SRC_PATH $CC_SRC_LANGUAGE $CC_VERSION 

PACKAGE_ID=$(peer lifecycle chaincode calculatepackageid ${CC_NAME}.tar.gz)
""")

        # Dynamic section: Install chaincode for each organization
        for i in range(1, num_orgs + 3):
            f.write(f'infoln "Installing chaincode on peer0.org{i}..."\n')
            f.write(f"installChaincode {i}\n")

        f.write("\nresolveSequence\n\n")

        # Approve the chaincode definition for each organization
        for i in range(1, num_orgs + 3):
            f.write(f"approveForMyOrg {i}\n")
        
        f.write("\n")

        # Check commit readiness for each organization
        f.write(f'checkCommitReadiness {i} ' +
                " ".join([f'"\\\"Org{j}MSP\\\": true"' for j in range(1, num_orgs + 3)]) + "\n")
        
        # Commit the chaincode definition with all organizations involved
        org_list = " ".join(str(i) for i in range(1, num_orgs + 3))
        f.write(f"commitChaincodeDefinition {org_list}\n\n")


        f.write("\n\n")

        for i in range(1, num_orgs + 3):
            f.write(f"queryCommitted {i}\n\n")

        # Static section: Invoke chaincode initialization if needed
        f.write("""
if [ "$CC_INIT_FCN" = "NA" ]; then
  infoln "Chaincode initialization is not required"
else
  chaincodeInvokeInit """ + org_list + """
fi

exit 0
""")
    print(f"Added {num_orgs} organizations to {file_path}")

num_orgs = int(input("Enter the number of organizations: "))

add_orgs_to_channel_script(num_orgs)
add_orgs_to_ccp_generate(num_orgs)
add_organizations_after_existing(num_orgs)
create_crypto_config_files(num_orgs)
add_orgs_to_setGlobals(num_orgs)
add_orgs_to_network_sh(num_orgs)
add_anchor_peer_update_blocks(num_orgs)
add_organizations(num_orgs)
add_peers_to_docker_compose(num_orgs)
add_org_to_setOrgEnv(num_orgs)
add_orgs_to_registerEnroll(num_orgs)
add_org_to_fabricca(num_orgs)
add_org_to_composeca(num_orgs)
add_org_to_ccutils(num_orgs)
add_org_to_deploycc(num_orgs)
