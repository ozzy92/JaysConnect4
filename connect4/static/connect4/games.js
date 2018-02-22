
function get_games_list(list) {
    http_get('/connect4/' + list).then((data) => {
        console.log('Replacing ' + list);
        $('#' + list).replaceWith(data);
    });
}

function create_game() {
    console.log('Creating game')
    http_get('/connect4/rester/create_game').then((data) => {
        console.log('Created game: ' + data)
        if('game_id' in data) {
            window.location = '/connect4/play/' + data.game_id;
        }
    });
}

$(document).ready(() => {
    var socket = connect_socket('games/');
    
    socket.onmessage = (message) => {
        var data = JSON.parse(message.data);

        console.log('Got games socket: ' + data);
        if('list' in data) {
            var list = data['list'];

            get_games_list(list);        
        }
    };

    get_games_list('available_games');
    get_games_list('running_games');
    get_games_list('user_games');
});
