const FabricCAServices = require('fabric-ca-client');
const { Gateway, Wallets } = require('fabric-network');
const fs = require('fs');
const path = require('path');
const readline = require('readline');
const crypto = require('crypto');
 
const encryptPassword = (password) => {
    const hash = crypto.createHash('sha256');
    hash.update(password);
    return hash.digest('hex');
};
 
const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});
 
// Helper function to read user input
function prompt(question) {
    return new Promise(resolve => rl.question(question, resolve));
}
 
// Step 1: Setup the Fabric CA Client
const caURL = 'https://localhost:7054'; // Fabric CA URL
const caCertPath = path.resolve(__dirname, 'organizations', 'fabric-ca', 'org1', 'ca-cert.pem');
const caCert = fs.readFileSync(caCertPath).toString();
 
const ca = new FabricCAServices(caURL, { trustedRoots: caCert, verify: false });
 
// Step 2: Create a wallet to store credentials
const walletPath = path.join(__dirname, 'wallet');
 
// function getCurrentTime() {
//     const now = new Date();
//     return `${now.toLocaleTimeString()}.${now.getMilliseconds()}`;
// }
 
const logFilePath = path.join(__dirname, 'analysis_log.txt');
 
function getCurrentTime(message) {
    const now = new Date();
    const timestamp = `${now.toLocaleTimeString()}.${now.getMilliseconds()}`;
    const logMessage = `[${timestamp}] ${message}\n`;
 
    // Print to terminal
    console.log(logMessage.trim());
 
    // Append to file
    fs.appendFileSync(logFilePath, logMessage, 'utf8');
}
 
async function registerUser(adminUserIdentity, userId, userPassword, wallet) {
    try {
 
 
        const infoPath = path.join(walletPath, 'userInfo.json');
        if (fs.existsSync(infoPath)) {
            const userInfo = JSON.parse(fs.readFileSync(infoPath));
           // Find the user object with the matching userId
            const user = userInfo.find(u => u.userId === userId);
            
            if (user) {
                console.log('User already exists.');
                rl.close();
                process.exit(0);
            }
        }
 
        console.log(`Registering user ${userId}...`);
        await ca.register(
            {
                enrollmentID: userId,
                enrollmentSecret: userPassword,
                role: 'client',
            },
            adminUserIdentity
        );
        
        const enrollment = await ca.enroll({
            enrollmentID: userId,
            enrollmentSecret: userPassword,
        });
 
        const user = {
            credentials: {
                certificate: enrollment.certificate,
                privateKey: enrollment.key.toBytes(),
            },
            mspId: 'Org1MSP', // Replace with your organization MSP
            type: 'X.509',
        };
 
        await wallet.put(userId, user);
 
        const encryptedPassword = encryptPassword(userPassword);
 
        const userInfo = {
            userId: userId,
            password: encryptedPassword
        };
 
        const userInfoPath = path.join(walletPath, 'userInfo.json');
 
        let existingData = [];
        if (fs.existsSync(userInfoPath)) {
            const fileContent = fs.readFileSync(userInfoPath);
            try {
                existingData = JSON.parse(fileContent);
            } catch (error) {
                console.log('Error parsing existing file content:', error);
            }
        }
        // Add the new user to the existing data array
        existingData.push(userInfo);
 
        // Write the updated array back to the file
        fs.writeFileSync(userInfoPath, JSON.stringify(existingData, null, 2));
 
        console.log(`User ${userId} is now part of the network.`);
 
    } catch (error) {
        if (error.toString().includes('already exists')) {
            console.log(`User ${userId} is already registered.`);
            rl.close();
            process.exit(0); // Gracefully exit if user already exists
        } else {
            throw error;
        }
    }
}
 
async function loginUser(userId, userPassword, wallet) {
    try {
 
        const userInfoPath = path.join(walletPath, 'userInfo.json');
        if (fs.existsSync(userInfoPath)) {
            const userInfo = JSON.parse(fs.readFileSync(userInfoPath));
           // Find the user object with the matching userId
            const user = userInfo.find(u => u.userId === userId);
            
            if (user) {
                if(user.password === encryptPassword(userPassword)) {
                    console.log(`Login successful for user ${userId}.`);
                }
                else {
                    console.log('Incorrect password.');
                    rl.close();
                    process.exit(0);
                }
            } else {
                console.log('User not found.');
                rl.close();
                process.exit(0);
            }
        } else {
            console.log('User info not found.');
        }
    } catch (error) {
        console.error(`Failed to login user: ${error.message}`);
    }
}
 
// Helper function to register land
async function registerLand(userId, landId, wallet) {
    try {
        const gateway = new Gateway();
 
        // Load user identity
        const userIdentity = await wallet.get(userId);
        if (!userIdentity) {
            throw new Error(`Identity for user ${userId} not found in wallet.`);
        }
 
        // Connect to the gateway
        const connectionProfilePath = path.resolve(__dirname, 'organizations/peerOrganizations/org1.example.com/connection-org1.json'); // Replace with your connection profile
        const connectionProfile = JSON.parse(fs.readFileSync(connectionProfilePath, 'utf8'));
        await gateway.connect(connectionProfile, {
            wallet,
            identity: userId,
            discovery: { enabled: true, asLocalhost: true },
        });
 
        // Get the network and contract
        const network = await gateway.getNetwork('mychannel'); // Replace 'mychannel' with your channel name
        const contract = network.getContract('basic'); // Replace 'landRegistry' with your chaincode name
 
        // console.log(`[${getCurrentTime()}] Registering land ID: ${landId} for user: ${userId}...`);
        getCurrentTime(`\nRegistering land ID: ${landId} for user: ${userId}...`);
        
        // Invoke the smart contract
        const result = await contract.submitTransaction('CreateAsset', landId, userId);
        const resp = JSON.parse(result.toString());
 
        // console.log(`[${getCurrentTime()}] Responses obtained from endorsers!`);
        getCurrentTime(`Responses obtained from endorsers!`);
        
        if (resp.status === "failed") {
            console.log("Land registration failed: ", resp.message);
        } else {
            const result2 = await contract.submitTransaction('CreateAsset2', landId, userId, resp.endorsementMessages);
            const resp2 = JSON.parse(result2.toString());
            // console.log(`[${getCurrentTime()}] Response: `, resp2);
            // getCurrentTime(`Response: ${JSON.stringify(resp2)}`);
            getCurrentTime(`Response: Final responses obtained`);
        }
 
        // Disconnect the gateway
        await gateway.disconnect();
 
    } catch (error) {
        console.error(`Failed to register land: ${error.message}`);
    }
}
 
async function viewLand(userId, wallet) {
    try {
        const gateway = new Gateway();
 
        // Load user identity
        const userIdentity = await wallet.get(userId);
        if (!userIdentity) {
            throw new Error(`Identity for user ${userId} not found in wallet.`);
        }
       
        // Connect to the gateway
        const connectionProfilePath = path.resolve(__dirname, 'organizations/peerOrganizations/org1.example.com/connection-org1.json'); // Replace with your connection profile
        const connectionProfile = JSON.parse(fs.readFileSync(connectionProfilePath, 'utf8'));
        await gateway.connect(connectionProfile, {
            wallet,
            identity: userId,
            discovery: { enabled: true, asLocalhost: true },
        });
       
        // Get the network and contract
        const network = await gateway.getNetwork('mychannel'); // Replace 'mychannel' with your channel name
        const contract = network.getContract('basic'); // Replace 'landRegistry' with your chaincode name
        
        // Invoke the smart contract
        const result = await contract.evaluateTransaction('GetAllAssets');
        console.log(`All lands: ${result.toString()}`);
 
        // Disconnect the gateway
        await gateway.disconnect();
    } catch (error) {
        console.error(`Failed to view land: ${error.message}`);
    }
}
 
async function viewLandRequests(userId, wallet) {
    try {
        const gateway = new Gateway();
 
        // Load user identity
        const userIdentity = await wallet.get(userId);
        if (!userIdentity) {
            throw new Error(`Identity for user ${userId} not found in wallet.`);
        }
       
        // Connect to the gateway
        const connectionProfilePath = path.resolve(__dirname, 'organizations/peerOrganizations/org1.example.com/connection-org1.json'); // Replace with your connection profile
        const connectionProfile = JSON.parse(fs.readFileSync(connectionProfilePath, 'utf8'));
        await gateway.connect(connectionProfile, {
            wallet,
            identity: userId,
            discovery: { enabled: true, asLocalhost: true },
        });
       
        // Get the network and contract
        const network = await gateway.getNetwork('mychannel'); // Replace 'mychannel' with your channel name
        const contract = network.getContract('basic'); // Replace 'landRegistry' with your chaincode name
        
        // Invoke the smart contract
        const result = await contract.evaluateTransaction('GetPendingRequests', userId);
        console.log(`All pending requests: ${result.toString()}`);
 
        // Disconnect the gateway
        await gateway.disconnect();
    } catch (error) {
        console.error(`Failed to view land requests: ${error.message}`);
    }
}
 
async function buyLand(userId, landId, wallet) {
    try {
        const gateway = new Gateway();
 
        // Load user identity
        const userIdentity = await wallet.get(userId);
        if (!userIdentity) {
            throw new Error(`Identity for user ${userId} not found in wallet.`);
        }
       
        // Connect to the gateway
        const connectionProfilePath = path.resolve(__dirname, 'organizations/peerOrganizations/org1.example.com/connection-org1.json'); // Replace with your connection profile
        const connectionProfile = JSON.parse(fs.readFileSync(connectionProfilePath, 'utf8'));
        await gateway.connect(connectionProfile, {
            wallet,
            identity: userId,
            discovery: { enabled: true, asLocalhost: true },
        });
       
        // Get the network and contract
        const network = await gateway.getNetwork('mychannel'); // Replace 'mychannel' with your channel name
        const contract = network.getContract('basic'); // Replace 'landRegistry' with your chaincode name
        
        // Invoke the smart contract
        const result = await contract.submitTransaction('RequestAssetTransfer', landId, userId);
        const resp = JSON.parse(result.toString());
 
        console.log("Request generated successfully:", result.toString());
 
        // Disconnect the gateway
        await gateway.disconnect();
    } catch (error) {
        console.error(`Failed to buy land: ${error.message}`);
    }
}
 
async function sellLand(userId, txId, wallet) {
    try {
        const gateway = new Gateway();
 
        // Load user identity
        const userIdentity = await wallet.get(userId);
        if (!userIdentity) {
            throw new Error(`Identity for user ${userId} not found in wallet.`);
        }
       
        // Connect to the gateway
        const connectionProfilePath = path.resolve(__dirname, 'organizations/peerOrganizations/org1.example.com/connection-org1.json'); // Replace with your connection profile
        const connectionProfile = JSON.parse(fs.readFileSync(connectionProfilePath, 'utf8'));
        await gateway.connect(connectionProfile, {
            wallet,
            identity: userId,
            discovery: { enabled: true, asLocalhost: true },
        });
       
        // Get the network and contract
        const network = await gateway.getNetwork('mychannel'); // Replace 'mychannel' with your channel name
        const contract = network.getContract('basic'); // Replace 'landRegistry' with your chaincode name
        
        // console.log(`[${getCurrentTime()}] Selling land!`);
        getCurrentTime(`\nSelling land!`);
        
        // Invoke the smart contract
        const result = await contract.submitTransaction('SellAsset', txId, userId);
        const resp = JSON.parse(result.toString());
        
        // console.log(`[${getCurrentTime()}] Responses obtained from endorsers!`);
        getCurrentTime(`Responses obtained from endorsers!`);
        
        if (resp.status === "failed") {
            console.log("Land Transfer failed:", resp.message);
        } else {
            const result2 = await contract.submitTransaction('SellAsset2', txId, resp.asset.ID, resp.asset.Owner, resp.endorsementMessages);
            const resp2 = JSON.parse(result2.toString());
            // console.log(`[${getCurrentTime()}] Response: `, resp2);
            // getCurrentTime(`Response: ${JSON.stringify(resp2)}`);
            getCurrentTime(`Response: Final responses obtained`);
        }
 
        // Disconnect the gateway
        await gateway.disconnect();
    } catch (error) {
        console.error(`Failed to sell land: ${error.message}`);
    }
}
 
async function main() {
    try {
 
        process.env.FABRIC_LOGGING = 'trace';
 
 
        const wallet = await Wallets.newFileSystemWallet(walletPath);
        console.log(`Wallet path: ${walletPath}`);
 
        // Step 3: Enroll the admin user (if not already enrolled)
        const adminIdentity = await wallet.get('admin');
        if (!adminIdentity) {
            console.log('Enrolling admin...');
            const enrollment = await ca.enroll({
                enrollmentID: 'admin', // Replace with your CA admin ID
                enrollmentSecret: 'adminpw', // Replace with your CA admin password
            });
 
            const admin = {
                credentials: {
                    certificate: enrollment.certificate,
                    privateKey: enrollment.key.toBytes(),
                },
                mspId: 'Org1MSP', // Replace with your organization MSP
                type: 'X.509',
            };
 
            await wallet.put('admin', admin);
            console.log('Successfully enrolled admin and imported it into the wallet.');
        } else {
            console.log('Admin already enrolled.');
        }
 
        // Step 4: Ask user to register or login
        const action = await prompt('Press 1 to Register or 2 to Login: ');
 
        const userId = await prompt('Enter user ID: ');
        const userPassword = await prompt('Enter user password: ');
 
        const adminUser = await wallet.get('admin');
        if (!adminUser) {
            console.error('Admin identity is not available in the wallet.');
            return;
        }
 
        const provider = wallet.getProviderRegistry().getProvider(adminUser.type);
        const adminUserIdentity = await provider.getUserContext(adminUser, 'admin');
 
        if (action === '1') {
            // Register new user
            await registerUser(adminUserIdentity, userId, userPassword, wallet);
            // await enrollUser(userId, userPassword, wallet);
        } else if (action === '2') {
            // Login existing user
            await loginUser(userId, userPassword, wallet);
            while(true) {
                // After login, ask to register land
                const landAction = await prompt('Press 1 to Register Land, 2 to view all lands, 3 to buy a land, 4 to view buy land requests, 5 to approve a buy request, or 0 to Exit: ');
                if (landAction === '1') {
                    const landId = await prompt('Enter Land ID: ');
                    await registerLand(userId, landId, wallet);
                }
                else if (landAction === '2') {
                    await viewLand(userId, wallet);
                }
                else if(landAction === '3') {
                    const landId = await prompt('Enter Land ID to be bought: ');
                    await buyLand(userId, landId, wallet);
                }
                else if(landAction === '4') {
                    await viewLandRequests(userId, wallet);
                }
                else if(landAction === '5') {
                    const txId = await prompt('Enter transaction ID to be approved: ');
                    await sellLand(userId, txId, wallet);
                }
                else break;
            }
        } else {
            console.log('Invalid action selected.');
        }
        rl.close();
    } catch (error) {
        console.error(`Error: ${error.message}`);
    }
}
 
main();