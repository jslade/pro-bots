import React, { useCallback, useContext, useEffect } from 'react';

import { ApiContext } from '../ApiContext';

const PlayerUpdater = ({ players, setPlayersUpdated }) => {
    const api = useContext(ApiContext);

    const handleUpdatePlayer = useCallback((update) => {
        if (!players) return;

        for (const player of players) {
            if (player.name === update.name) {
                Object.assign(player, update)
                break;
            }
        }

        setPlayersUpdated(Date.now());
    }, [players, setPlayersUpdated]);

    useEffect(() => {
        if (!api) return;

        api.registerCallback('game', 'update_player', handleUpdatePlayer);

        return () => {
            api?.unregisterCallback('game', 'update_player');
        }
    }, [api, api?.registerCallback, handleUpdatePlayer, players]);



    return ( <></> );
};

export { PlayerUpdater };