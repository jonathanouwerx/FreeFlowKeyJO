import WalletConnect from "@walletconnect/client";
import QRCodeModal from "algorand-walletconnect-qrcode-modal";
import algosdk from "algosdk";
import { formatJsonRpcRequest } from "@json-rpc-tools/utils";

// a function to see if a wallet has been connected already
const checkIfWalletIsConnected = async () => {
  try {
    if (!connected) {
      console.log("No connection");
      return;
    } else {
      console.log("We have connection", connector);
    }

    const { accounts }  = connector;

    if (accounts.length !== 0) {
      const account = accounts[0];
      console.log("Found an authorized account:", account);
      setCurrentAccount(account);
      // await getAllRecs(); IMPORTANT FOR FUNCTIONALITY LATER
    } else {
      setCurrentAccount();
      console.log("No authorized account found");
    }
  } catch (error) {
    console.log(error);
  }
}

// a function to disconnect a wallet
const disconnectWallet = async () => {
  connector.killSession();
  console.log("Killing session for wallet with address: ", currentAccount);
  setCurrentAccount();
  setConnector();
  setConnected(false);
}

// a function to connect a wallet
const connectWallet = async () => {
  try {
    const bridge = "https://bridge.walletconnect.org";
    const connector = new WalletConnect({ bridge, qrcodeModal: QRCodeModal });
    setConnector(connector);

    if (!connector.connected) {
      await connector.createSession();
      console.log("Creating new connector session");
    }

    connector.on("connect", (error, payload) => {
      if (error) {
        throw error;
      }
      // Get provided accounts
      const { accounts } = payload.params[0];
      console.log("connector.on connect: Connected an account with address:", accounts[0]);
      setConnector(connector);
      setConnected(true);
      setCurrentAccount(accounts[0]);
    });

    connector.on("session_update", (error, payload) => {
      if (error) {
        throw error;
      }
      // Get updated accounts 
      const { accounts } = payload.params[0];
      setCurrentAccount(accounts[0])
    });

    connector.on("disconnect", (error, payload) => {
      if (error) {
        throw error;
      }
      setCurrentAccount();
      setConnected(false);
      setConnector();
    });
    
    if (connector.connected) {
      const {accounts} = connector;
      const account = accounts[0];
      setCurrentAccount(account);
      setConnected(true);
    }
  } catch(error) {
    console.log("something didn't work in creating connector", error);
  }
}

/* This is an alternative way to perform the wallet connection process

// Create a connector
const connector = new WalletConnect({
  bridge: "https://bridge.walletconnect.org", // Required
  qrcodeModal: QRCodeModal,
});

// Check if connection is already established
if (!connector.connected) {
  // create new session
  connector.createSession();
}

// Subscribe to connection events
connector.on("connect", (error, payload) => {
  if (error) {
    throw error;
  }

  // Get provided accounts
  const { accounts } = payload.params[0];
});

connector.on("session_update", (error, payload) => {
  if (error) {
    throw error;
  }

  // Get updated accounts 
  const { accounts } = payload.params[0];
});

connector.on("disconnect", (error, payload) => {
  if (error) {
    throw error;
  }
});
*/

// python_filenames:
// asset_creation - args: None
// payment - args: sender_address, receiver_address, amount
// asset_xfer = args: receiver_address, amount



const executeProcess = async (pythonFilename, inputArgs, daoAddress, daoPrivateKey) => {
  let {PythonShell} = require('python-shell')

  // function to run a python environment and get basic transactions
  const runPy = async (pythonFilename, inputArgs) => {
    const options = {
      mode: 'text',
      scriptPath: 'wallet_connect/basic_transactions/',
      args: [inputArgs],
    };
  
    // wrap it in a promise, and `await` the result
    const result = await new Promise((resolve, reject) => {
      PythonShell.run(`${pythonFilename}.py`, options, (err, results) => {
        // results is an array consisting of messages collected during execution
        // results = [txn, message]
        if (err) return reject(err);
        return resolve(results);
      });
    });
    console.log(result.stdout);
    return result;
  };

  // array of WalletTransaction objects received from python shell
  arrayWT = runPy(pythonFilename, inputArgs)

  // array of signed txns to be submitted together
  let signed = []

  // function to sign txns with DAO private key
  const dao_sign = async(unsigned_txn) => {
      signedTxn = unsigned_txn.signTxn( daoPrivateKey )
    return signedTxn
  }

  // identifies if there are any transactions to be signed by the DAO 
  var arrayLength = arrayWT.length;
  for (var i = 0; i < arrayLength; i++) {
    if (arrayWT[i][2] == daoAddress) {
       // decode the relevant transactions and push into signed txns array
      rawDaoTxnBlob = dao_sign(algosdk.decodeUnsignedTransaction(results[i][0]))
      signedDaoTxn = algosdk.decodeSignedTransaction(rawDaoTxnBlob)
      signed.push( signedDaoTxn )
    }
  }
  
  // requestParams should be an array of WalletTransaction objects, one for each transaction
  // a WalletTransaction object has two fields, txn: string and message?: string
  
  // ? Do I need to import 'this'/'connector'
  // submit QR code to wallet to be signed
  const requestParams = [arrayWT];
  const request = formatJsonRpcRequest("algo_signTxn", requestParams);
  const result = await this.connector.sendCustomRequest(request);

  // TODO: Consider whether to use this code or mine below
  // TODO: Consider how many txns this will return - check walletconnect algo schema
  /* 
  const decodedResult = result.map(element => {
    return element ? new Uint8Array(Buffer.from(element, "base64")) : null;
  });
  */
  // TODO: Consider how to have a variable number of txns

  // decode the result and push into signed txns array // TODO: mbe switch result to decoded_result
  const rawWalletTxnBlob = Buffer.from(result,'base64');
  signedWalletTxn = algosdk.decodeSignedTransaction(rawWalletTxnBlob) // This needs to be fixed
  signed.push( signedWalletTxn )

  // create the algodClient for submitting transactions
  const baseServer = 'https://testnet-algorand.api.purestake.io/ps2'
  const port = '';
  const token = {'X-API-Key': '2MOR0HMzNG92jNIN89adW6GWQn0vcNL28JhWy9zT'}
  const algodClient = new algosdk.Algodv2(token, baseServer, port);

  
  // Submit transaction group
  let tx = (await algodClient.sendRawTransaction(signed).do());
  // Wait for transaction to be confirmed
  confirmedTxn = await algosdk.waitForConfirmation(algodClient, tx.txId, 4);
  //Get the completed Transaction
  console.log("Transaction " + tx.txId + " confirmed in round " + confirmedTxn["confirmed-round"]);
}



// TODO: Decide for the example how the DAO will sign with its private key
// For this example, there will only be one DAO account
// when it comes to production, there will be the DAO_creator_account and the DAO account

// ! Deprecated method
/* 
const sendWCTransaction = async (python_filename, input_args) => {
  let {PythonShell} = require('python-shell')

  var options = {
      scriptPath: 'wallet_connect/basic_transactions/',
      mode: 'text',
      args: [input_args]
  };
  
  PythonShell.run(`${python_filename}.py`, options, function (err, results) {
      if (err) throw err;
      // results is an array consisting of messages collected during execution
      // results = [txn, message]
      console.log('results: %j', results);
  });

  // identifies if there are any transactions to be signed by the DAO 
  var arrayLength = results.length;
  for (var i = 0; i < arrayLength; i++) {
    if (results[i][2] == dao_address) {
      // TODO: Create a function to sign the transaction, maybe a python binary?

    }
  }
    
  // requestParams should be an array of WalletTransaction objects, one for each transaction
  // a WalletTransaction object has two fields, txn: string and message?: string
  const requestParams = [results];

  const request = formatJsonRpcRequest("algo_signTxn", requestParams);
  const result = await this.connector.sendCustomRequest(request);
  const decodedResult = result.map(element => {
    return element ? new Uint8Array(Buffer.from(element, "base64")) : null;
  });

  console.log('decodedResult: %j', decodedResult)

  // TODO: python function to submit transaction
}
*/


