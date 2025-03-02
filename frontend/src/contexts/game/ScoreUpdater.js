import React, { useCallback, useContext, useEffect } from 'react';

import { ApiContext } from '../ApiContext';

const ScoreUpdater = ({ players, setScoresUpdated }) => {
    const api = useContext(ApiContext);

    const handleUpdateScore = useCallback(({ playerName, newScore }) => {
        if (!players) return;

        // Update the score of the specific player
        for (const player of players) {
            if (player.name === playerName) {
                player.score = newScore;
                break;
            }
        }

        // re-sort based on new scores
        players.sort((a, b) => b.score - a.score);

        setScoresUpdated(Date.now());
    }, [players, setScoresUpdated]);

    useEffect(() => {
        if (!api) return;

        api.registerCallback('game', 'update_score', (data) => {
            handleUpdateScore(data);
        });

        return () => {
            api?.unregisterCallback('game', 'update_score');
        }
    }, [api, api?.registerCallback, handleUpdateScore, players]);



    return ( <></> );
};

export { ScoreUpdater };