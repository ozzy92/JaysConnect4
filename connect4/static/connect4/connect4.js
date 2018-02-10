
const board_rows = 6;
const board_columns = 7

function connect_socket(url) {
    console.log('Connecting to socket ' + url);

    var chat_socket = new ReconnectingWebSocket('ws://' + window.location.host + "/connect4/" + url);
    return chat_socket
}
