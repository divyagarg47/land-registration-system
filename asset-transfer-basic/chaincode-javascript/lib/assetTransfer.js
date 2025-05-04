/*
 * Copyright IBM Corp. All Rights Reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

'use strict';

// Deterministic JSON.stringify()
const stringify  = require('json-stringify-deterministic');
const sortKeysRecursive  = require('sort-keys-recursive');
const { Contract } = require('fabric-contract-api');

class AssetTransfer extends Contract {

    async Init(ctx) {
        const assets = [
        ];

        for (const asset of assets) {
            asset.docType = 'asset';
            // example of how to write to world state deterministically
            // use convetion of alphabetic order
            // we insert data in alphabetic order using 'json-stringify-deterministic' and 'sort-keys-recursive'
            // when retrieving data, in any lang, the order of data will be the same and consequently also the corresonding hash
            await ctx.stub.putState(asset.ID, Buffer.from(stringify(sortKeysRecursive(asset))));
        }
    }

    // CreateAsset issues a new asset to the world state with given details.
    async CreateAsset(ctx, id, owner) {
        const exists = await this.AssetExists(ctx, id);
        if (exists) {
            return JSON.stringify({
                status: "failed",
                message: `The asset ${id} already exists`,
            });
        }
        
        const asset = {
            ID: id,
            Owner: owner,
        };
        const timestamp = ctx.stub.getTxTimestamp();  // Get block timestamp
         // Extract seconds and nanoseconds from the timestamp
        const milliseconds = Math.floor(timestamp.nanos / 1_000_000); // Convert nanoseconds to milliseconds
        // Create a JavaScript Date object from the timestamp
        const transferTime = new Date(timestamp.seconds * 1000 + milliseconds);
        const formattedTransferTime = new Intl.DateTimeFormat('en-IN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            fractionalSecondDigits: 3,
            timeZone: 'Asia/Kolkata',
            hour12: false, // 24-hour format
        }).format(transferTime);

        // await ctx.stub.putState(id, Buffer.from(stringify(sortKeysRecursive(asset))));
        await ctx.stub.setEvent('CreateAssetEvent', Buffer.from(formattedTransferTime));

        // Return both oldOwner and transfer timestamp
        return JSON.stringify({
            asset: asset,
            transferTime: formattedTransferTime,
        });

    }

     // CreateAsset issues a new asset to the world state with given details.
     async CreateAsset2(ctx, id, owner, responses) {
        
        const asset = {
            ID: id,
            Owner: owner,
            Responses: responses
        };
        const timestamp = ctx.stub.getTxTimestamp();  // Get block timestamp
         // Extract seconds and nanoseconds from the timestamp
        const milliseconds = Math.floor(timestamp.nanos / 1_000_000); // Convert nanoseconds to milliseconds
        // Create a JavaScript Date object from the timestamp
        const transferTime = new Date(timestamp.seconds * 1000 + milliseconds);
        const formattedTransferTime = new Intl.DateTimeFormat('en-IN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            fractionalSecondDigits: 3,
            timeZone: 'Asia/Kolkata',
            hour12: false, // 24-hour format
        }).format(transferTime);

        await ctx.stub.putState(id, Buffer.from(stringify(sortKeysRecursive(asset))));
        await ctx.stub.setEvent('CreateAssetEvent', Buffer.from(formattedTransferTime));

        // Return both oldOwner and transfer timestamp
        return JSON.stringify({
            asset: asset,
            transferTime: formattedTransferTime,
        });
    }

    // ReadAsset returns the asset stored in the world state with given id.
    async ReadAsset(ctx, id) {
        const assetJSON = await ctx.stub.getState(id); // get the asset from chaincode state
        if (!assetJSON || assetJSON.length === 0) {
            throw new Error(`The asset ${id} does not exist`);
        }
        return assetJSON.toString();
    }

    async RequestAssetTransfer(ctx, assetID, newOwner) {
        const exists = await this.AssetExists(ctx, assetID);
        if (!exists) {
            return JSON.stringify({
                status: "failed",
                message: `The asset ${assetID} does not exist`,
            });
        }
    
        const assetString = await this.ReadAsset(ctx, assetID);
        const asset = JSON.parse(assetString);
        const currentOwner = asset.Owner;
    
        // Ensure buyer is not already the owner
        if (currentOwner === newOwner) {
            return JSON.stringify({
                status: "failed",
                message: `You already own this asset.`,
            });
        }
    
        // Create a transaction request
        const transactionID = ctx.stub.getTxID();
        const request = {
            transactionID: transactionID,
            assetID: assetID,
            currentOwner: currentOwner,
            newOwner: newOwner,
            status: "pending",
            timestamp: ctx.stub.getTxTimestamp(),
        };
    
        // Store the transfer request in the world state
        const requestKey = `request_${transactionID}`;
        await ctx.stub.putState(requestKey, Buffer.from(JSON.stringify(request)));
    
        return JSON.stringify({
            status: "success",
            message: `Transfer request for ${assetID} created. Waiting for seller's approval.`,
            transactionID: transactionID,
        });
    }
    async GetPendingRequests(ctx, owner) {
        const iterator = await ctx.stub.getStateByRange("", ""); // Get all keys
        const requests = [];
    
        let result = await iterator.next();
        while (!result.done) {
            const key = result.value.key;
            const value = result.value.value.toString();
    
            if (key.startsWith("request_")) {  // Only consider transfer requests
                const request = JSON.parse(value);
                if (request.status === "pending" && request.currentOwner === owner) {
                    requests.push(request);
                }
            }
            result = await iterator.next();
        }
    
        return JSON.stringify(requests);
    }    

    // UpdateAsset updates an existing asset in the world state with provided parameters.
    async UpdateAsset(ctx, id, owner) {
        const exists = await this.AssetExists(ctx, id);
        if (!exists) {
            throw new Error(`The asset ${id} does not exist`);
        }

        // overwriting original asset with new asset
        const updatedAsset = {
            ID: id,
            Owner: owner,
        };
        // we insert data in alphabetic order using 'json-stringify-deterministic' and 'sort-keys-recursive'
        return ctx.stub.putState(id, Buffer.from(stringify(sortKeysRecursive(updatedAsset))));
    }

    // DeleteAsset deletes an given asset from the world state.
    async DeleteAsset(ctx, id) {
        const exists = await this.AssetExists(ctx, id);
        if (!exists) {
            throw new Error(`The asset ${id} does not exist`);
        }
        return ctx.stub.deleteState(id);
    }

    // AssetExists returns true when asset with given ID exists in world state.
    async AssetExists(ctx, id) {
        const assetJSON = await ctx.stub.getState(id);
        return assetJSON && assetJSON.length > 0;
    }

    // TransferAsset updates the owner field of asset with given id in the world state.
    async SellAsset(ctx, txId, owner) {
        const iterator = await ctx.stub.getStateByRange("", ""); // Get all keys
        const requests = [];
    
        let result = await iterator.next();
        while (!result.done) {
            const key = result.value.key;
            const value = result.value.value.toString();
    
            if (key.startsWith("request_")) {  // Only consider transfer requests
                const request = JSON.parse(value);
                if (request.status === "pending" && request.currentOwner === owner && request.transactionID === txId) {
                    requests.push(request);
                }
            }
            result = await iterator.next();
        }

        if (requests == []) {
            return JSON.stringify({
                status: "failed",
                message: `The transaction ${txId} does not exist`,
            });
        }

        const id = requests[0].assetID;
        const newOwner = requests[0].newOwner;

        const assetString = await this.ReadAsset(ctx, id);
        const asset = JSON.parse(assetString);
        const oldOwner = asset.Owner;

        asset.Owner = newOwner;
        const timestamp = ctx.stub.getTxTimestamp();  // Get block timestamp
         // Extract seconds and nanoseconds from the timestamp
        const milliseconds = Math.floor(timestamp.nanos / 1_000_000); // Convert nanoseconds to milliseconds
        // Create a JavaScript Date object from the timestamp
        const transferTime = new Date(timestamp.seconds * 1000 + milliseconds);
        const formattedTransferTime = new Intl.DateTimeFormat('en-IN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            fractionalSecondDigits: 3,
            timeZone: 'Asia/Kolkata',
            hour12: false, // 24-hour format
        }).format(transferTime);

        await ctx.stub.setEvent('TransferAssetEvent', Buffer.from(formattedTransferTime));

        // Return both oldOwner and transfer timestamp
        return JSON.stringify({
            asset: asset,
            transferTime: formattedTransferTime,
        });
    }

    // TransferAsset updates the owner field of asset with given id in the world state.
    async SellAsset2(ctx, txid, id, newOwner, responses) {
        const exists = await this.AssetExists(ctx, id);
        if (!exists) {
            return JSON.stringify({
                status: "failed",
                message: `The asset ${id} does not exist`,
            });
        }

        const assetString = await this.ReadAsset(ctx, id);
        const asset = JSON.parse(assetString);
        const oldOwner = asset.Owner;
        asset.Owner = newOwner;
        asset.Responses = responses;
        const timestamp = ctx.stub.getTxTimestamp();  // Get block timestamp
         // Extract seconds and nanoseconds from the timestamp
        const milliseconds = Math.floor(timestamp.nanos / 1_000_000); // Convert nanoseconds to milliseconds
        // Create a JavaScript Date object from the timestamp
        const transferTime = new Date(timestamp.seconds * 1000 + milliseconds);
        const formattedTransferTime = new Intl.DateTimeFormat('en-IN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            fractionalSecondDigits: 3,
            timeZone: 'Asia/Kolkata',
            hour12: false, // 24-hour format
        }).format(transferTime);

        await ctx.stub.putState(id, Buffer.from(stringify(sortKeysRecursive(asset))));
        await ctx.stub.setEvent('TransferAssetEvent', Buffer.from(formattedTransferTime));

        const updatedAssetBuffer = await ctx.stub.getState(id);
        const updatedAsset = JSON.parse(updatedAssetBuffer.toString());

        
        const iterator = await ctx.stub.getStateByRange("", ""); // Get all keys
        let result = await iterator.next();
        while (!result.done) {
            const key = result.value.key;
            const value = result.value.value.toString();
            if (key.startsWith("request_")) {  // Only consider transfer requests
                const request = JSON.parse(value);
                if (request.transactionID === txid) {
                    if (updatedAsset.owner === newOwner) {
                        request.status = "accepted";
                    }
                    else {
                        request.status = "rejected";
                    }
                    await ctx.stub.putState(key, Buffer.from(stringify(sortKeysRecursive(request))));
                    break;
                }
            }
            result = await iterator.next();
        }

        // Return both oldOwner and transfer timestamp
        return JSON.stringify({
            asset: asset,
            transferTime: formattedTransferTime,
        });
    }

    // GetAllAssets returns all assets found in the world state.
    async GetAllAssets(ctx) {
        const allResults = [];
        // range query with empty string for startKey and endKey does an open-ended query of all assets in the chaincode namespace.
        const iterator = await ctx.stub.getStateByRange('', '');
        let result = await iterator.next();
        while (!result.done) {
            const key = result.value.key;
            if (key.startsWith("request_")) {  // Only consider transfer requests
                result = await iterator.next();
                continue;
            }
            const strValue = Buffer.from(result.value.value.toString()).toString('utf8');
            let record;
            try {
                record = JSON.parse(strValue);
            } catch (err) {
                console.log(err);
                record = strValue;
            }
            allResults.push(record);
            result = await iterator.next();
        }
        return JSON.stringify(allResults);
    }
}

module.exports = AssetTransfer;
