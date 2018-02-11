
var game_pk;

// reload board html with polling query
function load_board() {
    polling_http('/connect4/rester/game_board/' + game_pk + '/', 2000, (data) => {
        console.log('Reloading board ' + game_pk);
        $('#board').html(data);
    });
}

// sends a joingame request
function join_game() {
    console.log('Joining join ' + game_pk);
    $.get('/connect4/rester/join_game/' + game_pk + '/', {}, (data) => {
        console.log('Join result ' + data);
    });
}

// make a move in the game
function make_move(column) {
    console.log('Making move in column ' + column);
    $.get('/connect4/rester/make_move/' + game_pk + '/' + column + '/', {}, (data) => {
        console.log('Move result ' + data);
    });
}

// called at page load to setup game
function play_game() {    
    console.log('Playgame ' + game_pk + ' running.');
    $(document).ready(() => {        
        load_board();
    });
    /** sockets would be so much cleaner
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
    **/
}
