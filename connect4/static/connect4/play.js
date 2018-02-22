
var game_pk;
var prompt_leave;

// loads the board
function get_board() {
    http_get('/connect4/rester/game_board/' + game_pk + '/').then((data) => {
        console.log('Reloading board ' + game_pk);
        $('#board').html(data);
    });
}

// sends a joingame request
function join_game() {
    console.log('Joining join ' + game_pk);
    http_get('/connect4/rester/join_game/' + game_pk + '/', (data) => {
        console.log('Join result ' + data);
        if(data) {
            prompt_leave = true;
        }
    });
}

// make a move in the game
function make_move(column) {
    console.log('Making move in column ' + column);
    http_get('/connect4/rester/make_move/' + game_pk + '/' + column + '/', (data) => {
        console.log('Move result ' + data);
    });
}

// called at page load to setup game
function play_game() {    
    console.log('Playgame ' + game_pk + ' running.');

    $(document).ready(() => {
        // reload the board
        get_board();

        // hook leave prompt
        $(window).bind('beforeunload', function(){
            if(prompt_leave) {
                // prompt is not guaranteed
                // https://stackoverflow.com/questions/7080269/javascript-before-leaving-the-page
                return 'Leave the game?';
            }
        });

        // connect to websocket
        var socket = connect_socket('play/' + game_pk + '/');

        // wire up receive message
        socket.onmessage = function(message) {
            var data = JSON.parse(message.data);

            console.log('Received message: ' + data);
            if(data.type == 'play.update') {
                get_board();
            }
        };
    });
}
