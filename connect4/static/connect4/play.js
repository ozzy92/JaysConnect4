
// called at page load to setup game
function play_game(game_pk) {    
    console.log('Playgame ' + game_pk + ' running.');
    $(document).ready(function() {        
        // connect to websocket
        var socket = connect_socket('play/' + game_pk);

        // wire up play buttons
        for(let c = 1; c <= board_columns; c ++) {
            $('#placetoken' + c).on('click', function(event) {
                console.log('Sending move in column ' + c);
                socket.send(JSON.stringify({ 'play' : c }));
            })
        }

        // wire up receive message
        socket.onmessage = function(message) {
            var data = JSON.parse(message.data);

            console.log('Received message: ' + data);
            $('#data').append('<div>Got Data: ' + data + '</div>');
        };
    });
}
