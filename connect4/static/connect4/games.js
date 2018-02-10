
function games_list_update(games, list) {
    console.log('Replacing ' + list);
    $('#' + list).html(games);
}

function create_game() {
    console.log('Creating game')
    $.get('/connect4/rester/create_game', {}, (data) => {
        console.log('Created game: ' + data)
        if('game_id' in data) {
            window.location = '/connect4/play/' + data.game_id;
        }
    });
}

$(document).ready(() => {
    let updaters = (url, list) => {
        polling_http(url, 5000, (data) => {
            games_list_update(data, list);
        });
    }
    updaters('/connect4/available_games', 'available_games');
    updaters('/connect4/running_games', 'running_games');
    updaters('/connect4/user_games', 'user_games');
});
