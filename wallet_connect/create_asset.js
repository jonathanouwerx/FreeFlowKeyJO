let {PythonShell} = require('python-shell')

var options = {
    scriptPath: 'wallet_connect/basic_transactions/',
    mode: 'text',
    args: []
};

PythonShell.run('asset_creation.py', options, function (err, results) {
    if (err) throw err;
    // results is an array consisting of messages collected during execution
    // results = [txn, message]
    console.log('results: %j', results);
});


