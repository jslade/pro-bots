import React, { useContext, useCallback } from 'react';

import { List, ListItem } from '@mui/material';

import {GameContext} from '../../contexts/GameContext';

const Scoreboard = () => {
    const { gameState } = useContext(GameContext);

    const sortedPlayersList = useCallback(() => {
        if (!gameState?.players) return [];

        const players = gameState?.players.map(player => player);
        return players.sort((a, b) => a.score - b.score);

    }, [gameState])

    const playerItem = (player) => {
        return (
            <ListItem key={player.name}>
                {player.score} - {player.name}
            </ListItem>
        )
    };

    return (
        <List>
            {sortedPlayersList().map((player) => playerItem(player))}
        </List>
    );
};


export default Scoreboard;