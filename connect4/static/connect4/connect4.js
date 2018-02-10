
const board_rows = 6;
const board_columns = 7

function connect_socket(url) {
    console.log('Connecting to socket ' + url);

    var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
    var chat_socket = new ReconnectingWebSocket(ws_scheme + '://' + window.location.host + "/connect4ws/" + url);
    return chat_socket
}

// helper to turn setTimeout into a Promise
var wait = ms => new Promise(resolve => setTimeout(resolve, ms));

function polling_http(url, interval, callback) {
    // since I can't get websocket working, we will simulate it!
    // url - relative url to json ajax page
    // interval - poll interval in milliseconds
    // callback - function to be called with decoded json payload
    let get = () => {
        $.get(url, (data) => {
            callback(data);
            wait(interval).then(() => { get(); });
        });
    };
    get();
}
